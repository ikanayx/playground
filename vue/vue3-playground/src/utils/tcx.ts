import { calculateDistance } from './coordinate'

export interface TrackPointType {
  time: string | null
  lat: number
  lng: number
  distanceMeters: number | null
  speed: number | null
  cadence: number | null
  heartRate: number | null
  pace: number | null
}

/**
 * 解析 TCX 文件并提取 GPS 坐标和速度/配速数据
 * @param {string} tcxUrl - TCX 文件的 HTTP 链接
 * @returns {Promise<Object>} 包含解析后数据的 Promise 对象
 */
export async function parseTcxFile(
  tcxUrl: string,
): Promise<{ activityType: string; trackPoints: TrackPointType[] }> {
  try {
    // 1. 下载 TCX 文件
    const response = await fetch(tcxUrl)
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    const tcxText = await response.text()

    // 2. 解析 XML 数据
    const parser = new DOMParser()
    const xmlDoc = parser.parseFromString(tcxText, 'text/xml')

    // 3. 检查解析错误
    const parserErrors = xmlDoc.getElementsByTagName('parsererror')
    if (parserErrors.length > 0) {
      throw new Error('Error parsing TCX file')
    }

    // 4. 提取轨迹点数据
    const trackPoints = xmlDoc.getElementsByTagName('Trackpoint')
    const activities = xmlDoc.getElementsByTagName('Activity')
    const activityType =
      activities.length > 0 ? activities[0]!.getAttribute('Sport') || 'unknown' : 'unknown'

    const result = {
      activityType: activityType,
      trackPoints: [] as TrackPointType[],
    }

    // 5. 遍历所有轨迹点
    for (let i = 0; i < trackPoints.length; i++) {
      const point = trackPoints[i]!
      const timeElem = point.getElementsByTagName('Time')[0]
      const positionElem = point.getElementsByTagName('Position')[0]
      const distanceElem = point.getElementsByTagName('DistanceMeters')[0]
      let speedElem = point.getElementsByTagName('Speed')[0]
      const cadenceElem = point.getElementsByTagName('Cadence')[0]
      const heartRateElem = point.getElementsByTagName('HeartRateBpm')[0]

      if (speedElem === undefined || speedElem === null) {
        const ext = point.getElementsByTagName('Extensions')[0]
        if (ext) {
          const ns3tpx = ext.getElementsByTagName('ns3:TPX')[0]
          if (ns3tpx) {
            speedElem = ns3tpx.getElementsByTagName('ns3:Speed')[0] // 米/秒
          }
        }
      }

      // 只有包含位置数据的点才处理
      if (positionElem) {
        const latitudeElem = positionElem.getElementsByTagName('LatitudeDegrees')[0]!
        const longitudeElem = positionElem.getElementsByTagName('LongitudeDegrees')[0]!

        const trackPoint = {
          time: timeElem?.textContent ? timeElem.textContent : null,
          lat: parseFloat(latitudeElem.textContent!),
          lng: parseFloat(longitudeElem.textContent!),
          distanceMeters: distanceElem?.textContent ? parseFloat(distanceElem.textContent) : null,
          speed: speedElem?.textContent ? parseFloat(speedElem.textContent) : null,
          cadence: cadenceElem?.textContent ? parseInt(cadenceElem.textContent) : null,
          heartRate: heartRateElem?.textContent ? parseInt(heartRateElem.textContent) : null,
          pace: 10, // 默认12分配
        }

        // 计算配速 (分钟/公里)，仅适用于跑步活动
        if (activityType.toLowerCase() === 'run' && trackPoint.speed && trackPoint.speed > 0) {
          trackPoint.pace = 1000 / 60 / trackPoint.speed // 转换为分钟/公里
        }

        result.trackPoints.push(trackPoint)
      }
    }

    // 6. 计算缺失的速度数据（如果原始文件没有提供）
    if (result.trackPoints.length > 1) {
      for (let i = 1; i < result.trackPoints.length; i++) {
        const prevPoint = result.trackPoints[i - 1]!
        const currPoint = result.trackPoints[i]!

        // 如果原始数据没有速度，但有时间差和距离差，则计算速度
        if (currPoint.speed === null && prevPoint.time && currPoint.time) {
          try {
            const timeDiff =
              (new Date(currPoint.time).getTime() - new Date(prevPoint.time).getTime()) / 1000 // 秒

            let distanceDiff // 米
            if (prevPoint.distanceMeters !== null && currPoint.distanceMeters !== null) {
              distanceDiff = currPoint.distanceMeters - prevPoint.distanceMeters
            } else {
              distanceDiff = calculateDistance(
                prevPoint.lat,
                prevPoint.lng,
                currPoint.lat,
                currPoint.lng,
              )
            }

            if (timeDiff > 0 && distanceDiff >= 0) {
              currPoint.speed = distanceDiff / timeDiff // 米/秒

              // 如果是跑步活动，计算配速
              if (activityType.toLowerCase() === 'run') {
                currPoint.pace = 1000 / 60 / currPoint.speed // 分钟/公里
              }
            }
          } catch (e) {
            console.warn(`Error calculating speed between points ${i - 1} and ${i}:`, e)
          }
        }
      }
    }

    return result
  } catch (error) {
    console.error('Error parsing TCX file:', error)
    throw error
  }
}

// 使用示例
// parseTcxFile("https://example.com/activity.tcx")
//   .then(data => console.log(data))
//   .catch(error => console.error(error));
