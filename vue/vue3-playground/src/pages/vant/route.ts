import type { RouteRecordRaw } from 'vue-router'

export default [
  {
    path: '/vant/area',
    name: 'VantAreaDemo',
    component: () => import('./area.vue'),
    meta: {
      title: '省市区组件 | Vant',
      allowAnonymous: true,
    },
  },
] as Array<RouteRecordRaw>
