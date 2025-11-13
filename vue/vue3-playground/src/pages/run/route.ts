import type { RouteRecordRaw } from 'vue-router'

export default [
  {
    path: '/run/canvasTrack',
    name: 'RunCanvasDrawTrack',
    component: () => import('./CanvasTrack.vue'),
    meta: {
      title: 'Canvas跑步轨迹',
      allowAnonymous: true,
    },
  },
] as Array<RouteRecordRaw>
