/// <reference types="vitest/config" />
import react from "@vitejs/plugin-react";
import { defineConfig, loadEnv } from "vite";

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  // Where the dev server forwards /api and /health. Override with API_PROXY_TARGET
  // in frontend/.env.local when the backend runs on a non-default port (e.g. because
  // another project already holds 8000). Not a VITE_ variable: it never reaches the bundle.
  const env = loadEnv(mode, process.cwd(), "");
  const apiTarget = env.API_PROXY_TARGET || "http://127.0.0.1:8000";

  return {
    plugins: [react()],
    server: {
      // Listen on all interfaces so a phone on the same Wi-Fi can open the app.
      host: true,
      port: 5173,
      // Proxy the API through the dev server: the browser (or phone) only talks to
      // this origin, so no CORS and no hard-coded laptop IP. Backend stays on localhost.
      proxy: {
        "/api": { target: apiTarget, changeOrigin: true },
        "/health": { target: apiTarget, changeOrigin: true },
      },
    },
    preview: { host: true, port: 4173 },
    test: {
      environment: "jsdom",
      globals: true,
      setupFiles: ["./src/test/setup.ts"],
      include: ["src/**/*.test.{ts,tsx}"],
      coverage: {
        provider: "v8",
        include: ["src/**/*.{ts,tsx}"],
        exclude: ["src/main.tsx", "src/test/**"],
      },
    },
  };
});
