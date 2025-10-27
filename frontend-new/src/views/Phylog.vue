<template>
  <div style="min-height: 20ch;"></div>
  <div class="container">
    <div class="extract_phylogeny">
      <p class="title">
        Extract Phylogeny
      </p>
      <p class="text_note">
        Based on the wealth of genome and transcriptome data, we reconstructed a comprehensive and robustly resolved
        phylogeny of 4,854 insects, representing all 28 orders. This master phylogeny was inferred from 824 concatenated
        BUSCO amino acid genes (a total of 276,683 sites) using maximum likelihood inference. This page allows users to
        extract the phylogenetic relationships of insects of interest. You can use either species names or NCBI taxon
        IDs, which can be found in the master table (List_of_4854_insects_for_phylogeny.tsv) on the download page. The
        output tree will be provided in Newick format.
      </p>
      <el-row class="search_box">
        <el-col :span="0"></el-col>
        <el-col :span="20">
          <div style="display: flex; flex-direction: column; width: 100%;">
            <el-input v-model="taxarea" :rows="7" style="width: 100%; " type="textarea"
              placeholder="Enter a list of taxon names or NCBI taxon IDs" />
            <div style="text-align: left;">
              <el-button @click="fillId" color="#626aef" size="small" plain
                style="margin-top: 4px; align-self: flex-start;">Try a list of taxa</el-button>
            </div>
          </div>
        </el-col>
        <el-col :span="2" style="text-align: left;">
          <el-button color="#8A2BE2" type="primary" :icon="Search" :loading="loading_phylog" @click="submitname"
            style="width: 50px;"></el-button>
        </el-col>

        <el-col :span="4"></el-col>
      </el-row>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { ref } from 'vue';
import { ElMessage } from 'element-plus';
import { useUuidStore } from '@/stores/uuid';
import { useTreeStore } from '@/stores/tree';
import { Search } from '@element-plus/icons-vue';
import { useRouter } from 'vue-router';
import axios from 'axios';


const uuidStore = useUuidStore();
const taxarea = ref('')
const loading_phylog = ref(false)

// 加载示例
const fillId = () => {
  taxarea.value = 'Ischnura_elegans\nEphemera_danica\nNemoura_dubitans\nMantis_religiosa\nBlattella_germanica\nAphis_citricidus\nApis_mellifera\nTribolium_castaneum\nNeoneuromus_ignobilis\nPanorpa_vulgaris\nDrosophila_melanogaster\nHeliconius_numata'; // 更新输入框的值
};


// 展示进化树
const treeStore = useTreeStore()
const router = useRouter();

// 设置跳转
const handleTargetClick = (treeuuid: string) => {
  router.push({ name: 'Viewtree', params: { treeuuid } });
};

// 提交按钮
const submitname = async () => {
  if (!taxarea.value) {
    ElMessage.error('Please paste your taxon names or IDs!');
    return;
  }
  try {
    loading_phylog.value = true
    const response = await axios.post(
      '/tips_api/prune_tree/',
      { species_names: taxarea.value },
      { headers: { uuid: uuidStore.uuid } }
    )
    const data = response.data
    loading_phylog.value = false
    treeStore.setTarget(data.tree)
    console.log(data.tree);
    handleTargetClick(treeStore.targetUUID)
    if (data.wrong_value.length > 0) {
      ElMessage.warning(`These input errors: ${data.wrong_value}`);
    }
  } catch (error) {
    loading_phylog.value = false;
    if (axios.isAxiosError(error)) {
      console.error('Axios error:', error);
      console.error('Status:', error.response?.status);
      console.error('Data:', error.response?.data);
      ElMessage.error(`Request failed: ${error.response?.status} ${error.message}`);
    } else {
      ElMessage.error('Network error or server unreachable');
      console.error('Unknown error:', error);
    }

    // if (error instanceof Error) {
    //   // 后端返回错误响应
    //   ElMessage.error(`Request failed: ${error.message}`);
    // } else {
    //   // 网络或其它异常
    //   ElMessage.error('Network error or server unreachable');
    // }

    // console.error('Error:', error);
  }
}

</script>

<style scoped>
.container {
  padding: 8px;
  max-width: 100%;
  justify-content: center;
  box-sizing: border-box;
}

.extract_phylogeny {
  max-width: 1100px;
  text-align: left;
  line-height: 1.2;
  text-align: justify;
  padding-top: 0px;
  margin: 0 auto;
}

.title {
  font-size: 40px;
  font-family: "Helvetica", Times, Sans-serif;
  margin-top: 5px;
  margin-bottom: 1px;
  font-weight: bold;
  line-height: 1.2;
  color: #333;
}

.text_note {
  font-size: 22px;
  line-height: 1.4;
  font-family: "Helvetica", Times, Sans-serif;
  margin-left: 0px;
  margin-top: 14px;
}

.search_box {
  margin-top: 0px;
  margin-bottom: 0px;
}
</style>
