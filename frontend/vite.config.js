import tailwindcss from "@tailwindcss/vite";
import vue from "@vitejs/plugin-vue";
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";
import { defineConfig } from "vite";

const __dirname = path.dirname(fileURLToPath(import.meta.url));

// Plugin to serve pre-built VitePress docs from dist folder during dev
function serveStaticDocs() {
  return {
    name: "serve-static-docs",
    configureServer(server) {
      server.middlewares.use((req, res, next) => {
        // Check if request is for docs
        if (req.url?.startsWith("/products/pressurize/docs")) {
          const docsPath = path.resolve(
            __dirname,
            "dist/products/pressurize/docs",
          );
          let urlPath =
            req.url.replace("/products/pressurize/docs", "") || "/index.html";

          // Handle trailing slash
          if (urlPath.endsWith("/") || urlPath === "") {
            urlPath = urlPath + "index.html";
          }

          const filePath = path.join(docsPath, urlPath);

          if (fs.existsSync(filePath)) {
            const ext = path.extname(filePath);
            const contentTypes = {
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
            res.setHeader("Content-Type", contentTypes[ext] || "text/html");
            fs.createReadStream(filePath).pipe(res);
            return;
          }
        }
        next();
      });
    },
  };
}

// https://vite.dev/config/
export default defineConfig(({ command, mode }) => ({
  plugins: [serveStaticDocs(), vue(), tailwindcss()],
  base: mode === "production" ? "/products/pressurize/" : "/",
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
}));
