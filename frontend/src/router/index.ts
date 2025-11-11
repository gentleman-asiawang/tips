import { createRouter, createWebHistory } from 'vue-router'
import Home from '@/views/Home.vue';
import Byseq from '@/views/Byseq.vue';
import Bystr from '@/views/Bystr.vue';
import Visualize from '@/views/Visualize.vue';
import Phylogeny from '@/views/Phylog.vue';
import Download from '@/views/Download.vue';
import About from '@/views/About.vue';

import Viewtree from '@/components/Viewtree.vue';
import Viewstr from '@/components/Viewstr.vue';
import NotFound from '@/views/NotFound.vue'; // 404 页面组件

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
      path: '/bystructure',
      component: Bystr,
      name: 'Bystr'
    },
    { 
      path: '/visualize',
      component: Visualize,
      name: 'Visualize'
    },
    { 
      path: '/download',
      component: Download,
      name: 'Download'
    },
    {
      path: '/about',
      name: 'about',
      component: About,
    },
    { 
      path: '/phylogeny',
      component: Phylogeny,
      name: 'Phylogeny'
    },
    { 
      path: '/phylogeny/:treeuuid',
      component: Viewtree,
      name: 'Viewtree',
      props: true 
    },
    {
      path: '/:source/:target',
      name: 'Viewstr',
      component: Viewstr,
      props: true
    },
    { 
      path: '/404',
      component: NotFound,
      name: 'NoPage404'
    },
    { 
      path: '/:pathMatch(.*)*',
      redirect: '/404'
    }
  ],
})

// 全局前置守卫
router.beforeEach((to, from, next) => {
  // 检查如果是根路径，则允许继续
  if (to.path === '/') {
    next(); // 继续访问根路径
  } else {
    // 如果不是根路径且用户在刷新，重定向到根路径
    if (from.name === undefined) { // from.name 为 null 表示用户是从浏览器刷新进来的
      next('/'); // 跳转到根路径
    } else {
      next(); // 继续访问其他页面
    }
  }
});

export default router
