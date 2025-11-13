import AMapRoutes from './amap/route'
import RunRoutes from './run/route'

const pages = [
  // 高德地图DEMO
  ...AMapRoutes,
  // 跑步轨迹
  ...RunRoutes,
]

export { pages }
