<template>
  <el-backtop :right="30" :bottom="50" />
  <el-scrollbar style="min-width: 0;">
    <h2 class="dot-heading">Density</h2>
    <Density />
  </el-scrollbar>
</template>

<script lang="ts" setup>
import Density from '@/components/Density.vue';
import { getLogger } from '@/utils/logger';

const log = getLogger('Home.vue'); // 当前组件名
log.setLevel('debug'); // 只打开这个组件的调试日志
</script>

<style scoped>
.info-text {
  max-width: 1100px;
  text-align: justify;
  font-family: "Helvetica", Times, Sans-serif;
  font-size: 22px;
  line-height: 1.4;
  margin-top: 1px;
  margin-bottom: 10px;
}




</style>