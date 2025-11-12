import PageNavigator from '@/pages/common/PageNavigator.vue'
import PageNotFound from '@/pages/common/PageNotFound.vue'
import { pages } from '@/pages/routes'
import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'HomePage',
      redirect: '/navigator',
    },
    ...pages,
    {
      path: '/navigator',
      name: 'DevRouteNavigator',
      component: PageNavigator,
    },
    {
      path: '/404',
      name: 'PageNotFound',
      component: PageNotFound,
    },
    // 通配符路由放在最后，仅匹配未定义的路由
    {
      path: '/:pathMatch(.*)*',
      redirect: '/404',
    },
  ],
})

export default router
