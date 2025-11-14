import AMapRoutes from './amap/route'
import BMapRoutes from './baidu-map/route'
import RunRoutes from './run/route'

const pages = [
  // 高德地图DEMO
  ...AMapRoutes,
  // 百度地图DEMO
  ...BMapRoutes,
  // 跑步轨迹
  ...RunRoutes,
]

export { pages }
