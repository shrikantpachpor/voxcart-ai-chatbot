from rapidfuzz import fuzz

def find_best_match(user_required_product, products):
    """
    Find the best matching product from a list based on user requirements.
    
    Args:
        user_required_product: Either a string or dict containing product name and attributes
        products: List of product dictionaries to search through
    
    Returns:
        Best matching product dict or None if no match above threshold
    """
    best_match = None
    best_score = 0
    
    if isinstance(user_required_product, str):
        user_product_name = user_required_product.lower()
    elif isinstance(user_required_product, dict) and "product" in user_required_product:
        user_product_name = user_required_product["product"].lower()
    else:
        user_product_name = ""
    
    user_attributes = {}
    if isinstance(user_required_product, dict):
        user_attributes = user_required_product.get("attributes", {})
        user_attributes = {k.lower(): str(v).lower() for k, v in user_attributes.items() if v}
    
    for product in products:
        product_title = product.get("title", "").lower()
        product_description = product.get("description", "").lower()
        
        name_score = fuzz.partial_ratio(user_product_name, product_title)
        desc_score = fuzz.partial_ratio(user_product_name, product_description)
        base_score = max(name_score, desc_score)
        
        attribute_bonus = 0
        
        for attr, value in user_attributes.items():
            found_in_title = value in product_title
            found_in_desc = value in product_description
            found_in_field = attr in product and value in str(product[attr]).lower()
            
            if found_in_title or found_in_desc or found_in_field:
                attribute_bonus += 20
        
        final_score = base_score + attribute_bonus
        
        if final_score > best_score:
            best_score = final_score
            best_match = product

    return best_match if best_score > 60 else None
