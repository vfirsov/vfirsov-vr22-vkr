<script setup lang="ts">
useSeoMeta({ title: 'Страница не найдена — Лист' })
if (import.meta.server) setResponseStatus(404)
</script>

<template>
  <section class="not-found-page empty-state" aria-labelledby="not-found-title">
    <p class="eyebrow">Ошибка 404</p>
    <h1 id="not-found-title" class="page-title">Кажется, мы<br />свернули не туда.</h1>
    <p class="empty-description">Такой страницы нет. Вернёмся туда,<br />где всё начинается?</p>
    <NuxtLink class="button button-primary" to="/">На главную <span aria-hidden="true">↗</span></NuxtLink>
  </section>
</template>
