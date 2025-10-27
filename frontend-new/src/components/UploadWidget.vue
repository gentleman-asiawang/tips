<template>
    <el-upload class="upload-demo" drag :limit="1" :before-upload="beforeAvatarUpload" accept=".pdb"
        :on-remove="handleRemove" action="/tips_api/receive_file/" ref="upload" :on-exceed="handleExceed"
        :headers="{ 'File-Type': props.FileType, 'uuid': uuidStore.uuid }" :on-change="handleFileChange"
        v-model:file-list="fileList" :on-success="handelSucceed">
        <el-icon color="#8A2BE2"><upload-filled /></el-icon>
        <br>
        <el-text>Drop file here or</el-text><el-text class="mx-1" color="#8A2BE2"><em>click to
                upload</em></el-text>
    </el-upload>
</template>

<script lang="ts" setup>
// 接收父组件传递的文件类型
const props = defineProps<{
    FileType: string;
}>();



// 导入模块
import { ref } from 'vue';
import { ElMessage } from 'element-plus';
import type { UploadInstance, UploadProps, UploadRawFile, UploadUserFile } from 'element-plus';

// 导入uuid
import { useUuidStore } from '@/stores/uuid';
const uuidStore = useUuidStore();

// 限制上传文件的大小
const beforeAvatarUpload: UploadProps['beforeUpload'] = (rawFile) => {
    console.log(fileList.value)
    if (rawFile.size / 1024 / 1024 > 10) {
        ElMessage.error('Sequence files cannot be larger than 10MB!');
        return false;
    }
    return true;
}
// 处理文件超出限制的情况
const upload = ref<UploadInstance | null>(null); // 确保 upload 可以为 null
const handleExceed: UploadProps['onExceed'] = (files) => {
    upload.value!.clearFiles()
    const file_new = files[0] as UploadRawFile
    upload.value!.handleStart(file_new)
    upload.value!.submit()
}
// 定义 emit
const emit = defineEmits(['fileChange']);
// 文件变化时，发送事件通知父组件
const handleFileChange = () => {
    console.log("file change")
    console.log(fileList.value)
    emit('fileChange', "1"); // 存在文件时，使值不为空
};

// 文件移除时，清除文件状态
const handleRemove = () => {
    console.log("file remove")
    emit('fileChange', null); // 文件移除时，发送空值给父组件
};

const handelSucceed = () => {
    console.log("file upload succeed")
}

// 示例文件
const initialFileList = [
  {
    name: '6RKF_A.pdb',
    url: '/data/Data/Example/6RKF_A.pdb'
  }
];
const fileList = ref<UploadUserFile[]>([])
// 使用示例
const fillInput = () => {
    fileList.value = [...initialFileList];
};

const getfileList = () => {
    if (fileList.value[0]) {
        const value =  fileList.value[0]
        if (value.raw){
            return 1 // 正常数据
        }else{
            return 2 // 示例数据
        }
    }else{
        return 0 // 空数据
    }
}

// 暴露 子组件 方法
defineExpose({
  getfileList, // 返回当前的 fileList
  fillInput
});
</script>

<style scoped>
:deep(.ep-upload .ep-upload-dragger) {
    padding-top: 12px;
    height: 70px;
}

:deep(.ep-upload-list) {
    margin-bottom: 10px !important;
}
</style>