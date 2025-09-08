<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue';
import { useUuidStore } from '@/stores/uuid';
import { useSamplesinfoStore, usePopulationsStore } from '@/stores/baseinfo';
import axios from 'axios';
import { getLogger } from '@/utils/logger';
const log = getLogger('App.vue'); // 当前组件名
log.setLevel('debug');

const uuidStore = useUuidStore();
const samplesinfoStore = useSamplesinfoStore()
const populationsStore = usePopulationsStore();
const fullscreenLoading = ref(true);


const activeIndex = ref('/');

const handleSelect = (index: string) => {
  log.debug('Menu selected:', index);
};


// use sendBeacon sent remove file request
const handleWindowClose = () => {
  log.debug('Window is closing, sending UUID to server');
  const data = new FormData();
  data.append('uuid', uuidStore.uuid);  // Use FormData to build request data
  navigator.sendBeacon('/maizevarmap_api/logout/', data);
};

// sent uuid to server
const sendUUIDToServer = async (uuid: string) => {
  try {
    const response = await axios.post('/maizevarmap_api/login/', { uuid });
    log.debug('Server response:', response.data);
  } catch (error) {
    log.error('Failed to send UUID:', error);
  }
};

onMounted(async () => {
  try {
    window.addEventListener('beforeunload', handleWindowClose);
    uuidStore.generateUuid();
    await sendUUIDToServer(uuidStore.uuid);
    await samplesinfoStore.querySampleinfo(uuidStore.uuid);
    await populationsStore.queryPopulationsInfo(uuidStore.uuid);
  } catch (error) {
    log.error('Error loading orders:', error);
  } finally {
    fullscreenLoading.value = false; // 设置加载状态为 false
  }
});

// remove listener
onBeforeUnmount(() => {
  window.removeEventListener('beforeunload', handleWindowClose);
});

</script>

<template>
  <div v-if="fullscreenLoading" v-loading.fullscreen.lock="fullscreenLoading"></div>
  <div v-else>
    <el-container style="height: 100vh; display: flex; flex-direction: column;">
      <el-header>
        <el-menu class="center-menu" :default-active="activeIndex" mode="horizontal" @select="handleSelect"
          popper-effect="light" :ellipsis="false" :router="true"
          style="border: 0; top: 0; left: 0; width: 100%; z-index: 1000;">
          <el-menu-item index="/"><font-awesome-icon icon="fa-solid fa-house" /><span
              style="margin-left: 8px;">Home</span></el-menu-item>
          <el-sub-menu index="/2">
            <template #title><span class="menu-item-text">Search</span></template>
            <el-menu-item index="/vars_in_region">Search for Variations by Region</el-menu-item>
            <el-menu-item index="/vars_in_gene">Search for Variations in Gene</el-menu-item>
            <el-menu-item index="/vars_genotype">Search for Genotype With Variation ID</el-menu-item>
            <el-menu-item index="/vars_info">Search for Variation Information with Variation ID</el-menu-item>
            <el-menu-item index="/two_cultivars_compare">Search for Polymorphic Positions Between Two
              Cultivars</el-menu-item>
          </el-sub-menu>
          <el-sub-menu index="/3">
            <template #title><span class="menu-item-text">Tools</span></template>
            <el-menu-item index="/blastn">Blast</el-menu-item>
            <el-menu-item index="/jbrowse">Jbrowse</el-menu-item>
          </el-sub-menu>
          <el-sub-menu index="/document">
            <template #title><span class="menu-item-text">Document</span></template>
            <el-menu-item index="/accession_info">Accession Info</el-menu-item>
            <el-menu-item index="/tutorial">Tutorial</el-menu-item>
            <el-menu-item index="/develop_notes">Development Notes</el-menu-item>
          </el-sub-menu>

          <el-menu-item index="/about_contact">About & Contact</el-menu-item>

        </el-menu>

        <!-- <el-switch v-model="isDark" inline-prompt @change="toggleDark()" :active-action-icon="Moon" -->
        <!-- :inactive-action-icon="Sunny" /> -->
      </el-header>
      <el-main style="flex-grow: 1;">
        <!-- 夜间模式切换 -->
        <!-- <button @click="toggleDark()">
          当前状态是: {{ isDark }}
        </button> -->
        <div class="container">
          <router-view v-slot="{ Component }">
            <keep-alive>
              <component :is="Component" />
            </keep-alive>
          </router-view>
        </div>

      </el-main>
      <el-footer style="flex-shrink: 0;">Henan Agricultural University</el-footer>
    </el-container>


  </div>
</template>

<style scoped>
/* 调整 el-header 的样式，确保没有内边距或外边距影响布局 */
.el-header {
  padding: 0;
  margin: 0;
}

/* 调整 el-menu 的样式，字体、粗细等 */
.el-menu {
  display: flex;
  justify-content: center;
  gap: 20px;
}

.el-menu>.el-menu-item,
.el-menu>.el-sub-menu .menu-item-text {
  font-size: 20px;
  /* 设置你需要的字体大小 */
  font-weight: bolder;
}

.el-menu--horizontal>.el-menu>.el-menu-item {
  font-size: 15px !important;
  font-weight: normal !important;
}

.el-footer {
  background-color: #58aa81;
  padding: 10px 0;
}

.container {
  justify-content: center;
  box-sizing: border-box;
  max-width: 1300px;
  text-align: left;
  line-height: 1.4;
  padding-top: 0px;
  margin: 0 auto;
}
</style>
