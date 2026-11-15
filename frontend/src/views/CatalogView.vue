<script setup lang="ts">
import { RouterLink } from 'vue-router'
</script>

<template>
  <section class="catalog-page" aria-labelledby="catalog-title">
    <p class="eyebrow">Наша будущая коллекция</p>
    <h1 id="catalog-title" class="page-title">Каталог чая</h1>
    <div class="empty-state">
      <svg class="empty-leaf" viewBox="0 0 80 80" fill="none" aria-hidden="true">
        <path d="M20 55C12 27 38 16 65 15c1 30-14 51-39 41l-8 10M26 56l25-26" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
      </svg>
      <p class="eyebrow">Всему своё время</p>
      <h2>Хороший чай<br />скоро будет здесь.</h2>
      <p class="empty-description">Мы готовим первую коллекцию.<br />Товары и оформление заказов пока недоступны.</p>
      <RouterLink class="button button-secondary" to="/">На главную <span aria-hidden="true">↗</span></RouterLink>
    </div>
  </section>
</template>
