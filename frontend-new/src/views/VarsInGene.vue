<template>
  <h2 class="dot-heading">Search for Variations in a Gene:</h2>
  <p>On this page, you can query variants by GeneID.</p>
  <el-card>
    <el-form label-width="auto">
      <el-row>
        <el-col :span="8">
          <el-form-item label="Position" style="width: 100%;">
            <el-input v-model="gene_id" placeholder="End Position" />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="Upstream" style="width: 100%;">
            <el-input v-model="upstream" placeholder="End Position" type="number" :min="0.5" :max="10"
              :step="0.1"><template #append>kb</template></el-input>
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="Downstream" style="width: 100%;">
            <el-input v-model="downstream" placeholder="End Position" type="number" :min="0.5" :max="10"
              :step="0.1"><template #append>kb</template></el-input>
          </el-form-item>
        </el-col>
      </el-row>
      <el-form-item label="Variations Type">
        <el-radio-group v-model="vartype">
          <el-radio value="ALL">
            ALL
          </el-radio>
          <el-radio value="SNP">
            SNP
          </el-radio>
          <el-radio value="INDEL">
            INDEL
          </el-radio>
        </el-radio-group>
      </el-form-item>
    </el-form>
    <div style="display: flex; justify-content: flex-end;">
      <el-button type="primary" @click="usesample">Example</el-button>
      <el-button type="primary" @click="submitQuery">Submit</el-button>
    </div>

  </el-card>



  <div v-if="loading_search" v-loading="loading_search" style="height: 40vh;"></div>
  <div v-if="outisnone">
    <el-divider />
    <el-empty description="No data found!" :image-size="300" />
  </div>

  <div v-if="tableData.length">
    <el-divider />
    <h2>Search Results:</h2>
    <h3>Variation Map (with Chromatin Accessibility Map/ Non-coding Varation Scores Map) in Searched Region:</h3>
    <div ref="chartRef" style="width: 100%; height: 400px"></div>
    <h3>Detailed Variation Information:</h3>
    <el-table :data="paginatedData" :stripe="true" style="width: 100%" :highlight-current-row="true"
      show-overflow-tooltip :header-cell-style="{ backgroundColor: '#EBEDF0' }">
      <!-- <el-table-column type="selection" width="55" /> -->
      <el-table-column label="Variant_id" prop="show_id">
        <template #default="{ row }">
          <span @click="handleIdClick(row.show_id, 'vars_in_gene')" style="color: #409EFF; cursor: pointer;">
            {{ row.show_id }}
          </span>
        </template>
      </el-table-column>
      <el-table-column label="Chr" prop="chr" min-width="20px" />
      <el-table-column label="Pos" prop="pos" min-width="50px" />
      <el-table-column label="Ref" prop="ref" />
      <el-table-column label="Alt" prop="alt" />
    </el-table>
    <el-pagination @current-change="handleCurrentChange" :current-page="currentPage" :page-size="pageSize"
      :total="totalItems" layout="total, prev, pager, next, jumper" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick } from 'vue'
import axios from 'axios'
import { useUuidStore } from '@/stores/uuid';
import { ElMessage } from 'element-plus';
import { useRouter } from 'vue-router';
import * as echarts from 'echarts';
import { getLogger } from '@/utils/logger';
const log = getLogger('VarsInGene.vue'); // 当前组件名

let chart: echarts.ECharts | null = null;
const loading_search = ref(false)
const outisnone = ref(false)

interface Variant {
  show_id: string;
  chr: string;
  pos: number;
  ref: string;
  alt: string;
}

const chartRef = ref();

const usesample = () => {
  const sampleGeneIds = [
    "Zm00001eb399670", "Zm00001eb401430", "Zm00001eb401440", "Zm00001eb402030",
    "Zm00001eb402040", "Zm00001eb403240", "Zm00001eb403250", "Zm00001eb403900",
    "Zm00001eb403910", "Zm00001eb406470", "Zm00001eb406480", "Zm00001eb410370",
    "Zm00001eb414870", "Zm00001eb416730", "Zm00001eb416740", "Zm00001eb417190",
    "Zm00001eb418650", "Zm00001eb423890"
  ];

  const randomIndex = Math.floor(Math.random() * sampleGeneIds.length);
  gene_id.value = sampleGeneIds[randomIndex];
}

const gene_id = ref(''); // 用于存储输入的基因ID
const upstream = ref(0.5); // 上游距离
const downstream = ref(0.5); // 下游距离
const vartype = ref('ALL'); // 变异类型

const submitQuery = async () => {
  loading_search.value = true;
  outisnone.value = false;

  try {
    const response = await axios.get('/maizevarmap_api/query_variants_bygeneid/', {
      headers: { uuid: uuidStore.uuid },
      params: {
        gene_id: gene_id.value,
        upstream: upstream.value * 1000, // 转换为碱基数
        downstream: downstream.value * 1000, // 转换为碱基数
        variants_type: vartype.value
      }
    })
    const { region, variants } = response.data;
    tableData.value = variants;

    if (!tableData.value.length) {
      outisnone.value = true;
      loading_search.value = false;
      return;
    }

    // 等 DOM 更新完成后再初始化 ECharts
    await nextTick();

    const mzsData = tableData.value
      .filter(item => item.show_id.startsWith('mzs'))
      .map(item => ({
        value: [item.pos, 1],
        ...item
      }));

    const mziData = tableData.value
      .filter(item => item.show_id.startsWith('mzi'))
      .map(item => ({
        value: [item.pos, 1],
        ...item
      }));

    // 销毁旧的图表实例（关键）
    if (chartRef.value) {
      const existing = echarts.getInstanceByDom(chartRef.value);
      if (existing) {
        existing.dispose();
      }
      chart = echarts.init(chartRef.value);
    }
    const regionStart = region.start_pos - upstream.value * 1000;
    const regionEnd = region.end_pos + downstream.value * 1000;
    const regionWidth = regionEnd - regionStart;
    const pad = Math.round(regionWidth * 0.05);

    (chart as echarts.ECharts).setOption({
      tooltip: {
        formatter: (params: { data: Variant }) => {
          const data = params.data;
          return `
          Type: ${data.show_id.startsWith('mzs') ? 'SNP' : 'INDEL'}<br/>
          ID: ${data.show_id}<br/>
          chr: ${data.chr}<br/>
          pos: ${data.pos}<br/>
          ${data.ref} → ${data.alt}
        `;
        }
      },
      xAxis: {
        name: 'Position',
        type: 'value',
        min: regionStart - pad,
        max: regionEnd + pad,
      },
      yAxis: {
        name: 'SNP',
        type: 'value',
        min: 0,
        max: 2,
      },
      dataZoom: [
        {
          type: 'inside', // 鼠标滚轮缩放
          xAxisIndex: 0,   // 缩放作用于哪个 x 轴
          zoomOnMouseWheel: true, // 默认就是 true，可以省略
        },
        {
          type: 'slider', // 下方拖动条，可选
          xAxisIndex: 0
        }
      ],
      series: [
        {
          name: 'SNP',
          type: 'scatter',
          symbolSize: 10,
          color: '#5470C6',
          data: mzsData
        },
        {
          name: 'INDEL',
          type: 'scatter',
          symbol: 'triangle',
          symbolSize: 10,
          color: '#FF0000',
          data: mziData
        }
      ]
    });

    (chart as echarts.ECharts).on('click', (params) => {
      const data = params.data as Variant;
      if (data?.show_id) {
        handleIdClick(data.show_id, 'vars_in_gene');
      }
    });



  } catch (error) {
    ElMessage.error('Query failed!');
    log.error(error);
  } finally {
    loading_search.value = false;
  }
}

const router = useRouter();
const uuidStore = useUuidStore();


const tableData = ref<Variant[]>([]);



// 表格分页
const pageSize = ref(20); // 每页显示的数量
const currentPage = ref(1); // 当前页码
const totalItems = computed(() => tableData.value.length); // 数据总量

const paginatedData = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value;
  return tableData.value.slice(start, start + pageSize.value);
});

const handleCurrentChange = (page: number) => {
  currentPage.value = page;
};

const handleIdClick = (target: string, source: string) => {
  router.push({ name: 'VariantDetail', params: { target, source } });
};
</script>