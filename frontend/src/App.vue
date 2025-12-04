<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue';
import { useUuidStore } from '@/stores/uuid';
import { useInfoStore } from '@/stores/info';
import axios from 'axios';
import { ElMessage } from 'element-plus';

import { getLogger } from '@/utils/logger';
const log = getLogger('App.vue'); // 当前组件名
log.setLevel('info');

const uuidStore = useUuidStore();
const infoStore = useInfoStore();
const fullscreenLoading = ref(true);


const activeIndex = ref('/');

const handleSelect = (index: string) => {
  log.debug('Menu selected:', index);
};


// use sendBeacon sent remove file request
const handleWindowClose = () => {
  log.debug('Window is closing, sending UUID to server');
  const body = new URLSearchParams({ uuid: uuidStore.uuid }).toString();
  navigator.sendBeacon('/tips_api/delete_all_temp_files/', new Blob([body], { type: 'application/x-www-form-urlencoded' }));
};

// sent uuid to server
const sendUUIDToServer = async (uuid: string) => {
  try {
    const response = await axios.post('/tips_api/login/', { uuid });
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
    await infoStore.fetchOrders();
  } catch (error) {
    console.error('Error loading orders or sending UUID:', error);
    ElMessage.error({
      message: 'Can not connect server !!!',
      duration: 0,
      type: 'success',
    })
    ElMessage.error({
      message: 'Please check your network or contact us',
      duration: 0,
      type: 'success',
    })
  } finally {
    fullscreenLoading.value = false; // 设置加载状态为 false
  }
});

// remove listener
onBeforeUnmount(() => {
  window.removeEventListener('unload', handleWindowClose);
});

</script>

<template>
  <div v-if="fullscreenLoading" v-loading.fullscreen.lock="fullscreenLoading"></div>
  <div v-else>
    <el-container style="height: 100vh; display: flex; flex-direction: column;">
      <el-header>
        <el-menu class="center-menu" :default-active="activeIndex" mode="horizontal" @select="handleSelect"
          popper-effect="light" :ellipsis="false" :router="true"
          style="border: 0; top: 0; left: 0; width: 100%; z-index: 1000; background-color: #ffffff; justify-content: center;">
          <el-menu-item index="/"><span>Home</span></el-menu-item>
          <el-sub-menu index="/2">
            <template #title><span class="menu-item-text">Search</span></template>
            <el-menu-item index="/bysequence">by sequence</el-menu-item>
            <el-menu-item index="/bystructure">by structure</el-menu-item>
          </el-sub-menu>
          <el-menu-item index="/visualize" class="menu-item"><span
              class="menu-item-text">Visualize</span></el-menu-item>
          <el-menu-item index="/phylogeny" class="menu-item"><span
              class="menu-item-text">Phylogeny</span></el-menu-item>
          <el-menu-item index="/download" class="menu-item"><span class="menu-item-text">Download</span></el-menu-item>
          <el-menu-item index="/about" class="menu-item"><span class="menu-item-text">About</span></el-menu-item>
        </el-menu>
      </el-header>
      <el-main style="flex-grow: 1;padding-top: 0;">
        <router-view v-slot="{ Component }">
          <keep-alive>
            <component :is="Component" />
          </keep-alive>
        </router-view>
      </el-main>
    </el-container>
  </div>
</template>

<style scoped>
/* Center the menu */
.el-menu {
  display: flex;
  justify-content: center;
  /* Centers the menu items */
  gap: 0px;
  /* Adds spacing between the menu items */
}

.el-menu-item {
  padding: 0 15px;
  /* Optional padding to make the menu items more spacious */
}

.menu-item-text {
  font-size: 25px !important;
  /* Ensure the text is the same size */
  font-family: "Helvetica", Times, Sans-serif;
  font-weight: bold;
}

.el-header {
  padding: 0;
  margin: 0;
}

.el-menu>.el-menu-item,
.el-menu>.el-sub-menu .menu-item-text {
  font-size: 25px;
  font-family: "Helvetica", Times, Sans-serif;
  font-weight: bold;
}

.el-menu--horizontal {
  --el-menu-horizontal-height: 60px;
}

.el-menu--horizontal>.el-menu>.el-menu-item {
  font-size: 15px !important;
  font-weight: normal !important;
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
