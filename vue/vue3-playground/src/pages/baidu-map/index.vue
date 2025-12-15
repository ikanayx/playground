<template>
  <div>
    <div id="mapContainer"></div>
  </div>
</template>

<script setup lang="ts">
import { wgs84ToBd09 } from '@/utils/coordinate'
import { loadJs } from '@/utils/dom'
import { loadYpx } from '@/utils/ypx'
import { onMounted } from 'vue'

onMounted(() => {
  if (!('BMapGL' in window)) {
    const key = import.meta.env.VITE_BAIDU_MAP_KEY
    ;(window as any).mapCallback = initMap
    loadJs(`https://api.map.baidu.com/api?v=1.0&type=webgl&ak=${key}&callback=mapCallback`, false)
    // loadJs(`https://api.map.baidu.com/api?v=3.0&ak=${key}&callback=mapCallback`, false)
  } else {
    initMap()
  }
})

enum COORDINATE_TYPE {
  COORDINATES_WGS84 = 1, // WGS84坐标
  COORDINATES_WGS84_MC = 2, // WGS84的平面墨卡托坐标
  COORDINATES_GCJ02 = 3, // GCJ02坐标
  COORDINATES_GCJ02_MC = 4, // GCJ02的平面墨卡托坐标
  COORDINATES_BD09 = 5, // 百度bd09经纬度坐标
  COORDINATES_BD09_MC = 6, // 百度bd09墨卡托坐标
  COORDINATES_MAPBAR = 7, // mapbar地图坐标
  COORDINATES_51 = 8, // 51地图坐标
}

function convert(points: BMapGL.Point[], srcType: COORDINATE_TYPE, dstType: COORDINATE_TYPE) {
  return new Promise<BMapGL.Point[]>((resolve, reject) => {
    setTimeout(() => {
      const convertor = new BMapGL.Convertor()
      convertor.translate(points, srcType, dstType, function (data) {
        if (data.status === 0) {
          resolve(data.points)
        } else {
          reject('转换异常:' + JSON.stringify(data))
        }
      })
    }, 1000)
  })
}

async function initMap() {
  // const points = await loadYpx('/data/unknown_bd09.ypx')
  // const bd09 = points.map(({ lng, lat }) => ({ lng, lat }) as BMapGL.Point)
  const points = await loadYpx('/data/1177034309_wgs84.ypx')
  const bd09 = points.map(({ lng, lat }) => wgs84ToBd09(lng, lat) as BMapGL.Point)
  //const bd09 = points.map((p) => wgs84ToBd09(p.lng, p.lat) as BMapGL.Point)

  const map = new BMapGL.Map('mapContainer') //地图初始化
  map.centerAndZoom(new BMapGL.Point(116.4041, 39.914435), 16)
  map.enableScrollWheelZoom()

  // 创建折线
  const polyline = new BMapGL.Polyline(bd09, {
    strokeColor: '#3498db', // 线条颜色
    strokeWeight: 6, // 线条宽度
    strokeOpacity: 0.8, // 线条透明度
    strokeStyle: 'solid', // 线条样式
  })

  // 添加折线到地图
  map.addOverlay(polyline)

  // 调整视野，留出一定边距
  map.setViewport(bd09, { margins: [50, 50, 50, 50] })
}
</script>

<style scoped>
#mapContainer {
  width: 100vw;
  height: 100vh;
}
</style>
