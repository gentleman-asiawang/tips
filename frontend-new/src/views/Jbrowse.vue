<template>
  <el-page-header v-if="source" v-on:back="goBack" style="margin-bottom: 5px;margin-left: 10px;margin-right: 10px;">
    <template #content>
      <span class="header-text"><b>Variant ID:</b> {{ varid }}</span>
    </template>
  </el-page-header>
  <div class="jbrowse-wrapper">
    <j-browse :defaultLoc="defaultLoc" />
  </div>

</template>

<script setup lang="ts">
import JBrowse from '@/components/JbrowseModule.vue';
import { useRouter } from 'vue-router';
import { computed } from 'vue';

const router = useRouter();

const defaultLoc = computed(() => router.currentRoute.value.query.loc || 'chr1:1..308,452,471');
const varid = computed(() => router.currentRoute.value.query.variantid);

const source = computed(() => router.currentRoute.value.query.source);

// back to previous page
function goBack() {
  router.push(`/${source.value}/${varid.value}`)
}
</script>