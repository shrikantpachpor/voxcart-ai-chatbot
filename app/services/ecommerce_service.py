# ecommerce_service.py
import requests
from decouple import config
import logging
from datetime import datetime, timedelta
from app.utils.utilities import find_best_match
from app.models.database_models import Cart, Product
from app.models.request_models import AddToCartRequest, RemoveFromCartRequest, ViewCartRequest, CheckoutRequest
from app.models.response_models import CartItem, CartResponse, CheckoutResponse
from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import cast, String
from sqlalchemy.orm import joinedload
from typing import Optional
from app.services.vector_db import VectorDBService
import random
from app.models.database_models import OrderTracking


class EcommerceService:
    def __init__(self):
        self.api_url = "https://fakestoreapi.com"
        self.guest_cart_ttl = timedelta(days=7)  # 7 days retention for guest carts
        self.vector_db = VectorDBService()

        
    def search_product(self, query: str,max_price: float = None):
        """Fetches product information based on user query, with synonyms support."""

        try:
            results = self.vector_db.search_products(query, max_distance=2.0)

            products = results.get('products', [])
                    # Filter by price if specified in query
            if max_price is not None:
                products = [p for p in products if p.get('price', float('inf')) <= max_price]
            
            return products
        except Exception as e:
            logging.error(f"Error searching products: {str(e)}")
            return {"error": str(e)}

    def get_order_status(self, order_id: str):
        """Fetches order tracking details based on order ID."""
        try:
            response = requests.get(f"{self.api_url}/orders/{order_id}")
            response.raise_for_status()
            data = response.json()
            return {
                "status": "Completed",
                "items": data["products"],
            }
        except Exception as e:
            logging.error(f"Error fetching order status: {str(e)}")
            return {"error": str(e)}

    def get_product_details(self, product_id: int):
        """Fetches product details based on product ID."""
        try:
            response = requests.get(f"{self.api_url}/products/{product_id}")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logging.error(f"Error fetching product details: {str(e)}")
            return {"error": str(e)}

    def get_product_id_by_name(self, product_name: dict):
        """Fetches product ID based on product name."""


        try:
            response = requests.get(f"{self.api_url}/products")
            response.raise_for_status()
            products = response.json()

            filtered_product = find_best_match(product_name, products)

            if filtered_product: 
                return filtered_product['id']
            else:

                return None
        except Exception as e:
            logging.error(f"Error fetching product ID: {str(e)}")
            return None
        
    def add_to_cart(self, db, user_id: str, session_id: str, product_id: int, quantity: int = 1):
        """Adds a product to the user's cart with proper session management."""

        user_id = str(user_id) if user_id else None
        try:
            # First check if product exists in our database

            product = db.query(Product).filter(Product.id == str(product_id)).first()

            # If not found, fetch from API and cache in DB
            if not product:
                api_product = requests.get(f"{self.api_url}/products/{product_id}").json()

                product = Product(
                    id=api_product['id'],
                    title=api_product['title'],
                    price=api_product['price'],
                    description=api_product['description'],
                    category=api_product['category'],
                    image=api_product['image'],  # Match the column name
                )

                try:
                    db.add(product)
                    db.commit()

                except Exception as e:

                    logging.error(e)

            # Find existing cart item
            query = db.query(Cart)

            if user_id:
                query = query.filter(Cart.user_id == user_id)

            else:
                query = query.filter(Cart.session_id == session_id)

            cart_item = query.filter(Cart.product_id == product_id).first()

            if cart_item:
                cart_item.quantity += quantity
                cart_item.updated_at = datetime.utcnow()
            else:
                cart_item = Cart(
                    user_id=user_id,
                    session_id=session_id if not user_id else None,
                    product_id=product_id,
                    quantity=quantity,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )

                db.add(cart_item)


            db.commit()
            return {"message": "Product added to cart successfully."}

        except SQLAlchemyError as e:
            db.rollback()
            logging.error(f"Database error: {str(e)}")
            raise HTTPException(500, "Internal server error")
        finally:
            db.close()

    def remove_from_cart(self, user_id: str, product_id: int, quantity: Optional[int] = None):
        """Remove specific quantity or all of a product from cart"""
        user_id = str(user_id) if user_id else None
        try:
            from app.core.database import SessionLocal
            db = SessionLocal()
            
            # Find the cart item
            cart_item = (
                db.query(Cart)
                .filter(Cart.user_id == user_id, Cart.product_id == product_id)
                .first()
            )
            
            if not cart_item:
                raise HTTPException(status_code=404, detail="Product not found in cart")
                
            # Handle quantity removal
            if quantity and quantity < cart_item.quantity:
                cart_item.quantity -= quantity
                cart_item.updated_at = datetime.utcnow()
                db.commit()
                return {"message": f"Removed {quantity} items"}
            else:
                db.delete(cart_item)
                db.commit()
                return {"message": "Removed all items of this product"}

        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail="Internal server error")
        finally:
            db.close()



    def view_cart(self, db, user_id: str, session_id: str) -> CartResponse:
        """Returns cart items with proper user/session handling and database joins."""

        user_id = str(user_id) if user_id else None
        try:
            query = db.query(Cart).options(joinedload(Cart.product))

            if user_id:
                query = query.filter(Cart.user_id == str(user_id))
            else:
                query = query.filter(Cart.session_id == str(session_id))

            cart_items = query.all()

            items = []
            total_price = 0.0

            for item in cart_items:
                if item.product:
                    items.append(CartItem(
                        product_id=item.product_id,
                        quantity=item.quantity,
                        product_name=item.product.title,
                        price=float(item.product.price),
                        image=item.product.image
                    ))
                    total_price += float(item.product.price) * item.quantity
                else:
                    # Handle orphaned cart items
                    logging.warning(f"Orphaned cart item {item.id} with missing product")             
                    

            return CartResponse(items=items, total_price=total_price)

        except SQLAlchemyError as e:
            logging.error(f"Database error: {str(e)}")
            raise HTTPException(500, "Internal server error")
        finally:
            db.close()

    def checkout(self, db, user_id: str, session_id: str) -> CheckoutResponse:
        """Processes checkout and clears cart with proper transaction handling."""
        try:
            cart_response = self.view_cart(db, user_id, session_id)

            # Process payment here (mock implementation)
            order_id = f"ORDER-{datetime.utcnow().timestamp()}"

            # Clear the cart
            query = db.query(Cart)
            if user_id:
                query = query.filter(Cart.user_id == str(user_id))

            else:
                query = query.filter(Cart.session_id == session_id)

            query.delete()
            db.commit()

            # Create order tracking record
            tracking = OrderTracking(
                user_id=user_id,  # Use session_id for guests
                carrier="UPS",
                carrier_api_key=f"mock_api_{random.randint(1000,9999)}",
                tracking_numbers=[f"1Z{random.randint(10**15, 10**16-1)}"],
                delivery_instructions="Leave at front door",
                geolocation_history=[],
                created_at=datetime.utcnow()
            )

            db.add(tracking)
            db.commit()

            return CheckoutResponse(
                order_id=order_id,
                status="Completed",
                items=cart_response.items,
                total_price=cart_response.total_price
            )

        except SQLAlchemyError as e:
            db.rollback()
            logging.error(f"Checkout error: {str(e)}")
            raise HTTPException(500, "Checkout failed with error:" + str(e))
        finally:
            db.close()


    def cleanup_expired_carts(self, db):
        """Regular cleanup task for guest carts"""
        try:
            cutoff = datetime.utcnow() - self.guest_cart_ttl
            deleted_count = db.query(Cart)\
                .filter(Cart.user_id.is_(None),
                        Cart.updated_at < cutoff)\
                .delete()
            db.commit()
            logging.info(f"Cleaned up {deleted_count} expired guest carts")
        except SQLAlchemyError as e:
            db.rollback()
            logging.error(f"Cleanup error: {str(e)}")


# End of ecommerce_service.py
