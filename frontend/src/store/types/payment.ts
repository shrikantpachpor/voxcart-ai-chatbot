// src/types/payment.ts
export interface PaymentMethod {
    id: number;
    brand: string;
    last4: string;
    exp_month: number;
    exp_year: number;
    is_default: boolean;
  }
  
  export interface PaymentRequest {
    amount: number;
    payment_method_id: number;
  }
  
  export interface AddPaymentMethodRequest {
    card_number: string;
    exp_month: number;
    exp_year: number;
    cvc: string;
    save_card?: boolean;
  }
  
  export interface CartItem {
    id: number;
    title: string;
    price: number;
    quantity: number;
    image: string;
  }
  
  export interface CartResponse {
    items: CartItem[];
    total_price: number;
  }