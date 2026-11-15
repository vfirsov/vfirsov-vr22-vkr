<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router'
</script>

<template>
  <a class="skip-link" href="#main">Перейти к содержимому</a>
  <div class="site-shell">
    <header class="site-header">
      <RouterLink class="brand" to="/" aria-label="Лист — на главную">
        <svg class="brand-mark" viewBox="0 0 42 42" fill="none" aria-hidden="true">
          <path d="M10 29C6 13 21 8 35 8c0 17-8 27-22 22l-4 5M13 30l15-15" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" />
        </svg>
        <span class="brand-name">лист<span class="brand-caption">чайный магазин</span></span>
      </RouterLink>
      <nav class="main-nav" aria-label="Основная навигация">
        <RouterLink to="/" exact-active-class="is-active" active-class="">Главная</RouterLink>
        <RouterLink to="/catalog" active-class="is-active">Каталог</RouterLink>
      </nav>
      <span class="opening-note"><span aria-hidden="true"></span>Скоро открытие</span>
    </header>

    <main id="main" tabindex="-1">
      <RouterView />
    </main>

    <footer class="site-footer">
      <span class="footer-brand">лист</span>
      <p>Хороший чай для маленьких ежедневных ритуалов.</p>
      <span class="demo-label">Демонстрационная версия</span>
    </footer>
  </div>
</template>
