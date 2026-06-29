import { chatApi } from "../services/api";

const sleep = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

/** Retry cart fetch — helps when auth/storage is not ready immediately after refresh. */
export const fetchCartFromApi = async (maxAttempts = 3) => {
  let lastError: unknown;

  for (let attempt = 0; attempt < maxAttempts; attempt++) {
    try {
      if (!localStorage.getItem("access_token")) {
        throw new Error("No access token");
      }
      return await chatApi.getCart();
    } catch (error) {
      lastError = error;
      if (attempt < maxAttempts - 1) {
        await sleep(250 * (attempt + 1));
      }
    }
  }

  throw lastError;
};
