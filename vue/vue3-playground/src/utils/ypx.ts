import { wgs84ToGcj02 } from './coordinate'
import type { TrackPointType } from './tcx'

export async function loadYpx(ypxUrl: string) {
  // 1. 下载 JSON 文件
  const response = await fetch(ypxUrl)
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`)
  }
  let jsonText = await response.text()
  if (jsonText.startsWith('"')) {
    jsonText = jsonText.substring(1)
  }
  if (jsonText.endsWith('"')) {
    jsonText = jsonText.substring(0, jsonText.length - 1)
  }
  const array = jsonText.split('-')
  const points = [] as TrackPointType[]
  for (let i = 0; i < array.length; i += 2) {
    const point = JSON.parse(array[i]!) as number[]
    const { lng, lat } = wgs84ToGcj02(point[1]! / 1000000, point[0]! / 1000000)
    points.push({
      lng,
      lat,
      time: null,
      distanceMeters: null,
      speed: null,
      cadence: null,
      heartRate: null,
      pace: null,
    })
  }
  console.debug(`ypx运动共加载了${points.length}个点`)
  return points
}
