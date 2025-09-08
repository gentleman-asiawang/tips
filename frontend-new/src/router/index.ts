import { createRouter, createWebHistory } from 'vue-router'
import Home from '@/views/Home.vue';
import AboutAndContact from '@/views/AboutAndContact.vue';
import Tutorial from '@/views/Tutorial.vue';

import VarsInRegion from '@/views/VarsInRegion.vue';
import VarsInGene from '@/views/VarsInGene.vue';
import VarsGenotype from '@/views/VarsGenotype.vue';
import VarsInfo from '@/views/VarsInfo.vue';
import TwoCultivarsCompare from '@/views/TwoCultivarsCompare.vue';

import Blastn from '@/views/Blastn.vue';
import Jbrowse from '@/views/Jbrowse.vue';

import AccessionInfo from '@/views/AccessionInfo.vue';
import VariantDetail from '@/components/VariantDetail.vue';
import AccessionDetail from '@/components/AccessionDetail.vue';
import DevelopNotes from '@/views/DevelopNotes.vue';

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: Home,
    },
    {
      path: '/vars_in_region',
      name: 'vars_in_region',
      component: VarsInRegion,
    },
    {
      path: '/vars_in_gene',
      name: 'vars_in_gene',
      component: VarsInGene,
    },
    {
      path: '/vars_genotype',
      name: 'vars_genotype',
      component: VarsGenotype,
    },
    {
      path: '/vars_info',
      name: 'vars_info',
      component: VarsInfo,
    },
    {
      path: '/two_cultivars_compare',
      name: 'two_cultivars_compare',
      component: TwoCultivarsCompare,
    },
    {
      path: '/blastn',
      name: 'blastn',
      component: Blastn,
    },
    {
      path: '/jbrowse',
      name: 'jbrowse',
      component: Jbrowse,
    },
    {
      path: '/accession_info',
      name: 'accession_info',
      component: AccessionInfo,

    },
    {
      path: '/about_contact',
      name: 'about_contact',
      component: AboutAndContact,
    },
    {
      path: '/tutorial',
      name: 'tutorial',
      component: Tutorial,
    },
    {
      path: '/develop_notes',
      name: 'develop_notes',
      component: DevelopNotes,
    },
    {
      path: '/:source/:target',
      name: 'VariantDetail',
      component: VariantDetail,
      props: true
    },
    {
      path: '/accession_detail/:sample_id',
      name: 'accession_detail',
      component: AccessionDetail,
      props: true
    },
  ],
})

export default router
