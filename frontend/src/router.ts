import { createRouter, createWebHistory } from 'vue-router'
import HomeView from './views/HomeView.vue'
import CatalogView from './views/CatalogView.vue'
import NotFoundView from './views/NotFoundView.vue'

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: HomeView, meta: { title: 'Лист — чайный магазин' } },
    { path: '/catalog', component: CatalogView, meta: { title: 'Каталог — Лист' } },
    { path: '/:pathMatch(.*)*', component: NotFoundView, meta: { title: 'Страница не найдена — Лист' } },
  ],
  scrollBehavior: () => ({ top: 0 }),
})

router.afterEach((to) => {
  document.title = String(to.meta.title)
})
