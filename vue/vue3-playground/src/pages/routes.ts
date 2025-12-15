import AMapRoutes from './amap/route'
import BMapRoutes from './baidu-map/route'
import CustomRoutes from './custom/route'
import RunRoutes from './run/route'
import VantRoutes from './vant/route'

const pages = [
  // 高德地图DEMO
  ...AMapRoutes,
  // 百度地图DEMO
  ...BMapRoutes,
  // 跑步轨迹
  ...RunRoutes,
  // VantUI库
  ...VantRoutes,
  ...CustomRoutes,
]

export { pages }
