<template>
    <el-backtop :right="30" :bottom="50" />
    <el-scrollbar>
        <div style="min-height: 20ch;"></div>
        <div class="custom-div">
            <el-row>
                <el-col :span="4"></el-col>
                <el-col :span="16" style="text-align: left;font-size: 40px; font-family: 'Helvetica', Times, serif;">
                    <span><b>Search By Structure</b></span>
                </el-col>
                <el-col :span="4"></el-col>
            </el-row>
            <div style="min-height: 20px;"></div>
            <el-row>
                <el-col :span="4"></el-col>
                <el-col :span="3">
                    <el-select v-model="foldseek_db_select" placeholder="Select">
                        <el-option v-for="item, index in transferData" :key="index" :label="item.orders"
                            :value="item.orders" />
                    </el-select>
                </el-col>
                <el-col :span="11">
                    <UploadWidget ref="uploadComponent" @fileChange="handleFileChange" FileType="pdb" />
                    <div style="margin-top: 6px;text-align: left;">
                        <span style="margin-right: 5px; font-size: 15px;">Try an example:</span>
                        <el-button @click="useSample" color="#626aef" size="small" plain>6RKF_A.pdb</el-button>
                    </div>
                </el-col>
                <el-col :span="2" style="text-align: left;">
                    <el-button class="search_button" color="#8A2BE2" type="primary" :icon="Search"
                        :loading="loading_search" @click="submitFoldseek" style="width: 50px;"></el-button>
                </el-col>
                <el-col :span="4"></el-col>
            </el-row>
            <div v-if="loading_search" v-loading="loading_search" style="height: 40vh;"></div>
            <div v-if="outisnone">
                <el-divider />
                <el-empty description="No matching data found!" :image-size="300" />
            </div>
            <div v-if="tableData.length">
                <el-divider />
                <div style="margin-bottom: 20px; display: flex; justify-content: flex-end;">
                    <el-button color="#8A2BE2" type="primary" :icon="Download" :loading="loading_download"
                        @click="downloadselect">
                        Download Table
                    </el-button>
                </div>

                <el-table :data="paginatedData" :stripe="true" style="width: 100%" :highlight-current-row="true"
                    show-overflow-tooltip :header-cell-style="{ backgroundColor: '#EBEDF0' }">
                    <!-- <el-table-column type="selection" width="55" /> -->
                    <el-table-column label="Target" prop="target">
                        <template #default="{ row }">
                            <span @click="handleTargetClick(row.target, 'bystructure')"
                                style="color: #409EFF; cursor: pointer;">
                                {{ row.target }}
                            </span>
                        </template>
                    </el-table-column>
                    <el-table-column prop="description" min-width="200px">
                        <template #header>
                            <div style="display: flex; align-items: center;">
                                <span>Description</span>
                                <el-tooltip content="Description derived from structure-based annotation."
                                    placement="top">
                                    <el-icon color="#409EFF" style="margin-left: 3px;">
                                        <InfoFilled />
                                    </el-icon>
                                </el-tooltip>
                            </div>
                        </template>
                    </el-table-column>
                    <el-table-column label="Species" prop="scientificname" min-width="100px" />
                    <el-table-column label="TM-score" prop="alntmscore" min-width="50px" />
                    <el-table-column label="Seq. Id." prop="fident" min-width="50px" />
                    <el-table-column label="Evalue" prop="evalue" />
                    <el-table-column label="Query Pos.(Cov)">
                        <template #default="{ row }">
                            {{ row.qstart }}-{{ row.qend }}({{ row.qcov }})
                        </template>
                    </el-table-column>
                    <el-table-column label="Target Pos.(Cov)">
                        <template #default="{ row }">
                            {{ row.tstart }}-{{ row.tend }}({{ row.tcov }})
                        </template>
                    </el-table-column>
                </el-table>
                <el-pagination @current-change="handleCurrentChange" :current-page="currentPage" :page-size="pageSize"
                    :total="totalItems" layout="total, prev, pager, next, jumper" />
            </div>
        </div>
    </el-scrollbar>


</template>

<script lang="ts" setup>
import { ref, computed } from 'vue';
import UploadWidget from '~/components/layouts/UploadWidget.vue'
import { ElMessage, type UploadRawFile } from 'element-plus';
import { useInfoStore, useUuidStore } from '~/store/globalStore';
import { Download, Search } from '@element-plus/icons-vue';
import { useRouter } from 'vue-router';
const router = useRouter();
const uuidStore = useUuidStore();
const tableData = ref([])
const uploadedFile = ref<UploadRawFile | null>(null);
const elapsedTime = ref(0)

// 加载示例
interface MyUploadComponent { // 定义组件的类型
    fillInput: () => void;
    getfileList: () => void;
}
const uploadComponent = ref<MyUploadComponent | null>(null);
const useSample = () => {
    if (uploadComponent.value) {
        uploadComponent.value.fillInput(); // 调用 fillInput 方法
    }
};

// 展示蛋白
const handleTargetClick = (target: string, source: string) => {
    router.push({ name: 'Viewstr', params: { target, source } });
    console.log(target)
};

// 选择数据库
const tips_info = useInfoStore()
const transferData = ref([
    { orders: 'All', pictures: '' }, // 添加 "all" 项，图片可以留空或者提供默认值
    ...tips_info.orders, // 其余的 orders
]);
const foldseek_db_select = ref<string>("All");

// 下载所选
const loading_download = ref(false)
const downloadselect = async () => {
    try {
        loading_download.value = true
        const response = await fetch('/tips_api/download_table/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'uuid': uuidStore.uuid
            },
            body: JSON.stringify({ download_type: 'foldseek' }),
        });
        if (!response.ok) {
            loading_download.value = false
            ElMessage.warning('Network response was not ok!');
        }
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        a.download = 'foldseekout.xlsx'; // 设置下载的文件名
        loading_download.value = false
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
    } catch (error) {
        ElMessage.error('Error downloading selected targets');
        console.error(error);
    }
}

// 文件改变时的逻辑
const handleFileChange = (file: UploadRawFile | null) => {
    uploadedFile.value = file; // 更新上传文件的状态
};

// 提交按钮的逻辑
const loading_search = ref(false)
const outisnone = ref(false)

const submitFoldseek = async () => {
    const currentfile = uploadComponent.value?.getfileList()

    if (!currentfile) {
        ElMessage.error('No file uploaded!');
        return;
    }
    tableData.value = []
    try {
        loading_search.value = true
        outisnone.value = false
        const serverloadResponse = await fetch('/tips_api/get_server_load/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'uuid': uuidStore.uuid }
            });
        // 处理获取服务器负载接口的结果
        if (serverloadResponse.ok) {
            const serverLoad = await serverloadResponse.json();
            if (serverLoad.serverload === 'high') {
                ElMessage.error('Current server load: high');
            } else if (serverLoad.serverload === 'medium') {
                ElMessage.warning('Current server load: medium');
            } else {
                ElMessage.success('Current server load: low');
            }
        } else {
            console.warn('Pre-processing interface failed or encountered an error.');
        }
        const startTime = Date.now();


        // 第二个请求：查询蛋白序列
        let sample
        if (currentfile === 2) {
            sample = true
        } else {
            sample = false
        }

        const mainResponse = await fetch('/tips_api/query_by_pdb/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'uuid': uuidStore.uuid },
            body: JSON.stringify({ foldseek_db: foldseek_db_select.value, sample: sample }),
        })
        if (!mainResponse.ok) {
            loading_search.value = false;
            ElMessage.error('Please check your input data!');
            return;
        }
        const data = await mainResponse.json()
        tableData.value = data || []
        currentPage.value = 1
        loading_search.value = false
        const endTime = Date.now();
        elapsedTime.value = endTime - startTime;
        if (tableData.value.length === 0) {
            outisnone.value = true
            ElMessage.warning('No matching data found!');
        }
        console.log(elapsedTime)
    } catch (error) {
        console.error('Error:', error)
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

</script>

<style scoped>
:deep(.ep-col .ep-select .ep-select__wrapper) {
    height: 40px !important;
}

:deep(.ep-col .search_button) {
    width: 5px !important;
    border-left: 0px;
    padding-left: 50px;
    padding-right: 50px;
}

:deep(.ep-empty__description p) {
    font-size: 20px !important;
}
</style>