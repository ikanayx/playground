import type { RouteRecordRaw } from 'vue-router'

export default [
  {
    path: '/map/amap',
    name: 'MapAMapDemoPage',
    // component: AMapDemoPage,
    // route level code-splitting
    // this generates a separate chunk (About.[hash].js) for this route
    // which is lazy-loaded when the route is visited.
    component: () => import('./index.vue'),
    meta: {
      title: '地图 | 高德地图DEMO',
      allowAnonymous: true,
    },
  },
] as Array<RouteRecordRaw>
