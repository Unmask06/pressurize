import tailwindcss from "@tailwindcss/vite";
import vue from "@vitejs/plugin-vue";
import { defineConfig } from "vite";

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue(), tailwindcss()],
  base: "/products/pressurize/",
  build: {
    outDir: "dist/products/pressurize",
  },
  server: {
    port: 5173,
    strictPort: false,
    host: "127.0.0.1",
    middlewareMode: false,
    fs: {
      allow: [".", "../docs"],
    },
  },
});
