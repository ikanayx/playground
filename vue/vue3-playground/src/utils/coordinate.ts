import type { TrackPointType } from './tcx'

const a = 6378245.0
const ee = 0.00669342162296594323

/**
 * WGS84 (GPS 坐标) 转 GCJ-02 (火星坐标)
 * @param {number} lng WGS84 经度
 * @param {number} lat WGS84 纬度
 * @returns {object} 包含 GCJ-02 经纬度的对象
 */
export function wgs84ToGcj02(lng: number, lat: number): { lng: number; lat: number } {
  if (outOfChina(lng, lat)) {
    return { lng: lng, lat: lat }
  }
  let deltaLat = transformLat(lng - 105.0, lat - 35.0)
  let deltaLng = transformLng(lng - 105.0, lat - 35.0)
  const radLat = (lat / 180.0) * Math.PI
  let magic = Math.sin(radLat)
  magic = 1 - ee * magic * magic
  const sqrtMagic = Math.sqrt(magic)
  deltaLat = (deltaLat * 180.0) / (((a * (1 - ee)) / (magic * sqrtMagic)) * Math.PI)
  deltaLng = (deltaLng * 180.0) / ((a / sqrtMagic) * Math.cos(radLat) * Math.PI)
  const mergeLng = lng + deltaLng
  const mergeLat = lat + deltaLat
  return { lng: mergeLng, lat: mergeLat }
}

/**
 * WGS84转BD09坐标系
 * @param wgs84 WGS84坐标点 {lng: 经度, lat: 纬度}
 * @returns BD09坐标点 {lng: 经度, lat: 纬度}
 */
export function wgs84ToBd09(lng: number, lat: number): { lng: number; lat: number } {
  // 先将WGS84转换为GCJ02
  const gcj02 = wgs84ToGcj02(lng, lat)
  // 再将GCJ02转换为BD09
  return gcj02ToBd09(gcj02)
}

/**
 * GCJ02转BD09坐标系
 * @param gcj02 GCJ02坐标点
 * @returns BD09坐标点
 */
export function gcj02ToBd09(gcj02: { lng: number; lat: number }): { lng: number; lat: number } {
  const x_pi = (Math.PI * 3000.0) / 180.0
  const { lng: lng, lat: lat } = gcj02
  const x = lng
  const y = lat
  const z = Math.sqrt(x * x + y * y) + 0.00002 * Math.sin(y * x_pi)
  const theta = Math.atan2(y, x) + 0.000003 * Math.cos(x * x_pi)

  return {
    lng: z * Math.cos(theta) + 0.0065,
    lat: z * Math.sin(theta) + 0.006,
  }
}

/**
 * 使用高德接口批量转换坐标
 * 慎用，量大的时候直接卡死
 * @param lnglatArray 坐标数组
 * @returns gcj02坐标系的坐标
 */
export function wgs84ToGcj02_amap(lnglatArray: number[][]) {
  return new Promise<AMap.LngLat[]>((resolve, reject) => {
    AMap.convertFrom(
      lnglatArray,
      'gps',
      function (status: string, result: { info: string; locations: AMap.LngLat[] }) {
        //status：complete 表示查询成功，no_data 为查询无结果，error 代表查询错误
        //查询成功时，result.locations 即为转换后的高德坐标系
        if (status === 'complete' && result.info === 'ok') {
          resolve(result.locations)
        } else if (status === 'error' || result.info !== 'ok') {
          reject(new Error(`坐标转换失败, status=${status}, result=${JSON.stringify(result)}`))
        }
      },
    )
  })
}

/**
 * 判断是否在中国
 * @param {number} lng 经度
 * @param {number} lat 纬度
 * @returns {boolean} true 如果在中国，否则 false
 */
function outOfChina(lng: number, lat: number): boolean {
  return lng < 72.004 || lng > 137.8347 || lat < 0.8293 || lat > 55.8271 || false
}

function transformLat(lng: number, lat: number) {
  lat = +lat
  lng = +lng
  let ret =
    -100.0 +
    2.0 * lng +
    3.0 * lat +
    0.2 * lat * lat +
    0.1 * lng * lat +
    0.2 * Math.sqrt(Math.abs(lng))
  ret += ((20.0 * Math.sin(6.0 * lng * Math.PI) + 20.0 * Math.sin(2.0 * lng * Math.PI)) * 2.0) / 3.0
  ret += ((20.0 * Math.sin(lat * Math.PI) + 40.0 * Math.sin((lat / 3.0) * Math.PI)) * 2.0) / 3.0
  ret +=
    ((160.0 * Math.sin((lat / 12.0) * Math.PI) + 320 * Math.sin((lat * Math.PI) / 30.0)) * 2.0) /
    3.0
  return ret
}

function transformLng(lng: number, lat: number) {
  lat = +lat
  lng = +lng
  let ret =
    300.0 + lng + 2.0 * lat + 0.1 * lng * lng + 0.1 * lng * lat + 0.1 * Math.sqrt(Math.abs(lng))
  ret += ((20.0 * Math.sin(6.0 * lng * Math.PI) + 20.0 * Math.sin(2.0 * lng * Math.PI)) * 2.0) / 3.0
  ret += ((20.0 * Math.sin(lng * Math.PI) + 40.0 * Math.sin((lng / 3.0) * Math.PI)) * 2.0) / 3.0
  ret +=
    ((150.0 * Math.sin((lng / 12.0) * Math.PI) + 300.0 * Math.sin((lng / 30.0) * Math.PI)) * 2.0) /
    3.0
  return ret
}

/**
 * 计算两个GPS坐标点之间的距离（使用Haversine公式）
 * 使用示例
 * const distance = calculateDistance(52.5200, 13.4050, 48.8566, 2.3522); // 柏林到巴黎
 * console.log(distance); // 输出大约878060米（878公里）
 * @param {number} lat1 - 第一个点的纬度（度）
 * @param {number} lon1 - 第一个点的经度（度）
 * @param {number} lat2 - 第二个点的纬度（度）
 * @param {number} lon2 - 第二个点的经度（度）
 * @returns {number} 两点之间的距离（米）
 */
export function calculateDistance(lat1: number, lon1: number, lat2: number, lon2: number): number {
  // 地球半径（米）
  const R = 6371e3

  // 将度转换为弧度
  const φ1 = (lat1 * Math.PI) / 180
  const φ2 = (lat2 * Math.PI) / 180
  const Δφ = ((lat2 - lat1) * Math.PI) / 180
  const Δλ = ((lon2 - lon1) * Math.PI) / 180

  // Haversine公式
  const a =
    Math.sin(Δφ / 2) * Math.sin(Δφ / 2) +
    Math.cos(φ1) * Math.cos(φ2) * Math.sin(Δλ / 2) * Math.sin(Δλ / 2)
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))

  // 计算距离
  const distance = R * c

  return distance
}

/**
 * 简化坐标点数量
 * @param points 经纬度坐标点
 * @param min 最小距离，默认1米
 */
export function simplify(points: TrackPointType[], min: number = 1): TrackPointType[] {
  const simplified = [] as TrackPointType[]
  let last = 0
  simplified.push(points[last]!)
  for (let i = 1; i < points.length; i++) {
    const meter = calculateDistance(
      points[last]!.lat,
      points[last]!.lng,
      points[i]!.lat,
      points[i]!.lng,
    )
    if (meter < min) continue
    last = i
    simplified.push(points[last]!)
  }
  console.debug(`简化后点数量为:${simplified.length}`)
  return simplified
}

/**
 * 轨迹抽稀算法 (Douglas-Peucker简化算法)
 * @param {Array} track 轨迹点数组
 * @param {Number} epsilon 抽稀阈值
 * @returns {Array} 抽稀后的轨迹
 */
export function simplifyDouglas(track: number[][], epsilon: number): number[][] {
  if (track.length <= 2) return track

  // 计算点到线段的距离
  const distance = (p: number[], a: number[], b: number[]) => {
    const [x, y] = [p[0]!, p[1]!]
    const [x1, y1] = [a[0]!, a[1]!]
    const [x2, y2] = [b[0]!, b[1]!]
    const A = x - x1
    const B = y - y1
    const C = x2 - x1
    const D = y2 - y1
    const dot = A * C + B * D
    const lenSq = C * C + D * D
    let param = -1
    if (lenSq !== 0) param = dot / lenSq
    let xx, yy
    if (param < 0) {
      xx = x1
      yy = y1
    } else if (param > 1) {
      xx = x2
      yy = y2
    } else {
      xx = x1 + param * C
      yy = y1 + param * D
    }
    const dx = x - xx
    const dy = y - yy
    return Math.sqrt(dx * dx + dy * dy)
  }

  // 找到最大距离点
  let maxDist = 0
  let index = 0
  const end = track.length - 1

  for (let i = 1; i < end; i++) {
    const dist = distance(track[i]!, track[0]!, track[end]!)
    if (dist > maxDist) {
      maxDist = dist
      index = i
    }
  }

  // 递归简化
  let result = [] as number[][]
  if (maxDist > epsilon) {
    const left = simplifyDouglas(track.slice(0, index + 1), epsilon)
    const right = simplifyDouglas(track.slice(index), epsilon)
    result = left.slice(0, -1).concat(right)
  } else {
    result = [track[0]!, track[end]!]
  }

  return result
}
