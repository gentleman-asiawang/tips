<template>
  <el-card>
    <el-form label-width="auto">
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
      <el-form-item label="Populations">
        <el-checkbox-group v-model="populations">
          <el-checkbox v-for="pop in populationsData" :key="pop.population_id" :label="pop.population" :value="pop.population_id">
            {{ pop.population }}
          </el-checkbox>
        </el-checkbox-group>
      </el-form-item>
    </el-form>
    <div style="display: flex; justify-content: flex-end;">
      <el-button type="primary" @click="usesample">Example</el-button>
      <el-button type="primary" @click="submitQuery">Submit</el-button>
    </div>
  </el-card>

</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useChromStore } from '@/stores/baseinfo';
import { ElMessage } from 'element-plus';
import { usePopulationsStore } from '@/stores/baseinfo';
import { getLogger } from '@/utils/logger';

const log = getLogger('ChromSelector'); // 当前组件名
log.setLevel('debug'); // 只打开这个组件的调试日志

const populationsStore = usePopulationsStore();
const populationsData = populationsStore.populationsData;


const chromStore = useChromStore()
const chromNames = chromStore.chromNames

const emit = defineEmits(['updateSelection'])

const selectedChrom = ref()
const startPos = ref()
const endPos = ref()
const vartype = ref('ALL')
const populations = ref([])  // 默认选择ALL

const submitQuery = async () => {
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
  if (endPos.value - startPos.value > 100000) {
    ElMessage.error('The range between Start and End positions must not exceed 100Kb!')
    return
  }

  log.debug('populations:', populations.value);

  emit('updateSelection', {
    chr: selectedChrom.value,
    start: startPos.value,
    end: endPos.value,
    vartype: vartype.value,
    populations: populations.value
  });
}

const usesample = () => {
  const chrs = [
    "chr1", "chr2", "chr3", "chr4", "chr5", "chr6", "chr7", "chr8", "chr9", "chr10"
  ];

  const randomIndex = Math.floor(Math.random() * chrs.length);
  // selectedChrom.value = chrs[randomIndex];
  selectedChrom.value = 'chr10'; // For testing, always use chr1
  startPos.value = 1;
  endPos.value = 100000;
}
</script>

<style scoped>
.text-center {
  text-align: center;
}
</style>