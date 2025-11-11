<template>
    <el-backtop :right="30" :bottom="50" />
    <div class="custom-div">
        <div style="min-height: 20ch;"></div>
        <el-row>
            <el-col :span="4"></el-col>
            <el-col :span="16" style="text-align: left;font-size: 40px; font-family: 'Helvetica', Times, serif;">
                <span><b>Visualize protein structure</b></span>
            </el-col>
            <el-col :span="4"></el-col>
        </el-row>
        <div style="min-height: 0px;"></div>
        <el-row>
            <el-col :span="4"></el-col>
            <el-col :span="16" class="info-text">
                <p>
                    The protein ID can be found in the master table (List_of_proteinIDs_with_structures.tsv) on the
                    download page.
                </p>
            </el-col>
            <el-col :span="4"></el-col>
        </el-row>
        <el-row>
            <el-col :span="4"></el-col>
            <el-col :span="14">
                <el-input v-model="idinput" style="width: 100%;height: 70px;" placeholder="Enter a protein ID" />
                <div style="margin-top: 6px;text-align: left;">
                    <span style="margin-right: 5px; font-size: 15px;">Try an example:</span>
                    <el-button @click="fillId" color="#626aef" size="small" plain>P005083005466</el-button>
                </div>
            </el-col>
            <el-col :span="2" style="text-align: left;">
                <el-button color="#8A2BE2" type="primary" :icon="Search" :loading @click="submitid"
                    style="width: 50px;"></el-button>
            </el-col>
            <el-col :span="4"></el-col>
        </el-row>
    </div>
</template>

<script lang="ts" setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import { Search } from '@element-plus/icons-vue';
import axios from 'axios';
const idinput = ref('')
const loading = ref(false)
const out_data = ref()

// 加载示例
const fillId = () => {
    idinput.value = 'P005083005466'; // 更新输入框的值
};

// 展示蛋白
const router = useRouter();
const handleTargetClick = (target: string, source: string) => {
    router.push({ name: 'Viewstr', params: { target, source } });
    console.log(target)
};

// 提交按钮
const submitid = async () => {
    if (!idinput.value) {
        ElMessage.error('Please input id!');
        return;
    }
    try {
        loading.value = true
        const response = await axios.get('/tips_api/query_by_id/', {
            params: { id: idinput.value }
        });
        out_data.value = response.data;
        handleTargetClick(response.data.pid, 'visualize');
    } catch (error: any) {
        if (error.response) {
            // 后端返回非 2xx
            if (error.response.status === 404) {
                ElMessage.error(error.response.data.error || 'Tips ID not found.');
            } else {
                ElMessage.error(`Request failed with status ${error.response.status}`);
            }
        } else if (error.request) {
            // 请求已发出但没有收到响应
            ElMessage.error('No response from server.');
        } else {
            // 其他错误
            ElMessage.error(`Error: ${error.message}`);
        }
        console.error('Axios error:', error);
    } finally {
        loading.value = false; // 无论成功还是失败都关闭加载状态
    }
}
</script>

<style scoped>
.info-text {
    font-family: "Helvetica", Times, Sans-serif;
    margin-top: 0px;
    max-width: 1200px;
    text-align: left;
    font-size: 22px;
    line-height: 1.3;
}
</style>