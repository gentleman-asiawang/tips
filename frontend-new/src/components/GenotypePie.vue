<script setup lang="ts">
import { ref, watch } from 'vue'
import { Pie } from 'vue-chartjs'
import {
  Chart as ChartJS,
  Title, Tooltip, Legend,
  ArcElement,
} from 'chart.js'

ChartJS.register(Title, Tooltip, Legend, ArcElement)

// Props: 输入 binaryData 数据
const props = defineProps<{
  binaryData: { genotype: string }[] | undefined
}>()

const chartData = ref({
  labels: [] as string[],
  datasets: [{
    data: [] as number[],
    backgroundColor: [] as string[],
  }]
})

// 响应数据变化
watch(() => props.binaryData, (newData) => {
  if (!newData || newData.length === 0) return

  const counts: Record<string, number> = {}
  newData.forEach(item => {
    counts[item.genotype] = (counts[item.genotype] || 0) + 1
  })
  const sorted = Object.entries(counts)
    .sort((a, b) => b[1] - a[1]) // 降序排序
  const labels = sorted.map(([label]) => label)
  const data = sorted.map(([_, count]) => count)
  const colors = sorted.map((_, i) => `hsl(${i * 50}, 70%, 60%)`)

  chartData.value = {
    labels,
    datasets: [{
      data,
      backgroundColor: colors,
    }]
  }
}, { immediate: true })
</script>


<template>
  <div v-if="chartData.labels.length > 0">
    <Pie :data="chartData" />
  </div>
  <div v-else>
    <p>No data available</p>
  </div>
</template>