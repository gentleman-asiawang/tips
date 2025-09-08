<!-- <template>
  <div ref="chartRef"></div>
</template>

<script setup lang="ts">
import * as d3 from 'd3';
import { ref, onMounted, watch } from 'vue';
import { getLogger } from '@/utils/logger';

const log = getLogger('BlastCircos.vue');
log.setLevel('debug');

const props = defineProps<{
  data: Array<{
    queryId: string
    targetId: string
    query_len: number
    hitchrlen: number
    qstart: number
    qend: number
    tstart: number
    tend: number
    bitScore: number
    identity: number
    evalue: string
    gaps: number
  }>
}>()

const chartRef = ref()

const width = 800
const height = 800
const innerRadius = 500
const outerRadius = 250

function drawCircos(blastData: any) {
  log.debug('Drawing circos with data:', blastData);
  if (!chartRef.value) return;
  d3.select(chartRef.value).selectAll('*').remove(); // 清空旧图形
  const svg = d3.select(chartRef.value)
    .append('svg')
    .attr('width', width)
    .attr('height', height)

  const g = svg.append('g')
    .attr('transform', `translate(${width / 2}, ${height / 2})`)

  // 显示 query 弧形
  g.append('circle')
    .attr('r', outerRadius)
    .attr('fill', 'none')
    .attr('stroke', '#ccc')

  // 提取所有染色体（target）和 query 的唯一 ID
  const targetMap: Record<string, number> = {};
  const queryMap: Record<string, number> = {};

  blastData.forEach((hsp: any) => {
    const { targetId, hitchrlen, queryId, query_len } = hsp;

    if (!(targetId in targetMap)) {
      targetMap[targetId] = hitchrlen;
    }

    if (!(queryId in queryMap)) {
      queryMap[queryId] = query_len;
    }
  });

  const targets = Object.entries(targetMap).map(([id, len]) => ({
    targetId: id,
    hitchrlen: len
  }));

  const queries = Object.entries(queryMap).map(([id, len]) => ({
    queryId: id,
    query_len: len
  }));

  console.log({ targets, queries });
}

onMounted(() => {
  drawCircos(props.data)
})
</script>

<style scoped>
/* 你可以为 tooltip 添加样式 */
</style> -->
