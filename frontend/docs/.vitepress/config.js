import mathjax3 from "markdown-it-mathjax3";
import { defineConfig } from "vitepress";

export default defineConfig({
  title: "Pressurize",
  description: "Dynamic Valve Pressurization Simulator",
  base: "/products/pressurize/docs/",
  outDir: "../dist/products/pressurize/docs",
  head: [["link", { rel: "canonical", href: "/products/pressurize/" }]],
  outDir: "../dist/products/pressurize/docs",
  markdown: {
    config: (md) => {
      md.use(mathjax3);
    },
  },
  themeConfig: {
    nav: [
      { text: "Home", link: "/" },
      { text: "Overview", link: "/overview" },
      { text: "How to Use", link: "/how-to-use" },
      { text: "Technical Background", link: "/technical-background" },
      { text: "Use Cases", link: "/use-cases" },
      { text: "Launch App", link: "../", target: "_blank", rel: "noopener noreferrer" },
    ],
    sidebar: [
      {
        text: "Guide",
        items: [
          { text: "Overview", link: "/overview" },
          { text: "How to Use", link: "/how-to-use" },
          { text: "Technical Background", link: "/technical-background" },
          { text: "Real World Use Cases", link: "/use-cases" },
        ],
      },
    ],
    socialLinks: [
      { icon: "github", link: "https://github.com/Unmask06/pressurize" },
    ],
  },
});
