<template>
  <div class="container" id="container"></div>
  <div class="buttons">
    <button v-if="overlaysVisible['mask']" @click="() => mask && mask.hide()">隐藏遮罩</button>
    <button v-if="!overlaysVisible['mask']" @click="() => mask && mask.show()">显示遮罩</button>
    <button v-if="overlaysVisible['track']" @click="() => track && track.hide()">隐藏路线</button>
    <button v-if="!overlaysVisible['track']" @click="() => track && track.show()">显示路线</button>
  </div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue'
import AMapLoader from '@amap/amap-jsapi-loader'
import { parseTcxFile, type TrackPointType } from '@/utils/tcx'
import { adjustColorBrightness, getBrightGradientColor } from '@/utils/colors'
import { simplify, simplifyDouglas, wgs84ToGcj02 } from '@/utils/coordinate'
import { loadYpx } from '@/utils/ypx'

const amap = ref()
const overlaysVisible = ref<Record<string, boolean>>({
  mask: true,
  track: true,
})
const mask = ref<AMap.Polygon>()
const track = ref<AMap.OverlayGroup>()

async function initMap(
  initConfig = {
    key: '',
    // 在2021年12月02日以后申请的key需要配合安全密钥一起使用
    // 服务端代理进行转发 - 推荐
    serviceHost: '', // "https://your_domain/_AMapService",
    // 直接明文声明安全密钥 - 不安全
    securityJsCode: '',
  },
  option?: AMap.MapOptions,
): Promise<AMap.Map> {
  if (!initConfig?.key) {
    alert('未配置高德地图Key')
    throw new Error('未配置高德地图Key')
  }
  if (initConfig?.serviceHost) {
    console.debug(`serviceHost=${initConfig.serviceHost}`)
  }
  if (initConfig?.securityJsCode) {
    console.warn(`注意安全密钥泄露 securityJsCode=${initConfig.securityJsCode}`)
  }
  window._AMapSecurityConfig = initConfig

  return AMapLoader.load({
    key: initConfig.key, // 申请高德地图key
    version: '2.0', // 指定地图版本
    // 预加载需要使用的插件
    // 插件的更多加载方式参考 https://lbs.amap.com/api/javascript-api-v2/guide/abc/plugins
    // 更多插件清单参考 https://lbs.amap.com/api/javascript-api-v2/guide/abc/plugins-list
    plugins: [
      'AMap.HawkEye', // 鹰眼
      'AMap.MapType', // 图层切换控件
      'AMap.ToolBar', // 缩放工具条
      'AMap.Scale', // 比例尺
    ],
  })
    .then((AMap) => {
      const defaultOptions: AMap.MapOptions = {
        zoom: 11, //级别
        center: [116.397428, 39.90923], //中心点坐标
        viewMode: '2D', //使用3D视图
      }
      const map = new AMap.Map('container', { ...defaultOptions, ...option })

      map.on('complete', function () {
        console.debug('amap实例加载完成')
      })
      map.on('click', function (evt: { lnglat: AMap.LngLat; pixel: AMap.Pixel; type: string }) {
        console.debug(
          `amap地图被点击,类型:${evt.type},位置:lng=${evt.lnglat.getLng()},lat=${evt.lnglat.getLat()}`,
        )
      })

      // 添加插件
      map.addControl(new AMap.ToolBar())
      map.addControl(new AMap.Scale())
      map.addControl(new AMap.HawkEye())
      map.addControl(new AMap.MapType())

      amap.value = map

      return map
    })
    .catch((e) => {
      console.error(e)
    })
}

async function loadTcx(tcxUrl: string) {
  const result = await parseTcxFile(tcxUrl)
  console.debug(`tcx运动类型为:${result.activityType}, 共加载了${result.trackPoints.length}个点`)
  const points = result.trackPoints
  points.forEach((point) => {
    const { lng, lat } = wgs84ToGcj02(point.lng, point.lat)
    point.lat = lat
    point.lng = lng
  })
  return points
}

async function loadJson(jsonUrl: string) {
  // 1. 下载 JSON 文件
  const response = await fetch(jsonUrl)
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`)
  }
  const jsonText = await response.text()
  const array = JSON.parse(jsonText)
  const points = [] as TrackPointType[]
  for (let i = 0; i < array.length; i += 2) {
    const point = array[i]
    points.push({
      lng: point[1],
      lat: point[0],
      time: null,
      distanceMeters: null,
      speed: null,
      cadence: null,
      heartRate: null,
      pace: null,
    })
  }
  return points
}

function createMask(map: AMap.Map) {
  // 外多边形坐标数组和内多边形坐标数组
  const outer = [
    new AMap.LngLat(-360, 90, true),
    new AMap.LngLat(-360, -90, true),
    new AMap.LngLat(360, -90, true),
    new AMap.LngLat(360, 90, true),
  ]

  const pathArray = [outer]
  pathArray.push.apply(pathArray)
  const polygon = new AMap.Polygon()
  polygon.setOptions({
    strokeColor: '#00eeff',
    strokeWeight: 1,
    fillColor: '#000000',
    fillOpacity: 0.2,
    zIndex: 1,
  })
  // const holes = result.districtList[0].boundaries
  polygon.setPath(pathArray)
  // @ts-expect-error
  polygon.on('hide', () => (overlaysVisible.value['mask'] = false))
  // @ts-expect-error
  polygon.on('show', () => (overlaysVisible.value['mask'] = true))
  map.add(polygon)
  mask.value = polygon
}

function buildPolyline_colorOnPace(points: TrackPointType[]) {
  // let paceFast = 15
  // let paceSlow = 3
  // points.forEach((p) => {
  //   if (!p.pace) return
  //   if (p.pace < paceFast) paceFast = p.pace
  //   if (p.pace > paceSlow) paceSlow = p.pace
  // })
  const paceFast = 4
  const paceSlow = 10
  const paceAmplitude = Math.abs(paceFast - paceSlow)

  const polylines = [] as AMap.Polyline[]
  for (let index = 1; index < points.length; index++) {
    const p_prev = points[index - 1]!
    const p_curr = points[index]!
    polylines.push(
      new AMap.Polyline({
        path: [
          [p_prev.lng, p_prev.lat],
          [p_curr.lng, p_curr.lat],
        ],
        strokeColor: getBrightGradientColor(
          '#9AF166',
          '#EA3323',
          (paceSlow - (p_curr.pace ?? paceSlow)) / paceAmplitude,
        ),
        lineJoin: 'round', // 折线拐点连接处样式
      }),
    )
  }
  return polylines
}

type DestinyConfig = {
  baseColor?: string
  gridSize?: number
  maxPoints?: number
  segmentLength?: number
}

/**
 * 在高德地图上绘制基于密度的动态亮度轨迹折线
 * @param {Array} tracks 轨迹数组
 * @param {Object} options 配置选项
 * @param {String} options.baseColor 基础颜色，默认"#ff0000"
 * @param {Number} options.maxPoints 用于计算密度的最大点数，避免极端值影响，默认100
 * @param {Number} options.segmentLength 每段折线的点数（控制颜色精度）
 */
function buildPolyline_colorOnQuantity(
  tracks: TrackPointType[][],
  options?: DestinyConfig,
): AMap.Polyline[] {
  // 合并配置选项
  const config = {
    baseColor: '#ff0000',
    maxPoints: 100,
    segmentLength: 2,
    ...options,
  }

  // 性能优化：合并所有轨迹点并去重，减少计算量
  const allPoints = new Map()
  tracks.forEach((track) => {
    track.forEach(({ lng, lat }) => {
      const key = `${lng.toFixed(6)},${lat.toFixed(6)}` // 保留6位小数精度去重
      allPoints.set(key, { lng, lat, count: (allPoints.get(key)?.count || 0) + 1 })
    })
  })

  // 计算密度分布和最大值
  const maxDensity = Math.min(
    Array.from(allPoints.values()).reduce((max, val) => Math.max(max, val.count), 0),
    config.maxPoints,
  )

  // 为每条轨迹创建折线，并根据密度设置颜色
  const polylines = [] as AMap.Polyline[]

  tracks.forEach((track) => {
    // 性能优化：对过长轨迹进行抽稀
    const points = simplifyDouglas(
      track.map((point) => [point.lng, point.lat]),
      0.00001,
    ) // 抽稀阈值，可根据精度调整
    if (points.length < 2) return

    // 按segmentLength拆分轨迹为多段折线
    for (let i = 0; i < points.length - 1; i += config.segmentLength) {
      // 确定当前段的起点和终点
      const endIndex = Math.min(i + config.segmentLength, points.length - 1)
      const segment = points.slice(i, endIndex + 1)

      // 计算当前段的平均密度（取段中点的密度）
      const midIndex = Math.floor(segment.length / 2)
      const [midLng, midLat] = segment[midIndex]!
      const midKey = `${midLng!.toFixed(6)},${midLat!.toFixed(6)}`
      const density = allPoints.get(midKey) || 1
      const densityRatio = Math.min(density / maxDensity, 1)

      // 根据密度计算颜色（亮度调整）
      const strokeColor = adjustColorBrightness(config.baseColor, densityRatio)

      // 创建当前段的折线（使用高德官方API）
      const polyline = new AMap.Polyline({
        path: segment as AMap.LngLatLike[],
        strokeColor: strokeColor,
        zIndex: 50,
      })

      // polyline.setMap(map);
      polylines.push(polyline)
    }
  })

  return polylines
}

type LocalLngLat = { lng: number; lat: number }

/**
 * 在高德地图上绘制基于网格密度的动态亮度轨迹折线
 * @param {Array} tracks 轨迹数组
 * @param {Object} options 配置选项
 * @param {String} options.baseColor 基础颜色，默认"#ff0000"
 * @param {Number} options.gridSize 网格大小(米)，用于密度计算，默认10（关键参数）
 * @param {Number} options.maxPoints 用于计算密度的最大点数，避免极端值影响，默认100
 * @param {Number} options.segmentLength 每段折线的点数（控制颜色精度）
 */
function buildPolyline_colorOnGrid(
  tracks: TrackPointType[][],
  options?: DestinyConfig,
): AMap.Polyline[] {
  // 合并配置选项
  const config = {
    baseColor: '#ff0000',
    gridSize: 10,
    maxPoints: 100,
    segmentLength: 2,
    ...options,
  }

  // 1. 提取所有轨迹点（经纬度数组）
  const allPoints = [] as LocalLngLat[]
  tracks.forEach((track) => {
    track.forEach(({ lng, lat }) => {
      allPoints.push({ lng, lat })
    })
  })
  if (allPoints.length === 0) return []

  // 2. 计算中心点（用于网格参考原点）
  const center = getCenterPoint(allPoints)

  // 3. 基于网格计算密度（核心：自定义方位角+距离计算）
  const gridDensity = new Map() // 键：网格ID，值：点数

  // 找出坐标点所属网格
  const locateGridId = (point: LocalLngLat) => {
    // 计算当前点相对于中心点的方位角（自定义实现）
    const bearing = calculateBearing(center, point)
    // 计算两点距离（使用高德官方distance方法）
    const distance = new AMap.LngLat(center.lng, center.lat).distance(
      new AMap.LngLat(point.lng, point.lat),
    )

    // 极坐标转平面坐标（x:东向，y:北向，单位：米）
    const radians = (bearing * Math.PI) / 180
    const x = distance * Math.sin(radians) // 东向偏移
    const y = distance * Math.cos(radians) // 北向偏移

    // 计算网格ID
    const gridX = Math.floor(x / config.gridSize)
    const gridY = Math.floor(y / config.gridSize)
    const gridId = `${gridX},${gridY}`
    return gridId
  }

  allPoints.forEach((point) => {
    const gridId = locateGridId(point)
    // 累加网格点数
    gridDensity.set(gridId, (gridDensity.get(gridId) || 0) + 1)
  })

  // 4. 计算最大密度
  const maxDensity = Math.min(
    Array.from(gridDensity.values()).reduce((max, val) => Math.max(max, val), 0),
    config.maxPoints,
  )

  // 5. 绘制轨迹
  const polylines = [] as AMap.Polyline[]
  tracks.forEach((track) => {
    const simplifiedTrack = simplifyDouglas(
      track.map((p) => [p.lng, p.lat]),
      0.00001,
    ) // 抽稀
    // const simplifiedTrack = track.map((p) => [p.lng, p.lat]) // 不抽稀
    if (simplifiedTrack.length < 2) return

    // 分段处理
    for (let i = 0; i < simplifiedTrack.length - 1; i += config.segmentLength) {
      const endIndex = Math.min(i + config.segmentLength, simplifiedTrack.length - 1)
      const segment = simplifiedTrack.slice(i, endIndex + 1)

      // 计算线段中点的密度
      const midIndex = Math.floor(segment.length / 2)
      const midPoint = {
        lng: segment[midIndex]![0]!,
        lat: segment[midIndex]![1]!,
      }
      const gridId = locateGridId(midPoint)

      // 计算颜色
      const density = gridDensity.get(gridId) || 1
      const densityRatio = Math.min(density / maxDensity, 1)
      const strokeColor = adjustColorBrightness(config.baseColor, densityRatio)

      // 创建折线（官方API）
      const polyline = new AMap.Polyline({
        lineJoin: 'round', // 折线拐点连接处样式
        path: segment as AMap.LngLatLike[],
        strokeColor: strokeColor,
        zIndex: 50,
      })

      polylines.push(polyline)
    }
  })
  return polylines
}

/**
 * 自定义计算两点间的方位角（从pointA到pointB的角度）
 * @param {Object} pointA 起点 {lng, lat}
 * @param {Object} pointB 终点 {lng, lat}
 * @returns {Number} 方位角（度，0-360，正北为0度，顺时针递增）
 */
function calculateBearing(pointA: LocalLngLat, pointB: LocalLngLat): number {
  // 转换为弧度
  const lat1 = (pointA.lat * Math.PI) / 180
  const lon1 = (pointA.lng * Math.PI) / 180
  const lat2 = (pointB.lat * Math.PI) / 180
  const lon2 = (pointB.lng * Math.PI) / 180

  // 球面三角学公式计算方位角
  const dLon = lon2 - lon1
  const y = Math.sin(dLon) * Math.cos(lat2)
  const x = Math.cos(lat1) * Math.sin(lat2) - Math.sin(lat1) * Math.cos(lat2) * Math.cos(dLon)
  const bearing = (Math.atan2(y, x) * 180) / Math.PI

  // 转换为0-360度
  return (bearing + 360) % 360
}

// 辅助函数：计算所有点的中心点（用于网格坐标偏移）
function getCenterPoint(points: LocalLngLat[]) {
  const sumLng = points.reduce((sum, p) => sum + p.lng, 0)
  const sumLat = points.reduce((sum, p) => sum + p.lat, 0)
  return {
    lng: sumLng / points.length,
    lat: sumLat / points.length,
  }
}

/**
 * 在高德地图上绘制基于网格密度的动态亮度轨迹折线
 * @param {Array} tracks 轨迹数组
 * @param {Object} options 配置选项
 * @param {String} options.baseColor 基础颜色，默认"#ff0000"
 */
function buildPolyline_colorFixed(
  tracks: TrackPointType[][],
  options?: DestinyConfig,
): AMap.Polyline[] {
  // 合并配置选项
  const config = {
    baseColor: '#ff0000',
    ...options,
  }

  // 绘制轨迹
  const polylines = [] as AMap.Polyline[]
  tracks.forEach((track) => {
    const simplifiedTrack = simplifyDouglas(
      track.map((p) => [p.lng, p.lat]),
      0.00001,
    ) // 抽稀
    // const simplifiedTrack = track.map((p) => [p.lng, p.lat]) // 不抽稀
    if (simplifiedTrack.length < 2) return

    // 分段处理
    for (let i = 0; i < simplifiedTrack.length - 1; i++) {
      const segment = simplifiedTrack.slice(i, i + 2)
      // 创建折线（官方API）
      const polyline = new AMap.Polyline({
        lineJoin: 'round', // 折线拐点连接处样式
        path: segment as AMap.LngLatLike[],
        strokeColor: config.baseColor,
        zIndex: 50,
      })

      polylines.push(polyline)
    }
  })
  return polylines
}

onMounted(() => {
  const mapConfig = {
    key: import.meta.env.VITE_AMAP_KEY,
    serviceHost: '',
    securityJsCode: import.meta.env.VITE_AMAP_SECURITY_JS_CODE,
  }
  const mapOption = {
    mapStyle: import.meta.env.VITE_AMAP_MAP_STYLE,
  }
  Promise.all([
    initMap(mapConfig, mapOption),
    Promise.all([
      loadTcx('/data/13238395397.tcx'),
      loadTcx('/data/13265099379.tcx'),
      // loadYpx('/data/1023642168.ypx'), // 江湾大桥附近
      loadYpx('/data/1043960695.ypx'),
    ]),
    loadJson('/data/simple-data.json'),
  ]).then(async (results) => {
    const [map, tracks, _track5] = results
    createMask(map)

    let polylines: AMap.Polyline[] | undefined = undefined

    // 单轨迹，配速控制颜色
    // polylines = buildPolyline_colorOnPace(simplify(track1, 5))
    // 多轨迹，点数量密度控制颜色
    // polylines = buildPolyline_colorOnQuantity(tracks, {
    //   baseColor: '#BDFD51',
    // })
    // 多轨迹，网格采样密度控制颜色
    // polylines = buildPolyline_colorOnGrid(tracks, {
    //   baseColor: '#9ffd00',
    //   gridSize: 1,
    // })
    // 多轨迹，固定颜色
    polylines = buildPolyline_colorFixed(tracks, { baseColor: '#9ffd00' })

    const overlayGroup = new AMap.OverlayGroup(polylines)
    // 对此覆盖物群组设置同一属性
    overlayGroup.setOptions({
      strokeWeight: 3,
      strokeOpacity: 0.4,
      borderWeight: 1,
      zIndex: 10,
    })
    overlayGroup.on('hide', () => (overlaysVisible.value['track'] = false))
    overlayGroup.on('show', () => (overlaysVisible.value['track'] = true))
    track.value = overlayGroup
    // @ts-expect-error
    map.add(overlayGroup)

    map.setFitView(polylines)
  })
})

function destroyMap() {
  console.debug('amap实例销毁')
  amap.value?.destroy()
  amap.value = null
}

onUnmounted(() => {
  destroyMap()
})
</script>

<style scoped>
.container {
  width: 100%;
  height: 100vh;
}

.buttons {
  display: flex;
  /* justify-content: space-around; */
  gap: 10px;
  padding: 10px;
}
</style>
