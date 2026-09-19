import { defineConfig } from "astro/config";
import tailwindcss from "@tailwindcss/vite";
import sitemap from "@astrojs/sitemap";
import compressor from "astro-compressor";
import mdx from "@astrojs/mdx";

// https://astro.build/config
export default defineConfig({
  site: "https://thiernothioune.com",
  image: {
    domains: ["images.unsplash.com"],
  },
  prefetch: true,
  integrations: [
    sitemap({
      i18n: {
        defaultLocale: "fr",
        locales: {
          fr: "fr",
          en: "en",
        },
      },
    }),
    compressor({
      gzip: false,
      brotli: true,
    }),
    mdx(),
  ],
  vite: {
    plugins: [tailwindcss()],
    resolve: {
      // Adding alias for React 19 on CF Pages
      alias: process.env.NODE_ENV === 'production' ? {
        'react-dom/server': 'react-dom/server.edge',
      } : undefined,
    },
  },
});
