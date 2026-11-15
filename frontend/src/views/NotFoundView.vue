<script setup lang="ts">
import { RouterLink } from 'vue-router'
</script>

<template>
  <section class="not-found-page empty-state" aria-labelledby="not-found-title">
    <p class="eyebrow">Ошибка 404</p>
    <h1 id="not-found-title" class="page-title">Кажется, мы<br />свернули не туда.</h1>
    <p class="empty-description">Такой страницы нет. Вернёмся туда,<br />где всё начинается?</p>
    <RouterLink class="button button-primary" to="/">На главную <span aria-hidden="true">↗</span></RouterLink>
  </section>
</template>
