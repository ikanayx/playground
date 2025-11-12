<template>
  <div class="page-container">
    <router-link v-for="route in routes" :key="route.path" :to="route.path">
      {{ route.meta.title || route.path }}
    </router-link>
  </div>
</template>

<script setup lang="ts">
import router from '@/router'
import { computed } from 'vue'

const routes = computed(() =>
  router
    .getRoutes()
    .filter((r) => !['/', '/navigator', '/404', '/:pathMatch(.*)*'].includes(r.path)),
)
</script>

<style scoped>
.page-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding-top: 100px;
  min-height: 100vh;
}

a {
  color: #ffffff;
}
</style>
