<template>
  <el-page-header v-on:back="goBack" style="margin-bottom: 5px;margin-left: 10px;margin-right: 10px;" />
  <h2 class="dot-heading">Sample Detail</h2>
  <div id="map" style="height: 500px;"></div>
</template>


<script lang="ts" setup>
import { ref, watch } from 'vue';
import { useRouter } from 'vue-router';
import { onMounted } from 'vue';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { getLogger } from '@/utils/logger';
import { useSamplesinfoStore } from '@/stores/baseinfo';

const log = getLogger('AccessionDetail.vue'); // 当前组件名
log.setLevel('debug'); // 只打开这个组件的调试日志

const router = useRouter();
const samplesinfoStore = useSamplesinfoStore();


// 接收父组件传递的sample_id
const props = defineProps<{
  sample_id: string;
}>();

// 地图缓存变量
let map: L.Map | null = null;
let marker: L.CircleMarker | null = null;
onMounted(() => {
  watch(() => props.sample_id, (newId) => {
    const sample = samplesinfoStore.samplesinfoData.find(s => s.sample_id === Number(newId));
    log.debug('Sample ID changed:', newId);
    if (!sample) {
      log.warn('No sample found with ID:', newId);
      return;
    }
    const lat = Number(sample.latitude);
    const lng = Number(sample.longitude);

    // 初始化地图
    if (!map) {
      map = L.map('map', {
        center: [lat, lng], // 初始中心点：根据传入的经纬度
        zoom: 3,                         // 初始缩放等级
        minZoom: 1,                      // 最小缩放限制（全球范围）
        maxZoom: 5,                      // 最大缩放限制（防止放太近）
        maxBounds: [
          [85, -Infinity],   // 最大可见范围的西北角（纬度限制：北纬85度）
          [-85, Infinity]    // 最大可见范围的东南角（纬度限制：南纬85度）
        ],
        maxBoundsViscosity: 1.0 // 让地图不能超出这个边界（设置为1是完全限制）
      });

      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors',
      }).addTo(map);

    } else {
      // 如果地图已存在，则移动视角
      map.setView([lat, lng], 1);
      if (marker) {
        marker.remove();
      }
    }

    // 添加标记
    marker = L.circleMarker([lat, lng], {
        radius: 6,            // 点的半径
        color: 'blue',        // 边框颜色
        fillColor: 'red',     // 填充颜色
        fillOpacity: 0.7,     // 填充透明度
        weight: 1             // 边框宽度
      }).addTo(map);
    marker.bindPopup(`
    <strong>${sample.sample_name}</strong><br/>
    ${sample.country}
    `).openPopup();
  }, { immediate: true });
});


// back to previous page
function goBack() {
  router.push("/accession_info");
}
</script>