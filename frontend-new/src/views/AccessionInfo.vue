<template>
  <h2 class="dot-heading">Accession Information:</h2>
  <div style="display: flex; justify-content: flex-end; margin-bottom: 10px;">
    <el-input v-model="searchQuery" placeholder="Search..." style="width: 300px;" />
  </div>
  <el-table v-if="paginatedData.length > 0" :data="paginatedData" :stripe="true" :highlight-current-row="true"
    :header-cell-style="{ backgroundColor: '#EBEDF0' }" show-overflow-tooltip style="width: 100%" row-key="id">
    <el-table-column prop="sample_id" label="ID" min-width="20px" />
    <el-table-column prop="project_name" label="Project" min-width="50px" />
    <el-table-column prop="sample_name" label="Name" min-width="70px" />
    <el-table-column prop="bases_mapped" min-width="50px">
      <template #header>
        Bases mapped<br>(Gb)
      </template>
    </el-table-column>
    <el-table-column prop="latitude" label="Latitude" min-width="35px" />
    <el-table-column prop="longitude" label="Longitude" min-width="40px" />
    <el-table-column prop="country" label="Source" min-width="70px" />
    <el-table-column prop="species" label="Species" />
    <el-table-column label="" fixed="right" min-width="40px">
      <template #default="{ row }">
        <el-button type="primary" size="small" :icon="Location" @click="goDetail(row)">View Detail</el-button>
      </template>
    </el-table-column>
  </el-table>
  <el-pagination @current-change="handleCurrentChange" :current-page="currentPage" :page-size="pageSize"
    :total="totalItems" layout="total, prev, pager, next, jumper" />
  <h2>Distribution Map:</h2>
  <div id="distribution_map" style="height: 500px;"></div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useSamplesinfoStore } from '@/stores/baseinfo';
import { useRouter } from 'vue-router';
import { getLogger } from '@/utils/logger';
import { Location } from '@element-plus/icons-vue';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

const log = getLogger('AccessionInfo.vue'); // 当前组件名
log.setLevel('debug'); // 只打开这个组件的调试日志

log.debug('AccessionInfo.vue loaded');
const samplesinfoStore = useSamplesinfoStore();
const samplesinfoData = samplesinfoStore.samplesinfoData;
const router = useRouter();



// 过滤数据
const searchQuery = ref('');
const filteredData = computed(() => {
  if (!searchQuery.value) return samplesinfoData;
  const query = searchQuery.value.toLowerCase();
  return samplesinfoData.filter(item =>
    item.project_name.toString().toLowerCase().includes(query) ||
    item.sample_name.toLowerCase().includes(query)
  );
});

// 表格分页
const pageSize = ref(15); // 每页显示的数量
const currentPage = ref(1); // 当前页码
const totalItems = computed(() => filteredData.value.length); // 数据总量
const paginatedData = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value;
  return filteredData.value.slice(start, start + pageSize.value);
});
const handleCurrentChange = (page: number) => {
  currentPage.value = page;
};



const goDetail = (row: any) => {
  const sample_id = row.sample_id;
  router.push({
    name: 'accession_detail',
    params: {
      sample_id
    }
  });
};

onMounted(() => {
  const distribution_map = L.map('distribution_map', {
    center: [20, 0], // 地图初始中心（你可以自定义）
    zoom: 2,
    minZoom: 1,
    maxZoom: 5,
    maxBounds: [
      [85, -180],
      [-85, 180],
    ],
    maxBoundsViscosity: 1.0
  });

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap contributors',
  }).addTo(distribution_map);

  // 添加样本点
  samplesinfoStore.samplesinfoData.forEach(sample => {
    const lat = Number(sample.latitude);
    const lng = Number(sample.longitude);
    if (!isNaN(lat) && !isNaN(lng)) {
      // const marker = L.marker([lat, lng]).addTo(distribution_map);
      L.circleMarker([lat, lng], {
        radius: 6,            // 点的半径
        color: 'blue',        // 边框颜色
        fillColor: 'red',     // 填充颜色
        fillOpacity: 0.7,     // 填充透明度
        weight: 1             // 边框宽度
      }).addTo(distribution_map);
    }
  });
});
</script>