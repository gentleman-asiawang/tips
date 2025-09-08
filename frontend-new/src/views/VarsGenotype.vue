<template>
  <h2 class="dot-heading">Search for Genotype With Variation ID:</h2>
  <p>On this page, you can query genotype by variant ID.</p>

  <el-card>
    <el-form label-width="auto">
      <el-form-item label="Cultivars" style="width: 100%;">
        <el-select-v2 v-model="cultivars" filterable :options="data" placeholder="Please select" multiple clearable
          @change="handleChange">
        </el-select-v2>
      </el-form-item>
      <el-form-item label="variant id">
        <el-input v-model="var_id" type="textarea" placeholder="Enter variant id" :rows="5" />
      </el-form-item>
    </el-form>
    <div style="display: flex; justify-content: flex-end;">
      <el-button type="primary" @click="usesample">Example</el-button>
      <el-button type="primary" @click="handleSubmit" :loading="loading_query">Submit</el-button>
    </div>
  </el-card>
  <div v-if="loading_query" v-loading="loading_query" style="height: 40vh;"></div>
  <div v-if="outisnone">
    <el-divider />
    <el-empty description="No matching data found!" :image-size="300" />
  </div>
  <div v-if="tableData.length">
    <el-divider />
    <h2>Search Results:</h2>
    <h3>Detailed Genotype Information:</h3>
    <div style="display: flex; justify-content: flex-end; margin-bottom: 10px;">
      <el-input v-model="searchQuery" placeholder="Search..." style="width: 300px;" />
    </div>
    <el-table :data="paginatedData" :stripe="true" style="width: 100%" :highlight-current-row="true"
      show-overflow-tooltip :header-cell-style="{ backgroundColor: '#EBEDF0' }">
      <el-table-column label="Variant ID" prop="label" min-width="80px" />
      <el-table-column v-for="id in allVarIds" :key="id" :prop="id" :label="id" :min-width="120">
        <template #header>
          <span @click="handleIdClick(id, 'vars_genotype')" style="cursor: pointer; color: #409EFF;">
            {{ id }}
          </span>
        </template>
      </el-table-column>
    </el-table>
    <el-pagination @current-change="handleCurrentChange" :current-page="currentPage" :page-size="pageSize"
      :total="totalItems" layout="total, prev, pager, next, jumper" />
  </div>
</template>

<script lang="ts" setup>
import { ref, onMounted, computed } from 'vue'
import { useSamplesinfoStore } from '@/stores/baseinfo';
import { useUuidStore } from '@/stores/uuid';
import { getLogger } from '@/utils/logger';
import axios from 'axios';
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';

const loading_query = ref(false)
const outisnone = ref(false)
const log = getLogger('VarsGenotype.vue'); // 当前组件名

log.setLevel('debug'); // 只打开这个组件的调试日志

const samplesinfoStore = useSamplesinfoStore();
const uuidStore = useUuidStore();

interface Option {
  value: number
  label: string
  disabled?: boolean
}


const data = ref<Option[]>([])
const cultivars = ref<number[]>([])

onMounted(() => {
  const samplesinfoData = samplesinfoStore.samplesinfoData
  if (samplesinfoData && Array.isArray(samplesinfoData)) {
    const options = samplesinfoData.map((item) => ({
      value: Number(item.sample_id),
      label: `${item.sample_name} (${item.project_name})`,
      disabled: false // 禁用全选项
    }))
    // 插入全选项
    data.value = [{ value: 0, label: 'All', disabled: false }, ...options]
  }
})


const lastselect = ref<number[]>([])
const handleChange = (val: number[]) => {
  log.debug('-------------------------------------------------')
  log.debug('values:', cultivars.value)
  log.debug('Selected values:', val)
  const isAllSelected = val.includes(0)
  log.debug('Is all selected:', isAllSelected)
  if (lastselect.value.length === 0) {
    log.debug('First selection')
    if (isAllSelected) {
      // 如果之前没有选择过，且现在选择了全选，则禁用除全选外其他选项,且清空选项（应对示例数据的情况）
      data.value.forEach((item) => {
        item.disabled = item.value !== 0
      })
      cultivars.value = [0];
    } else {
      // 如果之前没有选择过，且现在没有选择全选，则什么也不做
    }
    // 记录当前的选择
    lastselect.value = val
  } else {
    const islastAllSelected = lastselect.value.includes(0)
    log.debug('Already selected')
    if (isAllSelected) {
      // 只要选全选，都禁用除全选外其他选项，且只保留全选
      data.value.forEach((item) => {
        item.disabled = item.value !== 0
      })
      log.debug('All selected, disabling other options')
      cultivars.value = [0]
      // 记录当前的选择
      lastselect.value = val
    } else {
      if (islastAllSelected) {
        // 如果之前选择过全选，现在没有选择全选，则启用所有选项，并且还原除0之外的值
        data.value.forEach((item) => {
          item.disabled = false
        })

        cultivars.value = lastselect.value.filter((v) => v !== 0)
        lastselect.value = cultivars.value
        log.debug('lastselect:', lastselect.value)
      } else {
        // 如果之前没有选择全选，现在没有选择全选，则记录当前的选择
        lastselect.value = val
      }
    }
  }
  log.debug('Submit values:', cultivars.value)
}

// 校验用户的ID是否存在
const var_id = ref<string>('') // 用于存储输入的变异ID


// 定义结构
interface GenotypeItem {
  sample_id: number;
  genotype: number;
}
interface VariantResult {
  show_id: string;
  chr: string;
  position: number;
  ref: string;
  alt: string;
  genotypes: GenotypeItem[];
}

const tableData = ref<any[]>([])  // 表格的行数据
const allVarIds = ref<string[]>([])         // 所有变异 ID（列名）
const handleSubmit = async () => {
  if (cultivars.value.length === 0) {
    ElMessage.warning('Please select at least one cultivar.');
    return;
  }
  // 拆分并清洗多行 ID
  const rawInput = var_id.value.trim();
  const var_id_lines = rawInput.split('\n')
    .map(line => line.trim())
    .filter(line => line.length > 0);

  if (var_id_lines.length === 0) {
    ElMessage.warning('Please enter a variant ID.');
    return;
  }
  // 校验每个 ID 是否合格，收集所有错误信息
  const errors: string[] = [];

  var_id_lines.forEach(id => {
    if (id.length !== 14) {
      errors.push(`"${id}" is not 14 characters long.`);
    } else if (!(id.startsWith('mzi') || id.startsWith('mzs'))) {
      errors.push(`"${id}" must start with "mzi" or "mzs".`);
    }
  });

  if (errors.length > 0) {
    ElMessage.warning(`Invalid Variant ID(s):\n` + errors.join('\n'));
    return;
  }
  tableData.value = []; // 清空之前的表格数据
  try {
    loading_query.value = true;
    outisnone.value = false;
    const response = await axios.post(
      '/maizevarmap_api/check_and_query_gt_by_id/',
      {
        var_ids: var_id_lines,
        cultivars: cultivars.value
      },
      {
        headers: { uuid: uuidStore.uuid }
      }
    );
    const not_found = response.data.not_found;
    const result: VariantResult[] = response.data.result;

    if (not_found.length !== 0) {
      const ids = not_found.map((n: { id: string }) => n.id);
      ElMessage.warning(`Variant ID(s) "${ids.join(', ')}" not found, ignored.`);
    }
    if (!result || result.length === 0) {
      ElMessage.warning('No valid variant data returned.');
      outisnone.value = true;  // 显示无数据状态
      return;  // 提前退出后续逻辑
    }


    const metaRows = [
      {
        label: 'Chromosome',
        ...Object.fromEntries(result.map(r => [r.show_id, r.chr]))
      },
      {
        label: 'Position',
        ...Object.fromEntries(result.map(r => [r.show_id, r.position]))
      },
      {
        label: 'Ref',
        ...Object.fromEntries(result.map(r => [r.show_id, r.ref]))
      },
      {
        label: 'Alt',
        ...Object.fromEntries(result.map(r => [r.show_id, r.alt]))
      }
    ]

    // 获取所有的 variant 列名（即 show_id）
    allVarIds.value = result.map((item: VariantResult) => item.show_id)

    // 建立 sample_id → genotype 的映射
    const sampleMap = new Map<number, any>()

    samplesinfoStore.samplesinfoData.forEach(f => {
      const isAll = cultivars.value.includes(0)
      if (isAll || cultivars.value.includes(f.sample_id)) {
        const base: Record<string, any> = {
          label: `${f.sample_name} (${f.project_name})`
        }
        allVarIds.value.forEach((varId: string) => {
          base[varId] = '0|0'  // 预设默认值
        })
        sampleMap.set(f.sample_id, base)
      }
    })

    // 填充真实的基因型
    result.forEach((item: VariantResult) => {
      item.genotypes.forEach(gt => {
        const sample = sampleMap.get(gt.sample_id)
        if (sample) {
          const bin = gt.genotype.toString(2).padStart(6, '0')
          const left = parseInt(bin.slice(0, 3), 2)
          const right = parseInt(bin.slice(3), 2)
          sample[item.show_id] = `${left}|${right}`
        }
      })
    })

    // 最终表格数据
    tableData.value = [
      ...metaRows,
      ...Array.from(sampleMap.values())
    ]
    log.debug('tableData:', tableData.value);
  } catch (error) {
    ElMessage.error('Query failed!');
    log.error(error);
  } finally {
    loading_query.value = false;
  }

}
// 过滤数据
const metaRowCount = 4; // 信息行数量：Chromosome、Position、Ref、Alt
const searchQuery = ref('');
const filteredData = computed(() => {
  if (!searchQuery.value) return tableData.value;
  const query = searchQuery.value.toLowerCase();
  const metaRows = tableData.value.slice(0, metaRowCount); // 保留头部信息行
  const dataRows = tableData.value.slice(metaRowCount); // 样本行
  const filtered = dataRows.filter(item =>
    Object.values(item).some(val =>
      String(val).toLowerCase().includes(query)
    )
  );

  return [...metaRows, ...filtered];
});

// 表格分页
const pageSize = ref(20); // 每页显示的数量
const currentPage = ref(1); // 当前页码
const totalItems = computed(() => filteredData.value.length); // 数据总量

const paginatedData = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value;
  return filteredData.value.slice(start, start + pageSize.value);
});

const handleCurrentChange = (page: number) => {
  currentPage.value = page;
};



const usesample = () => {
  cultivars.value = [1, 2, 3];
  // var_id.value = 'mzs09159241572\nmzs09159241648\nmzi09159241588'; // 示例变异ID
  var_id.value = 'mzs09159241572\nmzs09159241648\nmzs09160404097'; // 示例变异ID
}

// 点击变异ID跳转到详细页面
const router = useRouter();
const handleIdClick = (target: string, source: string) => {
  router.push({ name: 'VariantDetail', params: { target, source } });
};
</script>

<style scoped>
.full-transfer {
  width: 100%;
}

/* 覆盖两个面板的宽度 */
::v-deep(.el-transfer-panel) {
  width: 40%;
}

/* 可选：调整中间箭头区域 */
::v-deep(.el-transfer__buttons) {
  width: auto;
}

.full-transfer .el-transfer__buttons {
  width: auto;
}
</style>