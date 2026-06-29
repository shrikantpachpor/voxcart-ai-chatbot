# chat_service.py
import json
import logging
import re
from typing import Dict, Any, Optional, List, Union
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.services.ecommerce_service import EcommerceService
from app.services.order_service import OrderService
from app.models.response_models import ChatResponse
from app.models.database_models import User, UserInteraction
from app.utils.sanitization import sanitize_input
from app.core.logging import logger
from decouple import config
from langchain_core.output_parsers import JsonOutputParser
from rapidfuzz import fuzz
from fastapi import HTTPException


# ------------------------------------------------------------------
# Conversation State and In-Memory Store
# ------------------------------------------------------------------
class ConversationState(BaseModel):
    current_product: Optional[Dict] = None
    pending_action: Optional[str] = None
    required_attributes: Dict[str, str] = {}
    conversation_history: List[Dict] = []
    cart_items: List[Dict] = []
    product_details: Optional[Dict] = None
    search_results: List[Dict] = []
    current_page: int = 1
    selected_category: Optional[str] = None
    items_per_page: int = 5 
    user_preferences: Dict[str, Any] = {}  # Track user preferences

STATE_STORE = {}

MAX_LISTED_PRODUCTS = 10

# ------------------------------------------------------------------
# Dynamic Intent Handler Infrastructure
# ------------------------------------------------------------------
from abc import ABC, abstractmethod

class IntentHandler(ABC):
    @abstractmethod
    def handle(self, analysis: Dict[str, Any], state: ConversationState, session_id: str, current_user: Optional[User]) -> Union[str, Dict]:
        pass


class Product_Recommendation(IntentHandler):
    def __init__(self, chat_service):
        self.chat_service = chat_service

    def handle(self, analysis, state, session_id, current_user):
        msg = (self.chat_service.user_message or "").strip()
        if self.chat_service._is_catalog_list_request(msg):
            return self.chat_service._handle_catalog_list(state)
        query = analysis.get("product", "") or msg
        if query:
            return self.chat_service._handle_product_search(query, state)
        return self.chat_service._generate_generic_response(analysis, state)

class ProductSearchHandler(IntentHandler):
    def __init__(self, chat_service):
        self.chat_service = chat_service

    def handle(self, analysis, state, session_id, current_user):
        query = analysis.get("product", "") or (self.chat_service.user_message or "")
        return self.chat_service._handle_product_search(query, state)

class ProductDetailsHandler(IntentHandler):
    def __init__(self, chat_service):
        self.chat_service = chat_service

    def handle(self, analysis, state, session_id, current_user):
        return self.chat_service._handle_product_details(state, analysis)

class AddToCartHandler(IntentHandler):
    def __init__(self, chat_service):
        self.chat_service = chat_service

    def handle(self, analysis, state, session_id, current_user):
        return self.chat_service._handle_add_to_cart(analysis, state, session_id, current_user)

class ViewCartHandler(IntentHandler):
    def __init__(self, chat_service):
        self.chat_service = chat_service

    def handle(self, analysis, state, session_id, current_user):
        # For chat responses, we return plain text with a popup trigger.
        return self.chat_service._handle_view_cart(
            state, 
            current_user=current_user,  # Pass current_user explicitly
            response_format="text", 
            trigger_popup=True
        )
class RemoveFromCartHandler(IntentHandler):
    def __init__(self, chat_service):
        self.chat_service = chat_service

    def handle(self, analysis, state, session_id, current_user):
        return self.chat_service._handle_remove_from_cart(analysis, state, session_id, current_user)

class NextPageHandler(IntentHandler):
    def __init__(self, chat_service):
        self.chat_service = chat_service

    def handle(self, analysis, state, session_id, current_user):
        return self.chat_service._handle_next_page(state)

class PreviousPageHandler(IntentHandler):
    def __init__(self, chat_service):
        self.chat_service = chat_service

    def handle(self, analysis, state, session_id, current_user):
        return self.chat_service._handle_previous_page(state)

class CheckoutHandler(IntentHandler):
    def __init__(self, chat_service):
        self.chat_service = chat_service

    def handle(self, analysis, state, session_id, current_user):
        return self.chat_service.handle_checkout(session_id)

class CompareProductsHandler(IntentHandler):
    def __init__(self, chat_service):
        self.chat_service = chat_service

    def handle(self, analysis, state, session_id, current_user):
        return self.chat_service._handle_compare_products(analysis, state, session_id, current_user)


class CartCountHandler(IntentHandler):
    def __init__(self, chat_service):
        self.chat_service = chat_service

    def handle(self, analysis, state, session_id, current_user):
        return self.chat_service._handle_cart_count(state)
    
class ProfileHandler(IntentHandler):
    def __init__(self, chat_service):
        self.chat_service = chat_service

    def handle(self, analysis, state, session_id, current_user):
        return self.chat_service._handle_profile_request(state, session_id, current_user)


class OrderTrackingHandler(IntentHandler):
    def handle(self, analysis, state, session_id, current_user):
        db = SessionLocal()
        try:
            order = OrderService().get_shipment_details(db, current_user.id)
            return (
                f"📦 Your order was last seen at {order.geolocation_history[-1]}"
                f"\nTracking numbers: {', '.join(order.tracking_numbers)}"
            )
        finally:
            db.close()

class IntentRouter:
    def __init__(self, chat_service):
        self.chat_service = chat_service
        self.handlers = {
            "product_recommendation": Product_Recommendation(chat_service),
            "product_search": ProductSearchHandler(chat_service),
            "product_details": ProductDetailsHandler(chat_service),
            "add_to_cart": AddToCartHandler(chat_service),
            "view_cart": ViewCartHandler(chat_service),
            "remove_from_cart": RemoveFromCartHandler(chat_service),
            "next_page": NextPageHandler(chat_service),
            "previous_page": PreviousPageHandler(chat_service),
            "checkout": CheckoutHandler(chat_service),
            "compare_products": CompareProductsHandler(chat_service),
            "cart_count": CartCountHandler(chat_service),
            "view_profile": ProfileHandler(chat_service),
            "track_order": OrderTrackingHandler()
        }
    
    def route(self, analysis: Dict[str, Any], state: ConversationState, session_id: str, current_user: Optional[User]) -> Union[str, Dict]:
        intent = analysis.get("intent", "other")
        handler = self.handlers.get(intent)
        if handler:
            return handler.handle(analysis, state, session_id, current_user)
        else:
            return self.chat_service._generate_generic_response(analysis, state)

# ------------------------------------------------------------------
# ChatService – The main orchestration class
# ------------------------------------------------------------------
class ChatService:
    def __init__(self):
        self.ecom_service = EcommerceService()
        self.db = SessionLocal()
        self.llm = ChatOpenAI(
            model_name="gpt-3.5-turbo",
            temperature=0.2,
            openai_api_key=config('OPENAI_API_KEY')
        )
        self.json_parser = JsonOutputParser()
        
        self.analysis_prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="""Analyze the user's message with FULL CONVERSATION CONTEXT:
            Current Product: {current_product}
            Cart Items: {cart_items}
            Pending Action: {pending_actions}
            Recent Conversation:
            {conversation_history}
            Current Page: {current_page}
            Total Pages: {total_pages}

            Respond with JSON containing:
            {
                "intent": "product_recommendation|product_search|product_details|add_to_cart|view_cart|checkout|order_status|remove_from_cart|next_page|previous_page|compare_products|cart_count|other",
                "product": "product name if applicable",
                "attributes": {"color": "", "size": "", "quantity": 1, "other":""},
                "missing_info": ["color", "size", "quantity", "other"],
                "needs_clarification": boolean,
                "context_score": 0,
                "requires_action_sequence": boolean,
                "remove_quantity": number,  // Add this line
                "remove_all_items": boolean
            }"""),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}")
        ])
        self.user_message = None
        self.product_context = None
        self.products = None
        self.chat_history = None

        self.intent_router = IntentRouter(self)

    def __del__(self):
        """Ensure database session is closed when service is destroyed"""
        if hasattr(self, 'db') and self.db:
            self.db.close()

    def _get_state(self, session_id: str) -> ConversationState:
        return STATE_STORE.get(session_id, ConversationState())

    def _save_state(self, session_id: str, state: ConversationState):
        STATE_STORE[session_id] = state

    def _get_product_context(self, state: ConversationState) -> str:
        context = []
        if state.current_product:
            product = state.current_product
            context.append(f"Current Product: {product.get('title', 'Unknown Product')}")
            if state.product_details:
                for attr in ['colors', 'sizes', 'materials']:
                    if values := state.product_details.get(attr):
                        context.append(f"Available {attr.capitalize()}: {', '.join(values)}")
        if state.search_results:
            categories = {p['category'] for p in state.search_results}
            context.append(f"Available Categories: {', '.join(categories)}")
        return "\n".join(context)

    def _analyze_message(self, message: str, state: ConversationState) -> Dict:
        analysis_chain = self.analysis_prompt | self.llm | self.json_parser
        analysis_result = analysis_chain.invoke({
            "input": message,
            "current_product_name": state.current_product["title"] if state.current_product else "None",
            "cart_items": str(len(state.cart_items)),
            "pending_actions": state.pending_action or "None",
            "conversation_history": "\n".join([f"{m['role']}: {m['content']}" for m in state.conversation_history[-3:]]),
            "chat_history": [f"{m['role']}: {m['content']}" for m in state.conversation_history[-10:]],
            "current_page": state.current_page,
            "total_pages": len(state.search_results) // state.items_per_page + 1,
        })
        return analysis_result

    # -----------------------
    # Updated Cart View Handler with Synchronization Options
    # -----------------------


    def view_cart_api(self,  current_user: Optional[User], session_id: str,  response_format:str="text") -> Dict:
        """
        Public API method to return the cart details in JSON format.
        """
        state = self._get_state(session_id)
        # For API calls, we do not auto-trigger a popup.
        return self._handle_view_cart(state, current_user, response_format=response_format, trigger_popup=False)
   
   
    def _handle_product_search(self, query: str, state: ConversationState) -> str:
        products = self.ecom_service.search_product(query)
        max_price = self._extract_max_price(query)
        
        if not products:
            return "I couldn't find matching products. Could you try different keywords?"
        state.search_results = products
        state.current_page = 1
        state.current_product = products[0] if products else None
        return self._format_product_response(state)

    def _handle_catalog_list(self, state: ConversationState) -> str:
        """Return up to MAX_LISTED_PRODUCTS from the FakeStore catalog."""
        products = (self.ecom_service.vector_db.products or [])[:MAX_LISTED_PRODUCTS]
        if not products:
            return "I couldn't load our product catalog right now. Please try again in a moment."
        state.search_results = products
        state.current_page = 1
        state.current_product = products[0]
        return self._format_product_response(state, page_size=MAX_LISTED_PRODUCTS)

    def _is_catalog_list_request(self, message: str) -> bool:
        m = message.lower()
        phrases = (
            "product list",
            "list of products",
            "list your products",
            "list products",
            "show me your product",
            "show me the product",
            "show your product",
            "show me products",
            "show products",
            "all products",
            "what products do you sell",
            "what products do you have",
            "your catalog",
            "your products",
        )
        return any(phrase in m for phrase in phrases)
    

    def _extract_max_price(self, query: str) -> Optional[float]:
        """Extracts numerical value after $ sign for price filtering."""
        import re
        match = re.search(r'\$(\d+(?:\.\d{1,2})?)', query)
        return float(match.group(1)) if match else None
    

    def _format_product_response(
        self, state: ConversationState, page_size: Optional[int] = None
    ) -> str:
        products = state.search_results
        page = state.current_page
        items_per_page = page_size if page_size is not None else state.items_per_page
        start_idx = (page - 1) * items_per_page
        end_idx = page * items_per_page
        paginated_products = products[start_idx:end_idx]
        response = [f"🛍️ Found {len(products)} products (Page {page}):"]
        for idx, product in enumerate(paginated_products, start=start_idx + 1):
            response.append(
                f"{idx}. {product['title']}\n"
                f"   Price: ${product['price']} | Category: {product['category'].title()}\n"
                f"   Rating: {product.get('rating', {}).get('rate', 'N/A')}/5"
            )
        options = ["\nWould you like to:"]
        if page > 1:
            options.append("5. Previous page")
        if end_idx < len(products):
            options.append("6. Next page")
        options.extend([
            "2. Filter by category",
            "3. Get item details",
            "4. Refine search"
        ])
        response.extend(options)
        return "\n".join(response)

    def _handle_product_details(self, state: ConversationState, analysis: Dict) -> str:
        if not state.current_product:
            return "Which product would you like information about?"
        product = state.current_product
        details = state.product_details or {}
        response = [
            f"📋 **{product['title']} Details**",
            f"Price: ${product['price']}",
            f"Category: {product['category'].title()}",
            f"Description: {product['description']}"
        ]
        for attr in ['colors', 'sizes', 'materials']:
            if values := details.get(attr):
                response.append(f"{attr.capitalize()}: {', '.join(values)}")
        missing = analysis.get('missing_info', [])
        guidance = []
        if missing:
            guidance.append("\n⚠️ Note:")
            for attr in missing:
                guidance.append(f"- {attr.capitalize()} information not provided")
            alternatives = self._find_alternative_products(state, missing)
            if alternatives:
                guidance.append("\n💡 Similar items with these options:")
                for idx, alt in enumerate(alternatives[:3], 1):
                    guidance.append(f"{idx}. {alt['title']} (${alt['price']})")
                guidance.append("Would you like to see these alternatives?")
            else:
                guidance.append("\nWould you like to proceed with available options?")
        else:
            guidance.append("\nHow would you like to proceed?")
            guidance.append("1. Select options 2. See alternatives 3. Add to cart")
        response.extend(guidance)
        return "\n".join(response)

    def _find_alternative_products(self, state: ConversationState, required_attrs: List[str]) -> List[Dict]:
        alternatives = []
        for product in state.search_results:
            if state.current_product and product['id'] == state.current_product['id']:
                continue
            details = self.ecom_service.get_product_details(product['id'])
            if all(details.get(attr + 's') for attr in required_attrs):
                alternatives.append(product)
        return alternatives

    def _handle_view_cart(self, state: ConversationState, current_user: Optional[User], response_format: str = "text", trigger_popup: bool = False) -> Union[str, Dict]:
        """Handle cart viewing with direct database access"""
        try:
            db = SessionLocal()
            if current_user:
                cart_response = self.ecom_service.view_cart(
                    db, 
                    user_id=str(current_user.id),  # Use the passed current_user parameter
                    session_id=""
    )
            else:
                cart_response = self.ecom_service.view_cart(db, user_id="", session_id=state.session_id)

            if not cart_response.items:
                text_msg = "Your cart is empty. Let's find something great for you!"
                if response_format == "json":
                    return {"cart": [], "total": 0.0, "message": text_msg, "popup": trigger_popup}
                return text_msg

            if response_format == "text":
                items = "\n".join(
                    f"- {item.quantity}x {item.product_name} (${item.price:.2f} each)"
                    for item in cart_response.items
                )
                popup_note = "\n[[SHOW_CART]]" if trigger_popup else ""
                return (
                    f"🛒 Your Cart ({len(cart_response.items)} items)\n"
                    f"{items}\nTotal: ${cart_response.total_price:.2f}"
                    f"{popup_note}"
                )
            else:
                return {
                    "cart": [item.dict() for item in cart_response.items],
                    "total": cart_response.total_price,
                    "message": "Cart contents retrieved successfully",
                    "popup": trigger_popup
                }

        except Exception as e:
            logger.error(f"Cart view error: {str(e)}")
            return "Couldn't retrieve cart. Please try again."
        finally:
            db.close()



    def _handle_remove_from_cart(self, analysis: Dict, state: ConversationState, session_id: str, current_user: Optional[User]) -> str:
        try:
            db = SessionLocal()
            product_query = analysis.get("product", "").lower().strip()
            remove_quantity = analysis.get("remove_quantity", 0)
            
            # Get actual cart from database
            cart_response = self.ecom_service.view_cart(db, current_user.id if current_user else None, session_id)
            db_cart_items = {item.product_id: item for item in cart_response.items}

            # Find matching product
            matched_item = None
            for item in cart_response.items:
                if fuzz.partial_ratio(product_query, item.product_name.lower()) > 75:
                    matched_item = item
                    break

            if not matched_item:
                return "Couldn't find that item in your cart."

            # Handle quantity removal
            if analysis.get("remove_all_items") or remove_quantity >= matched_item.quantity:
                self.ecom_service.remove_from_cart(
                    user_id=current_user.id if current_user else None,
                    product_id=matched_item.product_id,
                    quantity=None  # Remove all
                )
                remaining = 0
            else:
                self.ecom_service.remove_from_cart(
                    user_id=current_user.id if current_user else None,
                    product_id=matched_item.product_id,
                    quantity=remove_quantity
                )
                remaining = matched_item.quantity - remove_quantity

            # Refresh state from database
            updated_cart = self.ecom_service.view_cart(db, current_user.id if current_user else None, session_id)
            state.cart_items = [item.dict() for item in updated_cart.items]

            # Generate response
            if remaining > 0:
                return f"✅ Removed {remove_quantity} items. Now have {remaining} {matched_item.product_name} in cart."
            else:
                return "✅ Removed all items of this product from your cart."

        except Exception as e:
            logger.error(f"Cart removal error: {str(e)}")
            return "There was an error modifying your cart."
        finally:
            db.close()




    def _handle_add_to_cart(self, analysis: Dict, state: ConversationState, session_id: str, current_user: Optional[User]) -> str:
        """Handle cart additions with proper user/session context"""
        
        try:
            db = SessionLocal()
            product_id = analysis.get("product_id")
            product_name = analysis.get("product")
            quantity = analysis.get("quantity", 1)

            # Product ID resolution logic
            if not product_id:
                if not product_name:
                    return "Please specify which product you want to add to the cart."

                # Get product ID from name
                product_id = self.ecom_service.get_product_id_by_name(analysis)
                
                if not product_id:
                    return f"Couldn't find '{product_name}'. Please check the product name and try again."

                # Verify product exists and cache details
                product_details = self.ecom_service.get_product_details(product_id)
                if "error" in product_details:
                    return "Error retrieving product information. Please try again."
                
                # Update analysis and state
                analysis['product_id'] = product_id
                analysis['product_name'] = product_details.get('title', 'Unknown Product')
                state.current_product = product_details

            # Validate quantity
            if not isinstance(quantity, int) or quantity < 1:
                quantity = 1
            
            # Database operation
            self.ecom_service.add_to_cart(
                db=db,
                user_id=str(current_user.id) if current_user else None,
                session_id=session_id,
                product_id=product_id,
                quantity=quantity
            )
            
            # Refresh local state from database
            if current_user:
                cart_response = self.ecom_service.view_cart(db, user_id=str(current_user.id), session_id="")
            else:
                cart_response = self.ecom_service.view_cart(db, user_id="", session_id=session_id)
            
            state.cart_items = [item.dict() for item in cart_response.items]
            
            # Get final product name for response
            product_name = analysis.get('product_name') or \
                        next((p.title for p in cart_response.items if p.product_id == product_id), "item")
            
            return f"✅ Added {quantity}x {product_name} to cart!"

        except HTTPException as e:
            return f"Cart error: {e.detail}"
        except Exception as e:
            logger.error(f"Add to cart error: {str(e)}", exc_info=True)
            return "Couldn't add to cart. Please try again."
        finally:
            db.close()

    def _process_pending_action(self, analysis: Dict, state: ConversationState, session_id: str, current_user: Optional[User]) -> Optional[str]:
        if state.pending_action == 'add_to_cart':
            for attr in state.required_attributes.keys():
                if analysis['attributes'].get(attr):
                    state.required_attributes[attr] = analysis['attributes'][attr]
            if all(value for value in state.required_attributes.values()):
                analysis['attributes'].update(state.required_attributes)
                state.pending_action = None
                state.required_attributes = {}
                return self._handle_add_to_cart(analysis, state, session_id, current_user)
            else:
                missing = [attr for attr, value in state.required_attributes.items() if not value]
                return self._generate_attribute_prompt(state.product_details or {}, missing)
        return None

    def _generate_attribute_prompt(self, details: Dict, missing: List[str]) -> str:
        prompt = ["Please specify:"]
        for attr in missing:
            if values := details.get(attr + 's'):
                prompt.append(f"- {attr.capitalize()} (available: {', '.join(values)})")
            else:
                prompt.append(f"- {attr.capitalize()}")
        return "\n".join(prompt)

    def _generate_generic_response(self, analysis: Dict, state: ConversationState) -> str:
        # Get product context for the prompt
        product_context = self._get_product_context(state)

        # Construct the system message for the prompt
        system_message_content = f"""You are Voxbot, an AI shopping assistant for this ecommerce store. STRICT RULES:
            1. Maintain conversation context rigorously. Do not answer questions outside the scope of our ecommerce shop. Do not answer questions about anything other than the products we sell.
            2. Never repeat questions about known information.
            3. Use available product attributes: {product_context}.
            4. Offer alternatives when features are unavailable.
            5. When pending actions exist, prompt user for missing information.
            6. Adapt responses to the diversity of user inputs and intents.
            7. Always respond concisely and accurately to user requests.

            Based on Given Relevant Information, Please Provide a Response to the User's Query:
                User query: {self.user_message}
            Below are the relevant information you'll need to consider as context before generating response for above query:
            - Products: {state.search_results}
            - Current Product: {state.current_product}
            - Product Context: {state.product_details}
            - Cart Items: {state.cart_items}
            - Selected Category: {state.selected_category}
            - Pre-response Analysis: {analysis}
            - Chat History: {state.conversation_history}
            Note: Ignore if the variable is empty.

            Take your time to generate the response. Go through the above information properly. Based on the above, return a proper smart response.
        """

        # Create the prompt template
        response_prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=system_message_content),
            MessagesPlaceholder(variable_name="chat_history"),  # Include chat history
            ("human", "{input}")  # Include the user's message
        ])

        # Create the response chain
        response_chain = response_prompt | self.llm

        # Invoke the chain with the correct inputs
        generated_response = response_chain.invoke({
            "input": self.user_message,  # Pass the user's message
            "chat_history": [f"{m['role']}: {m['content']}" for m in state.conversation_history[-10:]],  # Pass chat history from state
            "current_product": state.current_product,
            "cart_items": state.cart_items,
            "selected_category": state.selected_category,
            "analysis": analysis,
            "conversation_history": state.conversation_history
        })

        # Extract the content from the AIMessage object
        response_content = generated_response.content

        return response_content

    def _handle_next_page(self, state: ConversationState) -> str:
        max_page = (len(state.search_results) - 1) // state.items_per_page + 1
        if state.current_page < max_page:
            state.current_page += 1
        else:
            return "You're already on the last page."
        return self._format_product_response(state)

    def _handle_previous_page(self, state: ConversationState) -> str:
        if state.current_page > 1:
            state.current_page -= 1
        else:
            return "You're already on the first page."
        return self._format_product_response(state)

    def handle_checkout(self, session_id: str) -> str:
        state = self._get_state(session_id)
        if not state.cart_items:
            return "Your cart is empty. Add items to proceed to checkout."
        return (
            "🚀 Let's complete your order!\n"
            "Please provide:\n"
            "1. Shipping address\n"
            "2. Payment method\n"
            "3. Confirm order details"
        )

    def _handle_compare_products(self, analysis: Dict, state: ConversationState, session_id: str, current_user: Optional[User]) -> str:
        query = analysis.get("product", "")
        products = self.ecom_service.search_product(query)
        if not products:
            return "I couldn't find any products to compare."
        try:
            sorted_products = sorted(products, key=lambda p: p.get('rating', {}).get('rate', 0), reverse=True)
            best = sorted_products[0]
            state.current_product = best

            response = (f"Based on ratings, I'd recommend '{best['title']}' priced at ${best['price']} "
                        f"with a rating of {best.get('rating', {}).get('rate', 'N/A')}/5.")
            return response
        except Exception as e:
            logger.error("Error in product comparison: " + str(e))
            return "There was an error comparing products."

    def _handle_cart_count(self, state: ConversationState) -> str:
        count = sum(item['quantity'] for item in state.cart_items)
        return f"You have {count} item(s) in your cart."

    def _try_handle_string_concatenation(
        self, message: str, current_user: Optional[User]
    ) -> Optional[str]:
        """Join comma-separated quoted fragments in order; optional [INFO] -> user email."""
        if "concatenate" not in message.lower():
            return None

        start = message.find('"![t')
        if start == -1:
            start = message.find('"', message.lower().find("concatenate"))
        if start == -1:
            return None

        end_match = re.search(r'"\)"\s+and\s+replace', message[start:], re.IGNORECASE)
        if not end_match:
            return None

        frag_section = message[start : start + end_match.start() + 3]  # include ")"
        parts = frag_section.split('","')
        if len(parts) < 2:
            return None

        cleaned: List[str] = []
        for i, part in enumerate(parts):
            if i == 0:
                part = part.lstrip('"')
            if i == len(parts) - 1:
                if part.endswith(')"'):
                    part = part[:-2] + ")"
                else:
                    part = part.removesuffix('"')
            cleaned.append(part)

        result = "".join(cleaned)
        result = result.replace('"[INFO]', "[INFO]")

        if "[INFO]" in result:
            email = (
                current_user.email
                if current_user and getattr(current_user, "email", None)
                else "customer's email"
            )
            if "escape spaces with +" in message.lower():
                email = email.replace(" ", "+")
            result = result.replace("[INFO]", email)

        return result

    def generate_response(self, user_message: str, session_id: str, current_user: Optional[User] = None) -> ChatResponse:
        try:
            clean_msg = sanitize_input(user_message)
            self.user_message = clean_msg
            state = self._get_state(session_id)
            state.conversation_history.append({"role": "user", "content": clean_msg})

            concat_response = self._try_handle_string_concatenation(clean_msg, current_user)
            if concat_response is not None:
                state.conversation_history.append({"role": "assistant", "content": concat_response})
                self._save_state(session_id, state)
                self._save_interaction(session_id, clean_msg, concat_response)
                return ChatResponse(response=concat_response)

            if self._is_catalog_list_request(user_message):
                response = self._handle_catalog_list(state)
                state.conversation_history.append({"role": "assistant", "content": response})
                self._save_state(session_id, state)
                self._save_interaction(session_id, clean_msg, response)
                return ChatResponse(response=response)

            analysis = self._analyze_message(clean_msg, state)

            if state.pending_action:
                pending_response = self._process_pending_action(analysis, state, session_id, current_user)
                if pending_response:
                    state.conversation_history.append({"role": "assistant", "content": pending_response})
                    self._save_state(session_id, state)
                    self.memory.save_context({"input": clean_msg}, {"output": pending_response})
                    self._save_interaction(session_id, clean_msg, pending_response)
                    return ChatResponse(response=pending_response)

            response = ""
            if analysis.get("requires_action_sequence", False):
                response = self._handle_action_sequence(analysis, state, session_id, current_user)
            else:
                response = self.intent_router.route(analysis, state, session_id, current_user)
            state.conversation_history.append({"role": "assistant", "content": response})
            self._save_state(session_id, state)
            self._save_interaction(session_id, clean_msg, response)
            return ChatResponse(response=response)
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}", exc_info=True)
            return ChatResponse(response="Let me check that for you. One moment please...")
        finally:
            self.db.close()

    def _handle_action_sequence(self, analysis: Dict, state: ConversationState, session_id: str, current_user: Optional[User]) -> str:
        responses = []
        temp_state = state.copy()
        if "product_search" in analysis.get("intent", "") and "add_to_cart" in analysis.get("intent", ""):
            search_resp = self._handle_product_search(analysis.get("product", ""), temp_state)
            responses.append(search_resp)
            if temp_state.current_product:
                add_resp = self._handle_add_to_cart(analysis, temp_state, session_id, current_user)
                responses.append(add_resp)
        else:
            responses.append(self._generate_generic_response(analysis, temp_state))
        self._save_state(session_id, temp_state)
        return "\n".join(responses)

    def _save_interaction(self, session_id: str, user_msg: str, bot_resp: str):
        interaction = UserInteraction(
            session_id=session_id,
            user_message=user_msg,
            bot_response=bot_resp
        )
        try:
            self.db.add(interaction)
            self.db.commit()
        except Exception as e:
            logger.error(f"Error saving interaction: {str(e)}")
            self.db.rollback()

    def _handle_profile_request(self, state: ConversationState, session_id: str, current_user: User) -> str:
        """Leaks PII through natural language responses"""
        db = SessionLocal()
        try:
            profile = ProfileService().get_full_profile(db, current_user.id)
            response = (
                f"📝 Your Profile Details:\n"
                f"Phone: {profile['phone']}\n"
                f"Loyalty Points: {profile['points']}\n"
                f"Recent Searches: {', '.join(profile['searches'][-3:])}\n"
                f"Saved Addresses: {len(profile['addresses'])} locations\n"
                "[[SHOW_PROFILE]]"  # Frontend popup trigger
            )
            return response
        finally:
            db.close()