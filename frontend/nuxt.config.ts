export default defineNuxtConfig({
  compatibilityDate: '2026-11-15',
  ssr: true,
  devtools: { enabled: false },
  css: ['~/assets/css/main.css'],
  runtimeConfig: { public: { apiBaseUrl: 'http://127.0.0.1:8080' } },
  nitro: { preset: 'node-server' },
  routeRules: {
    '/catalog': { ssr: true, prerender: false, cache: false, headers: { 'cache-control': 'no-store' } },
  },
  app: {
    head: {
      htmlAttrs: { lang: 'ru' },
      title: 'Лист — чайный магазин',
      meta: [
        { name: 'theme-color', content: '#294e3c' },
        { name: 'description', content: 'Лист — чайный магазин. Хороший чай для маленьких ежедневных ритуалов.' },
      ],
      link: [{ rel: 'icon', type: 'image/svg+xml', href: '/leaf.svg' }],
    },
  },
})
