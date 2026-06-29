import { useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";
import { RootState, store, persistor } from "../store/store";
import { syncCart } from "../store/slices/chatSlice";
import { mapApiCartToProducts, shouldApplyCartSync } from "../utils/cart";
import { fetchCartFromApi } from "../utils/fetchCart";
import { usePersistReady } from "./usePersistReady";

/** Load cart from the API after persist rehydration and login. */
export const useCartSync = () => {
  const dispatch = useDispatch();
  const persistReady = usePersistReady();
  const isLoggedIn = useSelector((state: RootState) => state.auth.isLoggedIn);

  useEffect(() => {
    if (!persistReady || !isLoggedIn) return;
    if (!localStorage.getItem("access_token")) return;

    let cancelled = false;

    const loadCart = async () => {
      try {
        const cartResponse = await fetchCartFromApi();
        if (cancelled) return;

        const products = mapApiCartToProducts(cartResponse.data);
        const currentCart = store.getState().chat.cart;

        if (shouldApplyCartSync(currentCart, products)) {
          dispatch(syncCart(products));
        }
      } catch {
        // Keep rehydrated cart if the API is unavailable
      }
    };

    loadCart();
    return () => {
      cancelled = true;
    };
  }, [persistReady, isLoggedIn, dispatch]);
};

/** Ensure cart is written to localStorage before the page unloads. */
export const useCartPersistFlush = () => {
  useEffect(() => {
    const flushOnExit = () => {
      void persistor.flush();
    };

    window.addEventListener("beforeunload", flushOnExit);
    window.addEventListener("pagehide", flushOnExit);

    return () => {
      window.removeEventListener("beforeunload", flushOnExit);
      window.removeEventListener("pagehide", flushOnExit);
    };
  }, []);
};
