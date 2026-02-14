import tailwindcss from "@tailwindcss/vite";
import vue from "@vitejs/plugin-vue";
import fs from "fs";
import type { IncomingMessage, ServerResponse } from "http";
import path from "path";
import { fileURLToPath } from "url";
import { defineConfig, type ViteDevServer } from "vite";

const __dirname = path.dirname(fileURLToPath(import.meta.url));

function serveStaticDocs() {
  return {
    name: "serve-static-docs",
    configureServer(server: ViteDevServer) {
      server.middlewares.use((req, res, next) => {
        const request = req as IncomingMessage & { url?: string };
        const response = res as ServerResponse;
        if (request.url?.startsWith("/products/pressurize/docs")) {
          const docsPath = path.resolve(
            __dirname,
            "dist/products/pressurize/docs",
          );
          let urlPath =
            request.url.replace("/products/pressurize/docs", "") ||
            "/index.html";

          if (urlPath.endsWith("/") || urlPath === "") {
            urlPath = `${urlPath}index.html`;
          }

          const filePath = path.join(docsPath, urlPath);

          if (fs.existsSync(filePath)) {
            const ext = path.extname(filePath);
            const contentTypes: Record<string, string> = {
              ".html": "text/html",
              ".css": "text/css",
              ".js": "application/javascript",
              ".json": "application/json",
              ".svg": "image/svg+xml",
              ".png": "image/png",
              ".jpg": "image/jpeg",
              ".woff": "font/woff",
              ".woff2": "font/woff2",
            };
            response.setHeader(
              "Content-Type",
              contentTypes[ext] || "text/html",
            );
            fs.createReadStream(filePath).pipe(response);
            return;
          }
        }
        next();
      });
    },
  };
}

export default defineConfig({
  plugins: [serveStaticDocs(), vue(), tailwindcss()],
  base: "/products/pressurize/",
  build: {
    outDir: "dist/products/pressurize",
  },
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "src"),
    },
  },
  server: {
    port: 5173,
  },
});
