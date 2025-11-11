<template>
    <el-page-header v-on:back="goBack" style="margin-bottom: 5px;margin-left: 10px;margin-right: 10px;">
        <template #extra>
            <div class="flex items-center">
                <el-button @click="downloadtree" size="small" type="primary" :loading="loading_download">
                    Download Tree<el-icon class="el-icon--right">
                        <Download />
                    </el-icon>
                </el-button>
            </div>
        </template>
    </el-page-header>
    <el-divider style="margin-bottom: 5px; margin-top: 5px;" />
    <div id="tree"></div>
</template>

<script lang="ts" setup>
import { Download } from '@element-plus/icons-vue'
import { ref, onMounted, watch } from 'vue';
import { useTreeStore } from '@/stores/tree';
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus';

const router = useRouter()
const treeStore = useTreeStore()

// 封装渲染逻辑到一个函数
const loadtree = () => {
    console.log("load tree")
    phyloview.InitTreeLayoutStructure("#tree", {
        extension: {
            show: true,
        },
        leafs: {
            show: true,
        },
        nodes: {
            value: {
                show: false,
                mark: 'all',
                style: {
                    'font-size': '10px',
                    // "fill": "red",
                }
            },
            name: {
                show: true,
                mark: 'node',
                dy: 4,
                style: {
                    'font-size': '10px',
                }
            }
        },
        content: treeStore.target,
        layout: "tree",
        position: [200, 200],
        separation: 30,
        isWheelZoom: true
    });
};

// 接收父组件传递的文件名
const props = defineProps<{
    treeuuid: string
}>();


// 监听 uuid 的变化来重新加载数据
watch(() => props.treeuuid, () => {
    if (treeStore.hasTargetChanged()) {
        loadtree();
    }
});

onMounted(() => {
    console.log("mounted")
    loadtree();
})

// 返回按钮
function goBack() {
    router.push(`/phylogeny`)

}

// 下载nwk文件
const loading_download = ref(false)
const downloadtree = () => {
    loading_download.value = true
    const blob = new Blob([treeStore.target], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);

    const a = document.createElement('a');
    a.href = url;
    a.download = 'phylogenetic_tree.nwk'; // 设置下载文件名
    document.body.appendChild(a);
    a.click(); // 触发下载
    document.body.removeChild(a);
    URL.revokeObjectURL(url); // 释放对象 URL
    loading_download.value = false
}
</script>

<style scoped>
#tree {
    position: relative;
    height: 90vh;
}

.header-text {
    font-size: 13px;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    white-space: nowrap;
    /* 不换行 */
}

.description {
    display: block;
    max-width: 800px;
    /* 设置最大宽度 */
    overflow: hidden;
    /* 超出隐藏 */
    text-overflow: ellipsis;
    /* 添加省略号 */
}
</style>