import { useEffect, useState } from "react";
import { persistor } from "../store/store";

export const usePersistReady = () => {
  const [ready, setReady] = useState(() => persistor.getState().bootstrapped);

  useEffect(() => {
    if (persistor.getState().bootstrapped) {
      setReady(true);
      return;
    }

    const unsubscribe = persistor.subscribe(() => {
      if (persistor.getState().bootstrapped) {
        setReady(true);
      }
    });

    return unsubscribe;
  }, []);

  return ready;
};
