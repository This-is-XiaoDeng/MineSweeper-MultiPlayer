import { createRouter, createMemoryHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import PrepareView from '../views/PrepareView.vue'
import GameView from '@/views/GameView.vue'

const router = createRouter({
  history: createMemoryHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    {
      path: '/prepare',
      name: 'prepare',
      component: PrepareView,
    },
    {
      path: '/game',
      name: 'game',
      component: GameView,
    },
    {
      path: '/about',
      name: 'about',
      // route level code-splitting
      // this generates a separate chunk (About.[hash].js) for this route
      // which is lazy-loaded when the route is visited.
      component: () => import('../views/AboutView.vue'),
    },
  ],
})

export default router
