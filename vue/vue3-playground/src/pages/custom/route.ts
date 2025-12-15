import type { RouteRecordRaw } from 'vue-router'

export default [
  {
    path: '/custom/roll',
    name: 'RollComponent',
    // component: AMapDemoPage,
    // route level code-splitting
    // this generates a separate chunk (About.[hash].js) for this route
    // which is lazy-loaded when the route is visited.
    component: () => import('./roll.vue'),
    meta: {
      title: '环绕 | 自定义组件',
      allowAnonymous: true,
    },
  },
] as Array<RouteRecordRaw>
