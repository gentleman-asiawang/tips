<template>
  <h2 class="dot-heading">Search for Variation information by Variation ID:</h2>
  <br>
  <p>On this page, please enter variantid in maizevarmap to view the specific information of the current variant</p>
  <h3>VarID:</h3>
  
  <el-row>
    <el-col :span="20">
      <el-input v-model="var_id" style="width: 100%;height: 50px;" placeholder="Enter a Variant ID" />
      <div style="margin-top: 6px;text-align: left;">
        <span style="margin-right: 5px; font-size: 15px;">Try an example:</span>
        <el-button @click="useExample" size="small" plain>mzs09156095036</el-button>
      </div>
    </el-col>
    <el-col :span="4" style="text-align: left;">
      <el-button type="primary" :icon="Search" :loading @click="submitid" style="width: 100%;height: 50px;"></el-button>
    </el-col>
  </el-row>

</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useUuidStore } from '@/stores/uuid';
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import { Search } from '@element-plus/icons-vue';
import axios from 'axios';
import { getLogger } from '@/utils/logger';

const log = getLogger('VarsInfo.vue'); // 当前组件名
log.setLevel('debug'); // 只打开这个组件的调试日志


const uuidStore = useUuidStore();
const var_id = ref('');
const loading = ref(false)


// 加载示例
const useExample = () => {
  var_id.value = 'mzs09156095036'; // 示例变异ID
}

// 跳转
const router = useRouter();
const handleTargetClick = (target: string, source: string) => {
  router.push({ name: 'VariantDetail', params: { target, source } });
  console.log(target)
};

// 提交按钮
const submitid = async () => {
  if (!var_id.value) {
    ElMessage.error('Please input Variant ID!');
    return;
  }

  if (var_id.value.length !== 14) {
    ElMessage.error('Variant ID must be 14 characters long!');
    return;
  } else if (!(var_id.value.startsWith('mzi') || var_id.value.startsWith('mzs'))) {
    ElMessage.error('Variant ID must start with "mzi" or "mzs"!');
    return;
  }

  try {
    const response = await axios.get('/maizevarmap_api/check_variants_id/', {
      headers: { uuid: uuidStore.uuid },
      params: {
        var_id: var_id.value
      }
    })
    const found = response.data.found;
    if (!found) {
      ElMessage.error('Variant ID not found!');
      return;
    } else {
      // 跳转到变异详情页面
      handleTargetClick(var_id.value, 'vars_info');
    }
    
  } catch (error) {
    ElMessage.error('Error occurred while fetching data.');
    console.error('Error:', error)
  } finally {
    loading.value = false; // 确保加载状态在完成后按钮被释放
  }
}

</script>