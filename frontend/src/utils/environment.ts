// src/utils/environment.ts
export const isStandaloneMode = () => {
  return !window.location.href.includes("embedded");
};
