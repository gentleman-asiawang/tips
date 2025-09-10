<template>
  <el-config-provider namespace="ep">
    <BaseHeader v-if="!isNotFound" class="header" />
    <div w="full" py="1">
      <div v-if="fullscreenLoading" v-loading.fullscreen.lock="fullscreenLoading"></div>
      <router-view v-slot="{ Component }" v-else>
        <keep-alive>
          <component :is="Component" />
        </keep-alive>
      </router-view>
    </div>
    <!-- <BaseFooter v-if="!isNotFound" /> -->
  </el-config-provider>
</template>

<style>
#app {
  width: 100%;
  text-align: center;
  color: var(--ep-text-color-primary);
}
</style>

<script lang="ts" setup>
import { computed, onMounted, onBeforeUnmount, ref } from 'vue';
import { useRoute } from 'vue-router';
import { useUuidStore, useInfoStore } from './store/globalStore';
import { ElMessage } from 'element-plus';

const route = useRoute();
const isNotFound = computed(() => route.path === '/404');

const handleWindowClose = () => {
  const data = new FormData();
  data.append('uuid', uuidStore.uuid);  //  Use FormData to build request data
  navigator.sendBeacon('/tips_api/delete_all_temp_files/', data);
};

const sendUUIDToServer = async (uuid: string) => {
  const formData = new FormData();
  formData.append('uuid', uuid)
  try {
    const response = await fetch('/tips_api/get_uuid/', {
      method: 'POST',
      body: formData,
    });
    if (!response.ok) {
      throw new Error('Failed to send UUID to the server');
    }
  } catch (error) {
    console.error('Error sending UUID to server:', error);
    throw error;
  }
};

const uuidStore = useUuidStore();
const infoStore = useInfoStore();
const fullscreenLoading = ref(true);
onMounted(async () => {
  try {
    window.addEventListener('beforeunload', handleWindowClose);
    uuidStore.generateUuid();
    await sendUUIDToServer(uuidStore.uuid);
    await infoStore.fetchOrders();
    fullscreenLoading.value = false
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
    
  }
});

// 移除监听器
onBeforeUnmount(() => {
  window.removeEventListener('beforeunload', handleWindowClose);
});
</script>

<style scoped>
.header {
  background: rgba(255, 255, 255, 0.4);
  backdrop-filter: blur(10px);
}
</style>