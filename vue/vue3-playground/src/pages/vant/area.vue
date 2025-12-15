<template>
  <div>
    <van-area
      title="省市"
      :area-list="areaList"
      :columns-num="2"
      :columns-placeholder="['省份', '城市']"
    />
  </div>
</template>

<script setup lang="ts">
import { areaList } from '@vant/area-data'
import { onMounted } from 'vue'

onMounted(() => {
  const city_list = areaList.city_list
  const cnNames: string[] = Object.values(city_list)
  console.log(JSON.stringify(cnNames))
})
</script>

<style></style>
