<script setup lang="ts">
import type { Catalog } from '../../shared/types/catalog'

useSeoMeta({
  title: 'Каталог чая — Лист',
  description: 'Коллекция чая: зелёный, чёрный, белый чай, улуны и пуэры. Происхождение и цены.',
})

const config = useRuntimeConfig()
const apiBaseUrl = import.meta.server
  ? config.apiBaseUrl || config.public.apiBaseUrl
  : config.public.apiBaseUrl
const { data: catalog, error } = await useFetch<Catalog>(`${apiBaseUrl}/api/catalog`, { key: 'catalog', server: true, lazy: false, retry: 0 })
if (import.meta.server && error.value) setResponseStatus(503)
const price = (value: number) => `${new Intl.NumberFormat('ru-RU').format(value)} ₽`
</script>

<template>
  <section class="catalog-page" aria-labelledby="catalog-title">
    <p class="eyebrow">Наша чайная коллекция</p>
    <h1 id="catalog-title" class="page-title">Каталог чая</h1>
    <p class="catalog-intro">Свежесть зелёного чая, мягкость улунов и глубина пуэров.<br class="desktop-break" /> Найдите вкус для своей ежедневной паузы.</p>
    <div v-if="error" class="empty-state" role="alert">
      <h2>Коллекция временно недоступна</h2>
      <p class="empty-description">Не удалось загрузить чай. Попробуйте чуть позже.</p>
      <a class="button button-secondary" href="/catalog">Попробовать снова <span aria-hidden="true">↗</span></a>
    </div>
    <template v-else-if="catalog">
      <div class="catalog-summary">
        <span>В коллекции: {{ catalog.total }}</span>
        <span>Цена за упаковку · ₽</span>
      </div>
      <div v-if="catalog.items.length" class="tea-grid">
        <article v-for="tea in catalog.items" :key="tea.id" class="tea-card" :aria-labelledby="`tea-${tea.id}`">
          <div class="tea-card-top">
            <span class="tea-category">{{ tea.category }}</span>
            <svg class="card-leaf" viewBox="0 0 42 42" fill="none" aria-hidden="true">
              <path d="M10 29C6 13 21 8 35 8c0 17-8 27-22 22l-4 5M13 30l15-15" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round" />
            </svg>
          </div>
          <p class="tea-origin">{{ tea.origin }}</p>
          <h2 :id="`tea-${tea.id}`">{{ tea.name }}</h2>
          <p class="tea-description">{{ tea.description }}</p>
          <div class="tea-card-bottom">
            <p class="tea-price">{{ price(tea.price) }} <span>/ {{ tea.weightGrams }} г</span></p>
            <span class="tea-stock" :class="{ 'is-unavailable': !tea.inStock }">{{ tea.inStock ? 'В наличии' : 'Нет в наличии' }}</span>
          </div>
        </article>
      </div>
      <p v-else class="empty-state">В коллекции пока нет товаров.</p>
      <p class="catalog-note">Демонстрационный ассортимент. Оформление заказов пока недоступно.</p>
    </template>
  </section>
</template>
