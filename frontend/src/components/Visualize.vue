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
                    The protein ID can be found in the master table (List_of_proteinIDs_with_structures.tsv) on the download page.
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
        let response
        loading.value = true
        response = await fetch('/tips_api/query_by_id/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                id: idinput.value
            }),
        })
        // 检查响应状态
        if (!response.ok) {
            // 根据响应状态码处理不同的情况
            if (response.status === 404) {
                const errorData = await response.json();
                ElMessage.error(errorData.error || 'Tips ID not found.');
            } else {
                ElMessage.error('Network response was not ok!');
            }
            loading.value = false;
            return;
        }
        const data = await response.json()
        out_data.value = data
        loading.value = false
        handleTargetClick(data.pid, 'visualize')
        console.log(data)
    } catch (error) {
        ElMessage.error('Error occurred while fetching data.');
        console.error('Error:', error)
    } finally {
        loading.value = false; // 确保加载状态在完成后按钮被释放
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