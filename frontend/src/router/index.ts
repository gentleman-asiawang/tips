import { createRouter, createWebHistory } from 'vue-router';
import Home from '~/components/Home.vue';
import About from '~/components/About.vue';
import Download from '~/components/Download.vue';
import Visualize from '~/components/Visualize.vue'; //如果提示报错则可能是因为名字太长导致
import Byseq from '~/components/Byseq.vue';
import Bystr from '~/components/Bystr.vue';
import Viewstr from '~/components/Viewstr.vue';
import Viewtree from '~/components/Viewtree.vue';
import Phylogeny from '~/components/Phylog.vue';
import NotFound from '~/components/NotFound.vue'; // 404 页面组件

const routes = [
  { path: '/', component: Home, name: 'Home' },
  { path: '/bysequence', component: Byseq, name: 'Byseq' },
  { path: '/bystructure', component: Bystr, name: 'Bystr' },
  { path: '/visualize', component: Visualize, name: 'Visualize' },
  { path: '/download', component: Download, name: 'Download' },
  { path: '/about', component: About, name: 'About' },
  { path: '/phylogeny', component: Phylogeny, name: 'Phylogeny' },
  { path: '/:source/:target', component: Viewstr, name: 'Viewstr', props: true },
  { path: '/phylogeny/:treeuuid', component: Viewtree, name: 'Viewtree', props: true },
  { path: '/404', component: NotFound, name: 'NoPage404', hidden: true },
  { path: '/:pathMatch(.*)*', redirect: '/404', hidden: true },
];

const router = createRouter({
  history: createWebHistory(), // 启用 HTML5 历史模式
  routes,
});

// 全局前置守卫
router.beforeEach((to, from, next) => {
  // 检查如果是根路径，则允许继续
  if (to.path === '/') {
    next(); // 继续访问根路径
  } else {
    console.log('not to root')
    console.log(from.name)
    // 如果不是根路径且用户在刷新，重定向到根路径
    if (from.name === undefined) { // from.name 为 null 表示用户是从浏览器刷新进来的
      console.log('web fresh')
      next('/'); // 跳转到根路径
    } else {
      next(); // 继续访问其他页面
    }
  }
});

export default router;