<template>
  <el-backtop :right="30" :bottom="50" />
  <el-scrollbar>
    <div class="container">
      <h1>Download Table</h1>
      <el-table :data="allData" stripe style="width: 100%" :header-cell-style="{ backgroundColor: '#EBEDF0' }">
        <el-table-column prop="name" label="Filename" />
        <el-table-column prop="date" label="Uploaded" />
        <el-table-column prop="size" label="Size" />
        <el-table-column label="" min-width="10px">
          <template v-slot="{ row }">
            <a :href="`https://tips.shenxlab.com/tips_data/${row.name}`" download>
              <el-icon>
                <Download color="#409EFF" />
              </el-icon>
            </a>
          </template>
        </el-table-column>
      </el-table>
      <el-divider />
      <h1>Download Structure</h1>
      <h2 class="dot-heading">By Protein IDs</h2>
      <p class="info-text">
        Given a list of protein IDs, you can batch download the corresponding structures. Note that maximum number of
        protein
        IDs is 100. The protein IDs can be found in the master table (List_of_proteinIDs_with_structures.tsv).
      </p>

      <div style="display: flex; align-items: flex-start; width: 100%;">
        <el-input v-model="idinput" style="flex: 1;" :rows="7" placeholder="Enter a list of protein IDs"
          type="textarea" />
        <el-button color="#8A2BE2" type="primary" :icon="Search" :loading @click="downloadSelect"
          style="width: 50px;" />
      </div>
      <el-button @click="fillIdinput" color="#626aef" size="small" plain style="margin-top: 6px;">Try a list of
        PID</el-button>

      <h2 class="dot-heading">By Species</h2>
      <p class="info-text">
        For downloading all predictions for a given species, you can provide the taxID for filtering and download using
        the
        links below. The taxID can be found in the master table (List_of_824_insects_with_structures.tsv).
      </p>
      <div v-loading="loading_table">
        <div style="display: flex; justify-content: flex-end; margin-bottom: 10px;">
          <el-input v-model="searchQuery" placeholder="Search..." style="width: 300px;" />
        </div>
        <el-table :data="paginatedData" :stripe="true" :highlight-current-row="true"
          :header-cell-style="{ backgroundColor: '#EBEDF0' }" show-overflow-tooltip style="width: 100%" row-key="id">
          <el-table-column prop="filename" label="Filename" min-width="70px" />
          <el-table-column prop="tax_id" label="NCBI TaxID" min-width="35px" />
          <el-table-column prop="count" label="Predicted Structures" min-width="40px" />
          <el-table-column prop="size" label="Size" min-width="24px" />
          <el-table-column prop="md5" label="MD5" min-width="70px" />
          <el-table-column label="" min-width="10px">
            <template v-slot="{ row }">
              <a :href="`https://tips.shenxlab.com/tips_data/structure/${row.filename}`" download>
                <el-icon>
                  <Download color="#409EFF" />
                </el-icon>
              </a>
            </template>
          </el-table-column>
        </el-table>
        <el-pagination @current-change="handleCurrentChange" :current-page="currentPage" :page-size="pageSize"
          :total="totalItems" layout="total, prev, pager, next, jumper" />
      </div>
      <h2 class="dot-heading">Full Dataset</h2>
      <p class="info-text">
        The full dataset of all predicted structures and phylogenomic matrix are available at <el-link
          style="font-size: 22px;" type="primary" href="https://doi.org/10.25452/figshare.plus.25906339"
          target="_">Figshare+</el-link>.
      </p>
      <h1>Download Database</h1>
      <p class="info-text">
        Database of protein structures with well-known functions.
        <el-tooltip
          content="<span>The CATH SSG5 database can be obtained from <a style='text-decoration: none;color: #409EFF;' href='https://www.science.org/doi/10.1126/science.adq4946' target='_'>this study</a></span>"
          raw-content placement="top">
          <el-icon color="#409EFF">
            <InfoFilled />
          </el-icon>
        </el-tooltip>
      </p>
      <el-table :data="fulldatabase" stripe style="width: 100%" :header-cell-style="{ backgroundColor: '#EBEDF0' }">
        <el-table-column prop="name" label="Filename" />
        <el-table-column prop="date" label="Uploaded" min-width="50px" />
        <el-table-column prop="size" label="Size" min-width="30px" />
        <el-table-column prop="md5" label="MD5" min-width="90px" />
        <el-table-column label="" min-width="10px">
          <template v-slot="{ row }">
            <a :href="`https://tips.shenxlab.com/tips_data/pdb_and_swissprot_database.tar.xz`" download>
              <el-icon>
                <Download color="#409EFF" />
              </el-icon>
            </a>
          </template>
        </el-table-column>
      </el-table>
      <el-divider />
      <h1>License</h1>
      <p class="info-text">
        Data is available for academic and commercial use, under a <el-link
          href="https://creativecommons.org/licenses/by/4.0/" target="_" style="font-size: 22px;"
          type="primary">CC-BY-4.0
          licence</el-link>.
      </p>
    </div>
  </el-scrollbar>
</template>

<script lang="ts" setup>
import { ref, computed, onMounted } from 'vue';
import { ElMessage } from 'element-plus';
import { Search, Download, InfoFilled } from '@element-plus/icons-vue';
import { useUuidStore } from '@/stores/uuid';
import axios from 'axios';
const uuidStore = useUuidStore();

const loading_table = ref(true)

// 按照PID list下载数据，最多100个
const idinput = ref('')
const loading = ref(false)
const downloadSelect = async () => {
  if (!idinput.value) {
    ElMessage.error('Please input id!');
    return;
  }
  const tipsIdList = idinput.value.split('\n').map(line => line.trim()).filter(line => line !== '');
  try {
    loading.value = true
    const response = await axios.post(
      '/tips_api/download_data/',
      {
        tips_id: tipsIdList,
        down_type: 'both'
      },
      {
        headers: {
          uuid: uuidStore.uuid
        },
        responseType: 'blob'
      }
    );
    // 从响应头中获取文件名
    let filename = 'select.zip'; // 默认名
    const disposition = response.headers['content-disposition'];
    if (disposition && disposition.includes('filename=')) {
      filename = disposition
        .split('filename=')[1]
        .trim()            // 去掉空格
        .replace(/['"]/g, ''); // 去掉可能的引号
    }
    const url = window.URL.createObjectURL(response.data);
    const a = document.createElement('a');
    a.style.display = 'none';
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    a.remove();
    window.URL.revokeObjectURL(url);
  } catch (error) {
    console.error('Error:', error)
  } finally {
    loading.value = false
  }
}

// 加载示例
const fillIdinput = () => {
  idinput.value = 'P003003001139\nP005072009281\nP009027009755\nP010059005391\nP002017007794\nP011041000349\nP011146003427\nP017009002614\nP018016008561\nP023002012790'; // 更新输入框的值
};

// 总表数据信息
const allData = [
  {
    name: 'List_of_proteinIDs_with_structures.tsv',
    date: '2024-10-30',
    size: '894 MB',
  },
  {
    name: 'List_of_824_insects_with_structures.tsv',
    date: '2024-10-30',
    size: '84 KB',
  },
  {
    name: 'List_of_4854_insects_for_phylogeny.tsv',
    date: '2024-10-30',
    size: '282 KB',
  },
]

const fulldatabase = [
  {
    name: 'pdb_and_swissprot_database.tar.xz',
    date: '2025-10-29',
    size: '1.3 GB',
    md5: '10ac65eb6c9ad56ba72b0233b959e820'
  }
]

// 转换文件大小为 MB
const formatFileSize = (sizeInBytes: number): string => {
  const sizeInMB = sizeInBytes / (1024 * 1024);
  const formattedSize = new Intl.NumberFormat().format(Number(sizeInMB.toFixed(0)));
  return `${formattedSize} MB`;
  // return (sizeInBytes / (1024 * 1024)).toFixed(0) + ' MB';
};

// 表格接口
interface FileInfo {
  tax_id: string | number; // 根据实际类型调整
  size: number; // 假设是数字类型
  count: number; // 假设是数字类型
  filename: string;
  md5: string;
}

// 从服务端查询datainfo
const loading_page = ref(true)
const fileinfoData = ref<FileInfo[]>([]);
const queryFileinfo = async () => {
  fileinfoData.value = []
  try {
    loading_page.value = true
    const FileinfoResponse = await fetch('/tips_api/get_file_info/', {
      method: 'get',
      headers: { 'Content-Type': 'application/json', 'uuid': uuidStore.uuid },
    });
    if (FileinfoResponse.ok) {
      const data = await FileinfoResponse.json();
      fileinfoData.value = data.map((item: any) => ({
        ...item,
        size: formatFileSize(item.size)
      }));
      loading_table.value = false
    } else {
      ElMessage.error('Unable to connect to server!');
      return;
    }
  } catch (error) {
    console.error('Error:', error)
  }
}

// 过滤数据
const searchQuery = ref('');
const filteredData = computed(() => {
  if (!searchQuery.value) return fileinfoData.value;
  const query = searchQuery.value.toLowerCase();
  return fileinfoData.value.filter(item =>
    item.tax_id.toString().toLowerCase().includes(query) ||
    item.filename.toLowerCase().includes(query)
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

// 进入页面时查询数据
onMounted(() => {
  queryFileinfo();
})

</script>

<style scoped>
.info-text {
  max-width: 1100px;
  text-align: justify;
  font-family: "Helvetica", Times, Sans-serif;
  font-size: 22px;
  line-height: 1.4;
  margin-top: 1px;
  margin-bottom: 10px;
}

.container {
  padding: 8px;
  justify-content: center;
  box-sizing: border-box;
  max-width: 1100px;
  text-align: left;
  line-height: 1.4;
  padding-top: 0px;
  margin: 0 auto;
}

.dot-heading {
  position: relative;
  padding-left: 20px;
  margin-top: 20px;
  margin-bottom: 5px;
  /* 为圆点留出空间 */
}

.dot-heading::before {
  content: '';
  position: absolute;
  left: 0;
  /* 圆点距离左侧的距离 */
  top: 50%;
  /* 垂直居中 */
  transform: translateY(-50%);
  /* 垂直居中调整 */
  width: 10px;
  /* 圆点的宽度 */
  height: 10px;
  /* 圆点的高度 */
  background-color: #000000;
  /* 圆点的颜色 */
  border-radius: 50%;
  /* 圆点形状 */
}
</style>
