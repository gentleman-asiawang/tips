import { createRouter, createWebHistory } from 'vue-router'
import Home from '@/views/Home.vue';
import Byseq from '@/views/Byseq.vue';
import About from '@/views/About.vue';

import Viewstr from '@/components/Viewstr.vue';

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: Home,
    },
    {
      path: '/bysequence',
      name: 'Byseq',
      component: Byseq,
    },
    {
      path: '/about',
      name: 'about',
      component: About,
    },
    {
      path: '/:source/:target',
      name: 'Viewstr',
      component: Viewstr,
      props: true
    }
  ],
})

export default router
