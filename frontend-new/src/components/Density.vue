<template>
  <el-radio-group v-model="type">
    <el-radio value="SNP">SNP</el-radio>
    <el-radio value="INDEL">INDEL</el-radio>
  </el-radio-group>
  <div ref="svgRef"></div>
</template>

<script setup lang="ts">
import * as d3 from 'd3'
import { onMounted, ref, watch } from 'vue'
import { useChromStore } from '@/stores/baseinfo'
import axios from 'axios'
import { useUuidStore } from '@/stores/uuid';
import { getLogger } from '@/utils/logger';
const log = getLogger('Density.vue'); // 当前组件名

// import uuid 
const uuidStore = useUuidStore();

// import chromosome data
const chromStore = useChromStore()
const chromNames = chromStore.chromNames
const chromLengths = chromStore.chromLengths

const svgRef = ref()
const snpData = ref<Record<string, number[]>>({})  // {Chr1: [12, 34, ...]}
const type = ref('SNP')

const fetchSnpDensity = async (dataType: string) => {
  try {
    const response = await axios.get('/maizevarmap_api/get_density_data/', {
      headers: { uuid: uuidStore.uuid },
      params: { type: dataType }
    });
    snpData.value = response.data
  } catch (e) {
    log.error('Failed to retrieve density information:', e)
  }
}


log.debug('type:', type.value)

/** 绘制染色体密度图 */
const drawChart = () => {
  const width = svgRef.value.clientWidth
  const height = 650
  const margin = { top: 10, right: 10, bottom: 200, left: 2 }
  const spacing = 60
  if (!svgRef.value) return

  const svg = d3.select(svgRef.value)
    .html('') // 清空之前的内容
    .append('svg')
    .attr('width', '100%')
    .attr('height', height)
    .attr('viewBox', `0 0 ${width} ${height}`)
    .attr('preserveAspectRatio', 'xMinYMin meet')

  const chromData = chromNames.map(name => ({
    chrom: name,
    length: chromLengths[name],
    bins: snpData.value[name] || [],
  }))

  const maxLength = d3.max(chromData, d => d.length) || 1
  const maxSnp = d3.max(chromData.flatMap(d => d.bins)) || 1

  const colorScale = d3.scaleSequential(d3.interpolateBlues)
    .domain([0, maxSnp])

  const barWidth = (width - margin.left - margin.right - (chromData.length - 1) * spacing) / chromData.length


  chromData.forEach((chrom, index) => {
    const x = margin.left + index * (barWidth + spacing)
    const y = margin.top
    const chromHeight = height - margin.top - margin.bottom
    const scaleY = d3.scaleLinear().domain([0, maxLength]).range([0, chromHeight])
    const scaledHeight = scaleY(chrom.length)

    // 绘制染色体外框
    svg.append('rect')
      .attr('x', x)
      .attr('y', y)
      .attr('width', barWidth)
      .attr('height', scaledHeight)
      .attr('fill', '#eee')
      .attr('stroke', '#333')
      .attr('rx', 4)

    // 绘制每个 bin 的密度色块
    const binHeight = scaledHeight / (chrom.bins.length || 1)
    chrom.bins.forEach((snpCount, binIndex) => {
      const binStart = 300000 * binIndex
      const binEnd = binIndex === chrom.bins.length - 1 ? chrom.length : 300000 * (binIndex + 1)

      svg.append('rect')
        .attr('x', x)
        .attr('y', y + binIndex * binHeight)
        .attr('width', barWidth)
        .attr('height', binHeight)
        .attr('fill', colorScale(snpCount))
        .append('title') // 鼠标悬停显示数量
        .text(`Bin ${binIndex + 1}: ${snpCount} SNPs\nRange: ${binStart.toFixed(0)} - ${binEnd.toFixed(0)}`)
    })

    // 标签
    svg.append('text')
      .attr('x', x + barWidth / 2)
      .attr('y', y + scaledHeight + 20)
      .attr('text-anchor', 'middle')
      .attr('font-size', 16)
      .text(chrom.chrom)



    /*** ✅✅✅ 加入图例部分 ***/

    // 渐变定义
    const defs = svg.append('defs');
    const gradient = defs.append('linearGradient')
      .attr('id', 'legend-gradient')
      .attr('x1', '0%')
      .attr('y1', '0%')
      .attr('x2', '100%')
      .attr('y2', '0%');

    gradient.append('stop')
      .attr('offset', '0%')
      .attr('stop-color', colorScale(0));

    gradient.append('stop')
      .attr('offset', '100%')
      .attr('stop-color', colorScale(maxSnp));

    // 图例容器
    const legendWidth = 400;
    const legendHeight = 20;
    const legendMarginTop = 30; // 距离底部条形图的距离

    const legendGroup = svg.append('g')
      .attr('transform', `translate(${width - margin.right - legendWidth - 20}, ${height - margin.bottom + legendMarginTop})`);

    // 色条
    legendGroup.append('rect')
      .attr('width', legendWidth)
      .attr('height', legendHeight)
      .style('fill', 'url(#legend-gradient)');

    // 刻度（用实际数量）
    const legendScale = d3.scaleLinear()
      .domain([0, maxSnp])
      .range([0, legendWidth]);

    const legendAxis = d3.axisBottom(legendScale)
      .ticks(0) // 均分5段
      .tickValues([0, maxSnp]) // 只显示0和maxSnp
      .tickFormat(d => `${Math.round(+d)}`); // 显示整数数量

    legendGroup.append('g')
      .attr('transform', `translate(0, ${legendHeight})`)
      .call(legendAxis)
      .selectAll('text')
      .attr('font-size', 14)

    // 图例标题
    legendGroup.append('text')
      .attr('x', legendWidth / 2)
      .attr('y', -6)
      .attr('text-anchor', 'middle')
      .attr('font-size', 16)
      .text(`${type.value} Density(count)`);

  })
}

onMounted(async () => {
  await fetchSnpDensity(type.value)
  drawChart()
})

watch(type, async (newType) => {
  await fetchSnpDensity(newType)
  drawChart()
})
watch(snpData, () => {
  drawChart()
})
</script>

<style scoped>
svg {
  background: #fafafa;
  border: 1px solid #ddd;
  border-radius: 8px;
}
</style>