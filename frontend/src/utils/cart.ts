import { Product } from "../store/slices/chatSlice";

export const mapApiCartToProducts = (data: Record<string, unknown>): Product[] => {
  const rawItems = (data.items ?? data.cart ?? []) as Array<Record<string, unknown>>;
  return rawItems.map((item) => ({
    id: Number(item.id ?? item.product_id),
    title: String(item.title ?? item.product_name ?? ""),
    price: Number(item.price ?? 0),
    quantity: Number(item.quantity ?? 1),
    image: String(item.image ?? ""),
  }));
};

/** Avoid replacing a non-empty local cart with an empty API response. */
export const shouldApplyCartSync = (
  currentCart: Product[],
  apiCart: Product[],
): boolean => apiCart.length > 0 || currentCart.length === 0;
