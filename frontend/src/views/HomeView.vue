<script setup lang="ts">
import { RouterLink } from 'vue-router'
</script>

<template>
  <section class="hero" aria-labelledby="hero-title">
    <div class="hero-copy">
      <p class="eyebrow"><span class="short-rule" aria-hidden="true"></span>Чай. Время. Вы.</p>
      <h1 id="hero-title">Место для<br />хорошего <em>чая.</em></h1>
      <p class="hero-description">Для утра без спешки, разговоров по душам<br class="desktop-break" /> и пауз, которые хочется продлить.</p>
      <RouterLink class="button button-primary" to="/catalog">Открыть каталог <span aria-hidden="true">↗</span></RouterLink>
      <p class="quiet-note">Готовим нашу первую чайную коллекцию.</p>
    </div>

    <div class="tea-scene" role="img" aria-label="Иллюстрация: чашка чая и веточка с зелёными листьями">
      <div class="scene-orbit orbit-one"></div>
      <div class="scene-orbit orbit-two"></div>
      <span class="scene-word" aria-hidden="true">slow down</span>
      <svg class="tea-illustration" viewBox="0 0 520 500" fill="none" aria-hidden="true">
        <ellipse cx="270" cy="382" rx="158" ry="24" fill="#244a39" opacity=".08" />
        <ellipse cx="261" cy="360" rx="144" ry="25" fill="#ece6d6" stroke="#bdb8a6" stroke-width="1.5" />
        <path d="M339 238h21c69 0 69 92 0 92h-27" stroke="#e4ddcb" stroke-width="23" />
        <path d="M339 238h21c69 0 69 92 0 92h-27" stroke="#b9b49e" stroke-width="1.4" />
        <path d="M161 226h182l-11 88c-5 40-28 51-79 51-50 0-74-11-79-51l-13-88Z" fill="#f8f4e9" stroke="#b9b49e" stroke-width="1.5" />
        <path d="M177 255c10 56 4 81 41 94" stroke="#e9e2cf" stroke-width="9" stroke-linecap="round" />
        <ellipse cx="252" cy="226" rx="91" ry="20" fill="#e6deca" stroke="#b9b49e" stroke-width="1.5" />
        <ellipse cx="252" cy="227" rx="77" ry="13" fill="#a27a3c" />
        <ellipse cx="245" cy="223" rx="57" ry="7" fill="#bd9657" opacity=".6" />
        <path d="M225 193c-22-30 20-38 0-69M267 188c-22-30 20-38 0-69" stroke="#6f8169" stroke-opacity=".35" stroke-width="2" stroke-linecap="round" />
        <path d="M118 344c-5-70-26-136-64-195" stroke="#68805b" stroke-width="2.5" stroke-linecap="round" />
        <path d="M102 265c-45 1-66-30-63-58 32 6 57 24 63 58Z" fill="#6b825c" />
        <path d="M104 269c-7-44 13-67 37-74 9 28-7 61-37 74Z" fill="#8c9c76" />
        <path d="M80 212c-38-2-51-29-48-50 27 3 44 22 48 50Z" fill="#81956e" />
        <path d="M79 210c-6-34 8-53 28-59 8 22-4 48-28 59Z" fill="#516d4f" />
        <path d="M58 162c-29-5-39-28-33-48 23 7 35 26 33 48Z" fill="#647e58" />
        <path d="M116 315c-37 8-65-10-72-34 28-5 55 7 72 34Z" fill="#9aaa83" />
        <path d="M350 385c20-15 43-17 67-9-18 19-43 23-67 9Z" fill="#6a825b" />
        <path d="M367 391c26 10 47 7 62-8" stroke="#4b6747" stroke-width="1.5" stroke-linecap="round" />
      </svg>
      <span class="scene-caption">одна чашка — целая пауза</span>
    </div>
  </section>

  <section class="welcome-strip" aria-labelledby="welcome-title">
    <div class="welcome-number" aria-hidden="true">01 /</div>
    <h2 id="welcome-title">Знакомство<br />с «Листом»</h2>
    <p>Мы создаём чайный магазин, в котором будет легко найти свой вкус. Сейчас готовим каталог и продумываем детали. Скоро здесь начнётся ваша чайная история.</p>
    <span class="strip-leaf" aria-hidden="true">✳</span>
  </section>
</template>
