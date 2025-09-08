<template>
  <h2 class="dot-heading">Search for Polymorphic Positions Between Two Accessions:</h2>
  <el-card>
    <el-form label-width="auto">
      <el-row>
        <el-col :span="12">
          <el-form-item label="Accession 1" style="width: 100%;"> 
            <el-select-v2 v-model="cultivar1" filterable :options="all_cultivars"
              placeholder="Please select"></el-select-v2>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="Accession 2" style="width: 100%;">
            <el-select-v2 v-model="cultivar2" filterable :options="all_cultivars"
              placeholder="Please select"></el-select-v2>
          </el-form-item>
        </el-col>
      </el-row>

      <el-row>
        <el-col :span="6">
          <el-form-item label="Chromsome" style="width: 100%;">
            <el-select v-model="selectedChrom">
              <el-option v-for="chrom in chromNames" :key="chrom" :label="chrom" :value="chrom" />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="18">
          <el-form-item label="Position" style="width: 100%;">
            <el-col :span="11">
              <el-form-item style="width: 100%;">
                <el-input v-model="startPos" placeholder="Start Position" />
              </el-form-item>
            </el-col>
            <el-col class="text-center" :span="2">
              <span>-</span>
            </el-col>
            <el-col :span="11">
              <el-form-item style="width: 100%;">
                <el-input v-model="endPos" placeholder="End Position" />
              </el-form-item>
            </el-col>
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

  <div v-if="tableData.length">
    <el-divider />
    <el-table :data="paginatedData" :stripe="true" style="width: 100%" :highlight-current-row="true"
      show-overflow-tooltip :header-cell-style="{ backgroundColor: '#EBEDF0' }">
      <el-table-column label="Variant_id" prop="show_id" min-width="60px">
        <template #default="{ row }">
          <span @click="handleIdClick(row.show_id, 'vars_in_region')" style="color: #409EFF; cursor: pointer;">
            {{ row.show_id }}
          </span>
        </template>
      </el-table-column>
      <el-table-column label="Type" prop="type" min-width="30px" />
      <el-table-column label="Chr" prop="chr" min-width="30px" />
      <el-table-column label="Pos" prop="pos" />
      <el-table-column label="Ref" prop="ref" />
      <el-table-column label="Alt" prop="alt" />
      <el-table-column :label="getCultivarLabelById(cultivar1)" prop="gt1" min-width="60px" />
      <el-table-column :label="getCultivarLabelById(cultivar2)" prop="gt2" min-width="60px" />
    </el-table>
    <el-pagination @current-change="handleCurrentChange" :current-page="currentPage" :page-size="pageSize"
      :total="totalItems" layout="total, prev, pager, next, jumper" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useChromStore, useSamplesinfoStore } from '@/stores/baseinfo';
import { ElMessage } from 'element-plus';
import { useUuidStore } from '@/stores/uuid';
import { useRouter } from 'vue-router';
import axios from 'axios';
import { getLogger } from '@/utils/logger';
const log = getLogger('TwoCultivarsCompare.vue'); // 当前组件名

log.setLevel('debug'); // 只打开这个组件的调试日志

const router = useRouter();
const chromStore = useChromStore()
const samplesinfoStore = useSamplesinfoStore();
const uuidStore = useUuidStore();
const chromNames = chromStore.chromNames;

const emit = defineEmits(['updateSelection'])

interface Option {
  value: number
  label: string
}

interface Variant {
  show_id: string;
  pos: number;
  type: string;
  ref: string;
  alt: string;
  gt1: string;
  gt2: string;
}

const tableData = ref<Variant[]>([]);
const all_cultivars = ref<Option[]>([])
const selectedChrom = ref()
const startPos = ref()
const endPos = ref()
const vartype = ref('ALL')
const cultivar1 = ref()
const cultivar2 = ref()

function getCultivarLabelById(id: number) {
  const item = all_cultivars.value.find(c => c.value === id)
  return item ? item.label : `样本ID: ${id}` // fallback
}

function formatGenotype(value: string | null): string {
  if (value === null || value === undefined) return '0|0'
  const num = Number(value)
  const bin = num.toString(2).padStart(6, '0')
  const left = parseInt(bin.slice(0, 3), 2)
  const right = parseInt(bin.slice(3), 2)
  return `${left}|${right}`
}

onMounted(() => {
  const samplesinfoData = samplesinfoStore.samplesinfoData
  if (samplesinfoData && Array.isArray(samplesinfoData)) {
    all_cultivars.value = samplesinfoData.map((item) => ({
      value: Number(item.sample_id),
      label: `${item.sample_name} (${item.project_name})`,
    }))
  }
})

const submitQuery = async () => {
  if (!cultivar1.value || !cultivar2.value) {
    ElMessage.error('Please select both cultivars!')
    return
  }
  if (!selectedChrom.value) {
    ElMessage.error('Please select a chromosome!')
    return
  }
  if (!startPos.value || !endPos.value) {
    ElMessage.error('Please enter both Start and End positions!')
    return
  }
  if (startPos.value >= endPos.value) {
    ElMessage.error('Start position must be less than End position!')
    return
  }

  try {
    const response = await axios.get('/maizevarmap_api/get_variants_cultivars/', {
      headers: { uuid: uuidStore.uuid },
      params: {
        chr: selectedChrom.value,
        start: startPos.value,
        end: endPos.value,
        var_type: vartype.value,
        cultivar1: cultivar1.value,
        cultivar2: cultivar2.value,
      }
    })


    tableData.value = (response.data as Omit<Variant, 'chr'>[]).map((item) => ({
      ...item,
      chr: selectedChrom.value,
      gt1: formatGenotype(item.gt1),
      gt2: formatGenotype(item.gt2),
    }));

    if (tableData.value.length === 0) {
      ElMessage.warning('No data found!');
    }



  } catch (error) {
    log.error('Failed to fetch variants:', error)
    return
  }

}

const usesample = () => {
  const chrs = [
    "chr1", "chr2", "chr3", "chr4", "chr5", "chr6", "chr7", "chr8", "chr9", "chr10"
  ];

  const randomIndex = Math.floor(Math.random() * chrs.length);
  cultivar1.value = 3;
  cultivar2.value = 40;
  selectedChrom.value = chrs[randomIndex];
  startPos.value = 1;
  endPos.value = 10000;
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

<style scoped>
.text-center {
  text-align: center;
}
</style>