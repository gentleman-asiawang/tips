<template>
    <el-page-header v-on:back="goBack" style="margin-bottom: 5px;margin-left: 10px;margin-right: 10px;">
        <template #content>
            <div v-if="out_data" class="flex items-center flex-no-wrap">
                <span class="header-text"><b>PID:</b> {{ out_data.pid }}</span>
                <el-divider direction="vertical" border-style="dashed" style="margin: 0 6px;" />
                <span class="header-text"><b>Species:</b> {{ out_data.species }}</span>
                <el-divider direction="vertical" border-style="dashed" style="margin: 0 6px;" />
                <el-tooltip v-if="isTruncated" class="item" effect="dark" :content="out_data.description"
                    placement="bottom">
                    <span class="header-text description" ref="descriptionRef"><b>Description:</b> {{
                        out_data.description }}</span>
                </el-tooltip>
                <span v-else class="header-text description" ref="descriptionRef"><b>Description:</b> {{
                    out_data.description }}</span>
            </div>
        </template>
        <template #extra>
            <div class="flex items-center">
                <el-button @click="downloadpdb" size="small" type="primary" :loading="loading_download">
                    Download Structure<el-icon class="el-icon--right">
                        <Download />
                    </el-icon>
                </el-button>
            </div>
        </template>
    </el-page-header>
    <el-divider style="margin-bottom: 5px; margin-top: 5px;" />
    <div id="viewer"></div>
    <div class="legend">
        <div class="legend-item">
            <div style="background-color: #0053d6; width: 20px;height: 20px;margin-right: 5px;"></div>
            <span>Very high (pLDDT > 90)</span>
        </div>
        <div class="legend-item">
            <div style="background-color: #65cbf3; width: 20px;height: 20px;margin-right: 5px;"></div>
            <span>High (90 > pLDDT > 70)</span>
        </div>
        <div class="legend-item">
            <div style="background-color: #ffdb13; width: 20px;height: 20px;margin-right: 5px;"></div>
            <span>Low (70 > pLDDT > 50)</span>
        </div>
        <div class="legend-item">
            <div style="background-color: #ff7d45; width: 20px;height: 20px;margin-right: 5px;"></div>
            <span>Very low (pLDDT < 50)</span>
        </div>
    </div>
    <div style="margin-top: 5px;">
        <span>
            The predicted local distance difference test (pLDDT), on a scale from 0 to 100, is a per-residue confidence
            score.
        </span>
    </div>
</template>

<script lang="ts" setup>
import { Download } from '@element-plus/icons-vue'
import { ref, onMounted, watch, nextTick } from 'vue';
import { useRouter } from 'vue-router'
import { useUuidStore } from '@/stores/uuid';
import { ElMessage } from 'element-plus';
import axios from 'axios';

const router = useRouter()
const uuidStore = useUuidStore();

// 省略时显示toolstip
const descriptionRef = ref<HTMLElement | null>(null);
const isTruncated = ref(false);
const checkTruncation = async () => {
    await nextTick(); // 确保 DOM 更新
    if (descriptionRef.value) {
        isTruncated.value = descriptionRef.value.scrollWidth > descriptionRef.value.clientWidth;
    }
};

// 接收父组件传递的文件名
const props = defineProps<{
    target: string;
    source: string
}>();

//let viewerInstance: PDBeMolstarPlugin | null = null;
let viewerInstance: ReturnType<typeof PDBeMolstarPlugin> | null = null;

// 封装渲染逻辑到一个函数
const load3DStructure = () => {
    if (!viewerInstance) {
        viewerInstance = new PDBeMolstarPlugin();
    }

    const options = {
        alphafoldView: true,
        sequencePanel: true,
        leftPanel: false,
        loadingOverlay: true,
        landscape: true,
        bgColor: 'white',
        customData: {
            url: `/tips_api/get_pdb_file/?tipsid=${props.target}`,
            format: 'pdb',
            binary: false,
        },
        hideCanvasControls: ['expand', 'controlToggle']
    };

    const viewerContainer = document.getElementById('viewer');
    if (viewerContainer && viewerInstance) {
        viewerInstance.render(viewerContainer, options);
    }
};

// 从数据库查询信息
const out_data = ref()
const querybyid = async () => {
    try {
        const response = await axios.get('/tips_api/query_by_id/', {
            params: { id: props.target }
        });
        out_data.value = response.data;
        await nextTick();
        checkTruncation();
    } catch (error) {
        console.error('Error:', error)
    }
}

// 监听 target 的变化来重新加载数据
watch(() => props.target, () => {
    load3DStructure();    // 加载新的 3D 数据
    querybyid();
});
onMounted(() => {
    load3DStructure();
    querybyid();
})

// 返回按钮
function goBack() {
    router.push(`/${props.source}`)

}

// 下载pdb文件
const loading_download = ref(false)
const downloadpdb = async () => {
    try {
        loading_download.value = true
        // 构建 GET 请求参数
        const tipsIds = Array.isArray(props.target) ? props.target : [props.target];
        const response = await axios.post(
            '/tips_api/download_data/',
            {
                tips_id: tipsIds,
                sequence: false
            },
            {
                headers: {
                    uuid: uuidStore.uuid
                },
                responseType: 'blob'
            }
        );
        // 生成下载
        const blob = new Blob([response.data], { type: 'application/octet-stream' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        a.download = `${props.target}.pdb`; // 设置下载的文件名
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
    } catch (error) {
        ElMessage.error('Error downloading selected targets');
        console.error(error);
    } finally {
        loading_download.value = false
    }
}
</script>

<style scoped>
#viewer {
    position: relative;
    height: 85vh;
}

.header-text {
    font-size: 13px;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    white-space: nowrap;
    /* 不换行 */
}

.description {
    display: block;
    max-width: 100%;
    /* 设置最大宽度 */
    overflow: hidden;
    /* 超出隐藏 */
    text-overflow: ellipsis;
    /* 添加省略号 */
}

.legend {
    justify-content: center;
    margin-top: 8px;
    display: flex;
    align-items: center;
}

.legend-item {
    display: flex;
    margin-right: 30px;
}

.flex-no-wrap {
    display: flex;
    flex-wrap: nowrap;
    align-items: center;
}
</style>