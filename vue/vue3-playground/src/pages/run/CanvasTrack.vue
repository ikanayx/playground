<template>
  <div class="page-container">
    <div class="row" v-for="i in Math.min(normalUrls.length, besselUrls.length)" :key="i">
      <div class="col">
        <div>普通绘图</div>
        <img v-if="normalUrls[i - 1]" :src="normalUrls[i - 1]" />
      </div>
      <div class="col">
        <div>贝塞尔曲线绘图</div>
        <img v-if="besselUrls[i - 1]" :src="besselUrls[i - 1]" />
      </div>
    </div>
    <canvas id="mapCanvas" style="border: 1px solid #333"></canvas>
  </div>
</template>

<script setup lang="ts">
import { wgs84ToGcj02 } from '@/utils/coordinate'
import { base64ToBlob } from '@/utils/file'
import { parseTcxFile, type TrackPointType } from '@/utils/tcx'
import { loadYpx } from '@/utils/ypx'
import { onMounted, ref } from 'vue'

type GeoPoint = { lng: number; lat: number }

type CanvasPoint = { x: number; y: number }

type CanvasOption = {
  canvasWidth: number
  canvasHeight: number
  padding: number
  lineWidth: number
  lineColor: string
  simplifiedRatio: number
  besselRatio?: number
}

const canvasOption = ref<CanvasOption>()

// 优化：根据实际数据范围计算缩放和偏移
const optimizeCanvasForData = (
  geoPoints: GeoPoint[],
  canvasWidth: number,
  canvasHeight: number,
  padding = 50,
) => {
  // 计算数据的经纬度范围
  const lngs = geoPoints.map((p) => p.lng)
  const lats = geoPoints.map((p) => p.lat)
  const minLng = Math.min(...lngs)
  const maxLng = Math.max(...lngs)
  const minLat = Math.min(...lats)
  const maxLat = Math.max(...lats)

  // 轨迹中心坐标
  const centerLng = (minLng + maxLng) / 2
  const centerLat = (minLat + maxLat) / 2

  // 计算经度和纬度方向的缩放比例（取较小值避免超出画布）
  const lngRange = maxLng - minLng
  const latRange = maxLat - minLat
  const scaleX = (canvasWidth - 2 * padding) / lngRange // 经度方向缩放
  const scaleY = (canvasHeight - 2 * padding) / latRange // 纬度方向缩放
  const scale = Math.min(scaleX, scaleY) // 统一缩放比例

  // 转换函数（基于数据范围的局部坐标）
  const geoToLocalCanvas = (lng: number, lat: number) => {
    const x = padding + (lng - minLng) * scale
    const y = padding + (maxLat - lat) * scale // 纬度y轴翻转
    return { x, y }
  }

  return {
    centerLng,
    centerLat,
    convert: geoToLocalCanvas,
  }
}

// 点到直线的距离计算（辅助函数）
const pointToLineDistance = (p: CanvasPoint, p1: CanvasPoint, p2: CanvasPoint) => {
  const A = p.x - p1.x
  const B = p.y - p1.y
  const C = p2.x - p1.x
  const D = p2.y - p1.y
  const dot = A * C + B * D
  const lenSq = C * C + D * D
  let param = -1
  if (lenSq !== 0) param = dot / lenSq
  let xx, yy
  if (param < 0) {
    xx = p1.x
    yy = p1.y
  } else if (param > 1) {
    xx = p2.x
    yy = p2.y
  } else {
    xx = p1.x + param * C
    yy = p1.y + param * D
  }
  const dx = p.x - xx
  const dy = p.y - yy
  return Math.sqrt(dx * dx + dy * dy)
}

// 道格拉斯-普克算法简化点集
const simplifyPoints = (points: CanvasPoint[], epsilon: number): CanvasPoint[] => {
  if (points.length <= 2) return points // 少于2个点直接返回
  let maxDist = 0
  let index = 0
  const start = 0
  const end = points.length - 1

  // 找到距离最远的点
  for (let i = start + 1; i < end; i++) {
    const dist = pointToLineDistance(points[i]!, points[start]!, points[end]!)
    if (dist > maxDist) {
      maxDist = dist
      index = i
    }
  }

  // 若距离大于阈值，递归简化
  if (maxDist > epsilon) {
    const left = simplifyPoints(points.slice(start, index + 1), epsilon)
    const right = simplifyPoints(points.slice(index, end + 1), epsilon)
    // 合并结果（去重中间点）
    return [...left.slice(0, -1), ...right]
  } else {
    // 否则保留首尾点
    return [points[start]!, points[end]!]
  }
}

// 生成三次贝塞尔曲线的控制点
const getControlPoints = (points: CanvasPoint[]) => {
  const cp1 = [] // 第一个控制点数组
  const cp2 = [] // 第二个控制点数组
  const n = points.length - 1

  // 处理起点和终点（无控制点，直接使用相邻点）
  cp1.push({ x: points[0]!.x, y: points[0]!.y })
  cp2.push({ x: points[0]!.x, y: points[0]!.y })

  // 中间点的控制点计算（基于相邻点的斜率）
  for (let i = 1; i < n; i++) {
    const pPrev = points[i - 1]!
    const pCurr = points[i]!
    const pNext = points[i + 1]!

    // 计算前一段和后一段的斜率
    const dx1 = pCurr.x - pPrev.x
    const dy1 = pCurr.y - pPrev.y
    const dx2 = pNext.x - pCurr.x
    const dy2 = pNext.y - pCurr.y

    // 控制点偏移比例（0.2-0.3较自然）
    const ratio = canvasOption.value?.besselRatio || defaultOption.besselRatio

    // 第一个控制点（基于前一段）
    cp1.push({
      x: pCurr.x - dx1 * ratio,
      y: pCurr.y - dy1 * ratio,
    })

    // 第二个控制点（基于后一段）
    cp2.push({
      x: pCurr.x + dx2 * ratio,
      y: pCurr.y + dy2 * ratio,
    })
  }

  // 处理最后一个点
  cp1.push({ x: points[n]!.x, y: points[n]!.y })
  cp2.push({ x: points[n]!.x, y: points[n]!.y })

  return { cp1, cp2 }
}

// 用三次贝塞尔曲线绘制平滑轨迹
const drawSmoothTrack = (ctx: CanvasRenderingContext2D, points: CanvasPoint[]) => {
  if (points.length < 2) return

  const { canvasWidth, canvasHeight, lineWidth, lineColor } = canvasOption.value!

  // 绘制轨迹
  ctx.clearRect(0, 0, canvasWidth, canvasHeight) // 清空画布

  const { cp1, cp2 } = getControlPoints(points)

  ctx.beginPath()
  ctx.moveTo(points[0]!.x, points[0]!.y) // 起点

  // 依次绘制三次贝塞尔曲线（cubicBezierCurveTo）
  for (let i = 0; i < points.length - 1; i++) {
    ctx.bezierCurveTo(
      cp1[i + 1]!.x,
      cp1[i + 1]!.y, // 第一个控制点
      cp2[i]!.x,
      cp2[i]!.y, // 第二个控制点
      points[i + 1]!.x,
      points[i + 1]!.y, // 终点
    )
  }

  ctx.strokeStyle = lineColor
  ctx.lineWidth = lineWidth
  ctx.stroke()
}

// 普通绘制轨迹
const drawTrack = (ctx: CanvasRenderingContext2D, points: CanvasPoint[]) => {
  if (points.length < 2) return

  const { canvasWidth, canvasHeight, lineColor, lineWidth, padding } = canvasOption.value!

  // 绘制轨迹
  ctx.clearRect(0, 0, canvasWidth, canvasHeight) // 清空画布

  // 绘制轨迹线
  ctx.beginPath()
  ctx.moveTo(points[0]!.x, points[0]!.y) // 起点
  points.slice(1).forEach((p) => {
    ctx.lineTo(p.x, p.y) // 连接后续点
  })
  ctx.strokeStyle = lineColor
  ctx.lineWidth = lineWidth
  ctx.stroke()

  // 绘制轨迹点（标记经纬度位置）
  // points.forEach((p, index) => {
  //   // 绘制点
  //   ctx.beginPath()
  //   ctx.arc(p.x, p.y, 2, 0, Math.PI * 2)
  //   ctx.fillStyle = index === 0 ? '#e74c3c' : '#3498db' // 起点红色，其他蓝色
  //   ctx.fill()
  // })
}

// 绘制轨迹主函数
const drawGeoTrack = (geoPoints: GeoPoint[]): [string, string] => {
  const canvas = document.getElementById('mapCanvas') as HTMLCanvasElement
  const ctx = canvas!.getContext('2d')!
  ctx.imageSmoothingEnabled = true

  // 设置画布大小（固定尺寸示例，可根据需求调整）
  const { canvasWidth, canvasHeight, padding, simplifiedRatio } = canvasOption.value!
  canvas.width = canvasWidth
  canvas.height = canvasHeight

  // 获取经纬度数据
  if (geoPoints.length < 2) {
    alert('经纬度点不足，无法绘制轨迹')
    return ['', '']
  }

  // 将所有经纬度转换为画布坐标
  // 在drawGeoTrack函数中替换坐标转换部分
  const { convert, centerLng, centerLat } = optimizeCanvasForData(
    geoPoints,
    canvasWidth,
    canvasHeight,
    padding,
  )
  canvas.width = canvasWidth
  canvas.height = canvasHeight

  // Canvas中心（1:1尺寸，中心坐标为(size/2, size/2)）
  const canvasCenterX = canvasWidth / 2
  const canvasCenterY = canvasHeight / 2
  const centerXy = convert(centerLng, centerLat)
  const offsetX = canvasCenterX - centerXy.x
  const offsetY = canvasCenterY - centerXy.y

  let canvasPoints = geoPoints.map((p) => {
    const { x, y } = convert(p.lng, p.lat)
    return {
      x: x + offsetX,
      y: y + offsetY,
    }
  })
  const num1 = canvasPoints.length

  // 简化坐标点
  canvasPoints = simplifyPoints(canvasPoints, simplifiedRatio)
  const num2 = canvasPoints.length
  console.debug(`画布坐标点共${num1}个，简化后共${num2}个`)

  drawTrack(ctx, canvasPoints)
  let base64 = canvas.toDataURL('image/png')
  const blob1 = base64ToBlob(base64)

  drawSmoothTrack(ctx, canvasPoints)
  base64 = canvas.toDataURL('image/png')
  const blob2 = base64ToBlob(base64)

  return [blob1 ? URL.createObjectURL(blob1) : '', blob2 ? URL.createObjectURL(blob2) : '']
}

const defaultOption = {
  besselRatio: 0.25,
  lineColor: '#3498db',
}

const normalUrls = ref<string[]>([])
const besselUrls = ref<string[]>([])

onMounted(async () => {
  canvasOption.value = {
    ...defaultOption,
    canvasWidth: 300,
    canvasHeight: 300,
    padding: 10,
    simplifiedRatio: 1,
    lineWidth: 10,
  }

  const convert = (p: TrackPointType): TrackPointType => ({ ...p, ...wgs84ToGcj02(p.lng, p.lat) })

  const res = await Promise.all([
    parseTcxFile('/data/13238395397.tcx').then((r) => r.trackPoints),
    parseTcxFile('/data/13265099379.tcx').then((r) => r.trackPoints),
    loadYpx('/data/1023642168.ypx').then((r) => r.map(convert)),
    loadYpx('/data/1043960695.ypx').then((r) => r.map(convert)),
  ])

  res.forEach((r) => {
    // 执行绘制
    const [normalUrl, besselUrl] = drawGeoTrack(r)
    normalUrls.value.push(normalUrl)
    besselUrls.value.push(besselUrl)
  })
})
</script>

<style scoped>
.page-container {
  width: 100vw;
  min-height: 100vh;
  background-color: #fff;
  position: relative;
  overflow-x: hidden;
}

.row {
  display: flex;
  width: 100%;
  padding: 10px;
}

.col {
  flex: 1;
  height: auto;
}

img {
  display: block;
  width: 50px;
  height: 50px;
}

canvas {
  position: absolute;
  left: 100%;
  top: 0;
}
</style>
