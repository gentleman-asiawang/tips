<template>
  <h2 style="display: flex; align-items: center;" class="dot-heading">
    Search for Variations in a Region:
    <el-tooltip content="tooltip" placement="bottom">
      <el-icon color="#409eff" style="margin-left: 6px;">
        <InfoFilled />
      </el-icon>
    </el-tooltip>
  </h2>
  <p>On this page, you can query variants based on chromosomal regions.</p>
  <ChromSelector @updateSelection="handleSearch" />
  <div v-if="loading_search" v-loading="loading_search" style="height: 40vh;"></div>
  <div v-if="outisnone">
    <el-divider />
    <el-empty description="No data found!" :image-size="300" />
  </div>
  <div v-if="tableData.length">
    <el-divider />
    <el-table :data="paginatedData" :stripe="true" style="width: 100%" :highlight-current-row="true"
      show-overflow-tooltip :header-cell-style="{ backgroundColor: '#EBEDF0' }">
      <!-- <el-table-column type="selection" width="55" /> -->
      <el-table-column label="Variant_id" prop="show_id" min-width="50px">
        <template #default="{ row }">
          <span @click="handleIdClick(row.show_id, 'vars_in_region')" style="color: #409EFF; cursor: pointer;">
            {{ row.show_id }}
          </span>
        </template>
      </el-table-column>
      <el-table-column label="Chr" prop="chr" min-width="30px" />
      <el-table-column label="Pos" prop="pos" min-width="30px" />
      <el-table-column label="Ref" prop="ref" min-width="50px" />
      <el-table-column prop="major_allele" min-width="50px">
        <template #header>
          <div style="display: flex; align-items: center;">
            <span>Primary Allele</span>
            <el-tooltip content="Description derived from structure-based annotation." placement="top">
              <el-icon color="#409EFF" style="margin-left: 3px;">
                <InfoFilled />
              </el-icon>
            </el-tooltip>
          </div>
        </template>
      </el-table-column>
      <el-table-column label="Secondary Allele" prop="minor_allele" />
      <el-table-column label="Frequency of Primary Allele in All" prop="af" />
      <el-table-column label="Frequency of Primary Allele in Selected" prop="select_af" />
    </el-table>
    <el-pagination @current-change="handleCurrentChange" :current-page="currentPage" :page-size="pageSize"
      :total="totalItems" layout="total, prev, pager, next, jumper" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import ChromSelector from '@/components/ChromSelector.vue'
import axios from 'axios';
import { useUuidStore } from '@/stores/uuid';
import { useSamplesinfoStore, usePopulationsStore } from '@/stores/baseinfo';
import { ElMessage } from 'element-plus';
import { useRouter } from 'vue-router';
import { getLogger } from '@/utils/logger';
import { InfoFilled } from '@element-plus/icons-vue';
const log = getLogger('VarsInRegion.vue'); // 当前组件名

log.setLevel('debug'); // 只打开这个组件的调试日志

interface Population {
  population_id: number;
  population: string;
  p_ac: string;
}

interface Variant {
  show_id: string;
  chr: string;
  pos: number;
  ref: string;
  alt: string;
  populations: Population[];
  ac: string;
}

const router = useRouter();
const uuidStore = useUuidStore();
const samplesinfoStore = useSamplesinfoStore();
const populationsStore = usePopulationsStore();
const populationsData = populationsStore.populationsData;

const tableData = ref<Variant[]>([]);
const elapsedTime = ref(0)
const loading_search = ref(false)
const outisnone = ref(false)



const selectedRegion = ref({ chr: '', start: 0, end: 0 })
const handleSearch = async (selection: { chr: string, start: number, end: number, vartype: string, populations: number[] }) => {
  tableData.value = []
  selectedRegion.value = selection
  log.debug('Selected region:', selection)
  try {
    loading_search.value = true
    outisnone.value = false
    const startTime = Date.now();
    const response = await axios.get('/maizevarmap_api/get_variants_region/', {
      headers: { uuid: uuidStore.uuid },
      params: {
        chr: selection.chr,
        start: selection.start,
        end: selection.end,
        var_type: selection.vartype,
        populations: selection.populations
      }
    })
    const total = samplesinfoStore.samplesinfoData.length * 2
    const selectedChr = selection.chr;
    tableData.value = (response.data as Omit<Variant, 'chr'>[]).map((item) => {
      const totalSamples = item.populations.reduce((sum, pop) => {
        const matched = populationsData.find(p => p.population_id === pop.population_id);
        return sum + (matched ? Number(matched.population_count) : 0);
      }, 0);
      log.debug('Total samples in selected populations:', totalSamples);

      // const alleleCountList = item.populations.map(pop =>
      //   pop.p_ac.split(',').map(s => Number(s.trim()))
      // )
      // // 按位求和，比如 [[20,5], [30,10]] -> [50,15]
      // const pAltAC = alleleCountList.reduce((acc, curr) => {
      //   return acc.map((val, i) => val + (curr[i] || 0))
      // }, new Array(alleleCountList[0].length).fill(0))
      // log.debug('Population alt allele counts:', pAltAC)
      const altAC = item.ac.split(',').map(v => Number(v.trim()))
      
      const sumAltAC = altAC.reduce((sum, val) => sum + val, 0)
      const refAC = Math.max(total - sumAltAC, 0)
      const acParts = [refAC, ...altAC]
      const alleles = [item.ref, ...item.alt.split(',').map(s => s.trim())]
      // 找出排序后的索引
      const indexedAC = acParts.map((count, i) => ({ index: i, count }))
      indexedAC.sort((a, b) => b.count - a.count)  // 降序排列

      const majorIndex = indexedAC[0]?.index ?? 0
      const minorIndex = indexedAC[1]?.index ?? 0

      const majorAf = total === 0 ? 0 : +(Math.max(...acParts) / total).toFixed(4);

      return {
        ...item,
        chr: selectedChr,
        af: majorAf,
        select_af: majorAf,
        major_allele: alleles[majorIndex],
        minor_allele: alleles[minorIndex]
      }
    })

    currentPage.value = 1
    loading_search.value = false
    const endTime = Date.now();
    elapsedTime.value = endTime - startTime;
    if (tableData.value.length === 0) {
      outisnone.value = true;
      ElMessage.warning('No data found!');
    }

  } catch (error) {
    loading_search.value = false;
    log.error('Failed to fetch variants:', error)
    return
  }
}


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

<style>
.input-with-select .el-input-group__prepend {
  background-color: var(--el-fill-color-blank);
}
</style>