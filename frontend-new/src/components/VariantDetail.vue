<template>
  <el-page-header v-on:back="goBack" style="margin-bottom: 5px;margin-left: 10px;margin-right: 10px;">
    <template #content>
      <span class="header-text"><b>Variant ID:</b> {{ props.target }}</span>
      <el-divider direction="vertical" />
      <el-button type="primary" @click="jumpToVariant">Jbrowse</el-button>
    </template>
  </el-page-header>
  <el-divider style="margin-bottom: 5px; margin-top: 5px;" />
  <h2 class="dot-heading">Detailed information for {{ props.target }}:</h2>
  <el-descriptions size="large" :column="2" border>
    <el-descriptions-item label="Variant ID">{{ props.target }}</el-descriptions-item>
    <el-descriptions-item label="Variation Type">{{ summary?.type }}</el-descriptions-item>
    <el-descriptions-item label="Chromosome">{{ summary?.chr }}</el-descriptions-item>
    <el-descriptions-item label="Position">{{ summary?.pos }}</el-descriptions-item>
    <el-descriptions-item label="Ref">
      {{ summary?.alleles?.[0] ?? '-' }}
    </el-descriptions-item>
    <el-descriptions-item label="Alt">
      {{ summary?.alleles?.slice(1).join(', ') || '-' }}
    </el-descriptions-item>
    <el-descriptions-item label="Primary Allele">
      {{ sortedAlleles[0]?.allele ?? '-' }}
    </el-descriptions-item>
    <el-descriptions-item label="Secondary Allele">
      {{ sortedAlleles[1]?.allele ?? '-' }}
    </el-descriptions-item>
  </el-descriptions>
  <h2 class="dot-heading">Flanking Sequence (100 bp) in Reference Genome:</h2>
  <el-descriptions direction="vertical" :column="1" size="large" border>
    <el-descriptions-item label="sequence">
      <div class="sequence-block">
        <span>{{ summary?.up_sequence }}</span><span class="middle-sequence">[{{ summary?.alleles?.[0] ?? '-' }}/{{
          summary?.alleles?.slice(1).join(',') || '-' }}]</span><span>{{ summary?.down_sequence }}</span>
      </div>
    </el-descriptions-item>
    <el-descriptions-item label="Reverse complement sequence">
      <div class="sequence-block">
        <span>{{ reverseUpSequence }}</span><span class="middle-sequence">[{{ reverseAlleles[0] }}/{{
          reverseAlleles.slice(1).join(',') || '-' }}]</span><span>{{ reverseDownSequence }}</span>
      </div>
    </el-descriptions-item>
  </el-descriptions>
  <h2 class="dot-heading">Allele Frequencies:</h2>
  <el-table :data="tableRows" :stripe="true" style="width: 100%" :highlight-current-row="true" show-overflow-tooltip
    :header-cell-style="{ backgroundColor: '#EBEDF0' }">
    <!-- 第一列：群体名称 -->
    <el-table-column prop="label" label="Populations" min-width="30px" />
    <!-- 第二列：群体样本数 -->
    <el-table-column prop="populationCount" label="Pop Size" min-width="40px" />
    <!-- 动态渲染 allele 列 -->
    <el-table-column v-for="(allele, index) in summary?.alleles" :key="index" :prop="`col_${index}`">
      <template #header>
        Frequency of <span style="color: green">{{ allele }}</span>
      </template>
    </el-table-column>
  </el-table>
  <h2 class="dot-heading">Allele Effect:</h2>
  <el-table :data="efftableData" :stripe="true" style="width: 100%" :highlight-current-row="true" show-overflow-tooltip
    :header-cell-style="{ backgroundColor: '#EBEDF0' }">
    <el-table-column label="Var ID" prop="variantid" min-width="30px" />
    <el-table-column label="Var" prop="variant" min-width="40px" />
    <el-table-column label="Locus" prop="locus" min-width="80px" />
    <el-table-column label="Annotation" prop="annotation" min-width="50px" />
    <el-table-column label="Putative impact" prop="putative_impact" />
    <el-table-column label="Distance to feature" prop="distance_to_feature" min-width="40px" />
  </el-table>

</template>

<script lang="ts" setup>
import { ref, onMounted, watch, nextTick, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useUuidStore } from '@/stores/uuid';
import { useSamplesinfoStore } from '@/stores/baseinfo';
import GenotypePie from '@/components/GenotypePie.vue';
import axios from 'axios';
import { getLogger } from '@/utils/logger';
const log = getLogger('VariantDetail.vue'); // 当前组件名

log.setLevel('debug'); // 只打开这个组件的调试日志


const router = useRouter();
const uuidStore = useUuidStore();
const samplesinfoStore = useSamplesinfoStore()

interface PopulationSummary {
  population: string;
  population_count: string;
  ac: string;
}

interface snpeffData {
  alt: string;
  annotation: string;
  putative_impact: string;
  gene_name: string;
  gene_id: string;
  feature_type: string;
  feature_id: string;
  transcript_biotype: string;
  rank_total: string;
  hgvs_c: string;
  hgvs_p: string;
  cDNA_position_: string;
  cds_position_: string;
  protein_position_: string;
  distance_to_feature: string;
}

interface Variant_summary {
  chr: string;
  pos: string;
  alleles: string[];
  type: string;
  ac: number[];
  frequencies: string[];
  up_sequence: string;
  down_sequence: string;
  populations: PopulationSummary[];
  snpeffData: snpeffData[];
}
const summary = ref<Variant_summary | null>(null)

// 接收父组件传递的文件名
const props = defineProps<{
  target: string;
  source: string
}>();

function complement(base: string): string {
  const map: Record<string, string> = {
    A: 'T', T: 'A',
    C: 'G', G: 'C',
    a: 't', t: 'a',
    c: 'g', g: 'c',
    N: 'N', n: 'n'
  };
  return map[base] || base;
}

function reverseComplement(seq: string): string {
  // 特殊标记直接返回
  if (seq.startsWith('<') && seq.endsWith('>')) {
    return seq;
  }
  if (seq.startsWith('Your') && seq.endsWith('environment')) {
    return seq;
  }
  return seq.split('').reverse().map(complement).join('');
}
const reverseUpSequence = computed(() =>
  reverseComplement(summary.value?.down_sequence || '')
);
const reverseDownSequence = computed(() =>
  reverseComplement(summary.value?.up_sequence || '')
);
const reverseAlleles = computed(() => {
  return summary.value?.alleles?.map(allele => reverseComplement(allele)) ?? ['-'];
});

interface EffTableRow {
  variantid: string;
  variant: string;
  locus: string;
  annotation: string;
  putative_impact: string;
  distance_to_feature: string;
}
const efftableData = ref<EffTableRow[]>([])
const querybyid = async () => {
  try {
    const response = await axios.get('/maizevarmap_api/query_variants_byid/', {
      headers: { uuid: uuidStore.uuid },
      params: { show_id: props.target }
    })
    const rawSummary = response.data.summary;

    const altAlleles = rawSummary.alt.split(',').map((s: string) => s.trim()).filter((s: string) => s !== '');
    const alleles = [rawSummary.ref, ...altAlleles]; // REF + ALT symbols

    const an = samplesinfoStore.samplesinfoData.length * 2; // 假设每个样本有两个等位基因 allele number
    const acArray = rawSummary.ac
      .split(',')
      .map((s: string) => s.trim())
      .filter((s: string) => s !== '')
      .map((s: string) => Number(s)) as number[];

    const refCount = an - (acArray.reduce((a, b) => a + b, 0)); // 参考等位基因数目
    const acFinal = [refCount, ...acArray]; // 索引后移，0 为 REF 计数
    const frequencies = acFinal.map(ac => (ac / an).toFixed(3)); // 频率
    summary.value = {
      chr: rawSummary.chr,
      pos: rawSummary.pos,
      type: rawSummary.type,
      alleles,
      ac: acFinal,
      frequencies,
      up_sequence: rawSummary.up_sequence,
      down_sequence: rawSummary.down_sequence,
      populations: rawSummary.populations || [],
      snpeffData: rawSummary.snpeff_data || []
    }
    efftableData.value = summary.value.snpeffData.map((item: any) => ({
      variantid: props.target,
      variant: `${summary.value?.alleles?.[0] ?? '-'}->${item.alt}`,
      locus: item.gene_id,
      annotation: item.annotation,
      putative_impact: item.putative_impact,
      distance_to_feature: item.distance_to_feature,
    }));
    await nextTick();
  } catch (error) {
    log.error('Error:', error)
  }
}

const tableRows = computed(() => {
  if (!summary.value) return []
  const frequencies = summary.value.frequencies
  const populationCount = samplesinfoStore.samplesinfoData.length
  const populations = summary.value.populations as {
    population: string
    population_count: string
    ac: string
  }[]

  const result: Record<string, any>[] = []


  // 第一行：全体频率（label 为 All）
  const freqRow: Record<string, any> = {
    label: 'All',
    populationCount: populationCount
  };
  frequencies.forEach((freq, index) => {
    freqRow[`col_${index}`] = freq
  })

  result.push(freqRow)

  // 第二行起：每个群体信息
  populations.forEach((pop) => {
    const acParts = pop.ac.split(',').map(x => Number(x.trim()))
    const totalAC = acParts.reduce((sum, val) => sum + val, 0)  // 避免除以 0
    const row: Record<string, any> = {
      label: pop.population,
      populationCount: Number(pop.population_count)
    }

    acParts.forEach((value, index) => {
      let freq: string
      if (value === 0) {
        freq = '-'
      } else {
        freq = (value / totalAC).toFixed(4)
      }
      row[`col_${index}`] = freq
    })

    result.push(row)
  })

  return result
})

const sortedAlleles = computed(() => {
  if (!summary.value?.alleles || !summary.value?.ac) return [];

  return summary.value.alleles
    .map((allele, index) => ({
      allele,
      ac: summary.value?.ac[index] ?? 0
    }))
    .sort((a, b) => b.ac - a.ac);
});

onMounted(() => {
  querybyid();
})

watch(() => props.target, () => {
  querybyid();
});

// back to previous page
function goBack() {
  router.push(`/${props.source}`)
}

// 定义跳转方法
function jumpToVariant() {
  const start = Math.max(Number(summary.value?.pos) - 100, 0)
  const end = Number(summary.value?.pos) + 100
  const location = `${summary.value?.chr}:${start}..${end}`

  log.debug('Jumping to location:', location);

  router.push({
    name: 'jbrowse',
    query: {
      loc: location,
      variantid: props.target,
      source: props.source
    },
  })
}


</script>

<style scoped>
.sequence-block {
  white-space: pre-wrap;
  word-break: break-word;
  font-family: monospace;
}

.middle-sequence {
  color: green;
}
</style>