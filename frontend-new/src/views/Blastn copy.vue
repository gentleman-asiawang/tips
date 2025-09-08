<template>
  <h2 class="dot-heading">RiceVarMap BLASTN:</h2>
  <iframe src="http://172.31.2.238/sequenceserver/" frameborder="0" width="100%" height="800"></iframe>
  <el-card>
    <el-form label-width="auto">
      <el-form-item label="Sequence:" style="width: 100%;">
        <el-input v-model="dnaseqInput" type="textarea" placeholder="Enter your sequence" :rows="5" />
      </el-form-item>
      <el-form-item label="Database:" style="width: 100%;">



        <el-select v-model="selectedBlastdb" multiple>
          <el-option v-for="db in Blastdbs" :key="db.value" :label="db.label" :value="db.value" />
        </el-select>
      </el-form-item>
      <el-row>
        <el-col :span="8">
          <el-form-item label="E-value:" style="width: 100%;">
            <el-select v-model="selectedEvalue">
              <el-option v-for="evalue in evalueOptions" :key="evalue.value" :label="evalue.label"
                :value="evalue.value" />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="Word size:" style="width: 100%;">
            <el-input-number v-model="wordsize" :min="4" style="width: 100%;" />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="Max hsps:" style="width: 100%;">
            <el-input-number v-model="maxHsps" :min="1" style="width: 100%;" />
          </el-form-item>
        </el-col>
      </el-row>
      <el-row>
        <el-col :span="4">
          <el-form-item label="Short sequence:" style="width: 100%;">
            <el-switch v-model="shortSequence" />
          </el-form-item>
        </el-col>
        <el-col :span="4">
          <el-form-item label="Fast mode:" style="width: 100%;">
            <el-switch v-model="fastMode" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <!-- <el-form-item label="Filter low complexity region:" style="width: 100%;">
            <el-switch v-model="filterLowComplexity" />
          </el-form-item> -->
        </el-col>
      </el-row>
    </el-form>
    <div style="display: flex; justify-content: flex-end;">
      <el-button type="primary" @click="handlefillExample">Example</el-button>
      <el-button type="primary" :icon="Search" :loading="loading_search" @click="submitblastn">Search</el-button>
    </div>
  </el-card>

  <div v-if="loading_search" v-loading="loading_search" style="height: 40vh;"></div>
  <div v-if="outisnone">
    <el-divider />
    <el-empty description="No matching data found!" :image-size="300" />
  </div>
  <div v-if="tableData.length">
    <div style="display: flex; justify-content: center;">
      <BlastCircos :data="tableData" />
    </div>
    <el-divider />

    <h2>Search Results:</h2>
    <!-- <div style="margin-bottom: 20px; display: flex; justify-content: flex-end;">
      <el-button color="#8A2BE2" type="primary" :icon="Download" :loading="loading_download" @click="downloadselect">
        Download Table
      </el-button>
    </div> -->
    <el-table :data="paginatedData" :stripe="true" style="width: 100%" :highlight-current-row="true"
      @filter-change="handleFilterChange" @sort-change="handleSort" show-overflow-tooltip
      :header-cell-style="{ backgroundColor: '#EBEDF0' }">
      <el-table-column type="expand">
        <template #default="props">
          <div style="padding: 8px 20px;">
            <pre style="font-family: monospace; white-space: pre-wrap;">
{{ formatAlignment(props.row.qseq, props.row.midline, props.row.hseq) }}
            </pre>
          </div>
        </template>
      </el-table-column>
      <el-table-column label="Query ID" prop="queryId" min-width="50px" :filters="queryFilters" column-key="queryId"
        :filter-method="() => true" :filtered-value="selectedQuery" />
      <el-table-column label="Target" prop="targetId" min-width="40px" :filters="chromFilters" column-key="targetId"
        :filter-method="() => true" :filtered-value="selectedTargets" />
      <el-table-column label="Bit Score" prop="bitScore" min-width="40px" sortable="custom" />
      <el-table-column label="Evalue" prop="evalue" min-width="40px" sortable="custom">
        <template #default="{ row }">
          {{ row.evalue }}
        </template>
      </el-table-column>
      <el-table-column label="Identity" prop="identity" min-width="50px" sortable="custom" />
      <el-table-column label="Gaps" prop="gaps" min-width="30px" sortable="custom" />
      <el-table-column label="Query Pos.(Len)">
        <template #default="{ row }">
          {{ row.qstart }}-{{ row.qend }}({{ row.qlen }})
        </template>
      </el-table-column>
      <el-table-column label="Target Pos.(Len)">
        <template #default="{ row }">
          {{ row.tstart }}-{{ row.tend }}({{ row.tlen }})
        </template>
      </el-table-column>
      <el-table-column label="Strand" prop="strand" min-width="30px" />
    </el-table>
    <el-pagination @current-change="handleCurrentChange" :current-page="currentPage" :page-size="pageSize"
      :total="totalItems" layout="total, prev, pager, next, jumper" />
  </div>


</template>

<script lang="ts" setup>
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue';
import { Download, Search } from '@element-plus/icons-vue';
import { ElMessage } from 'element-plus';
import axios from 'axios';
import BlastCircos from '@/components/BlastCircos.vue';
import { useUuidStore } from '@/stores/uuid';
import { getLogger } from '@/utils/logger';
import type { CheckboxValueType } from 'element-plus'
import { identity } from '@vueuse/core';
const log = getLogger('Blastn.vue'); // 当前组件名

log.setLevel('debug'); // 只打开这个组件的调试日志

const dnaseqInput = ref('');
const loading_search = ref(false);
const outisnone = ref(false);
const uuidStore = useUuidStore();

type FastaSequence = {
  name: string;
  sequence: string;
}
const selectedBlastdb = ref<CheckboxValueType[]>(['b73v5'])
const Blastdbs = [
  {
    value: 'b73v5',
    label: 'b73v5',
  },
  {
    value: 'b97',
    label: 'b97',
  }
]
const selectedEvalue = ref('5');
const evalueOptions = [
  {
    value: '0',
    label: '1',
  },
  {
    value: '3',
    label: '1e-3',
  },
  {
    value: '5',
    label: '1e-5',
  },
  {
    value: '6',
    label: '1e-6',
  },
  {
    value: '10',
    label: '1e-10',
  },
  {
    value: '30',
    label: '1e-30',
  },
  {
    value: '100',
    label: '1e-100',
  }
];

const filterLowComplexity = ref(false);
const wordsize = ref(11); // 默认值为 11
const maxHsps = ref(5); // 默认值为 5

// blastTask处理逻辑，两个互斥
const shortSequence = ref(false);
const fastMode = ref(false);
watch(shortSequence, (val) => {
  if (val) fastMode.value = false;
});

watch(fastMode, (val) => {
  if (val) shortSequence.value = false;
});

const blastTask = computed(() => {
  if (shortSequence.value) return 'blastn-short';
  if (fastMode.value) return 'megablast';
  return 'blastn';
});

watch(blastTask, (task) => {
  if (task === 'blastn') wordsize.value = 11;
  else if (task === 'blastn-short') wordsize.value = 7;
  else if (task === 'megablast') wordsize.value = 28;
});


const handlefillExample = () => {
  dnaseqInput.value = `>seq_1
AAATAATTGAACGCTTTATCTTTTGTTTTTAAGAGATACACATAACAAAATCTAGTGGAGTCATCTATAAAAGTGAGAAA
GTATCTTTTACCACCTTTGGTCAAAATTCCATTCATCTCGCACAGATCAGAATGAACAAGTTCTAGAGGTGCCAAACTCC
TCGCCTCAGCAGCCTTGTGAGGCTTGCGAGGTTGTTTTGATTCTACACACACATGGCACTTAGACTTTTTGACCAAGTTA
AATTTAGGAATTAAATTTATATTTGCTAACCGCATAAGACAGCCAAAGCTTGCATGACAAAACCGTGAATGCCATAAATC
TGACTCATCAGAAAAATTAACAGAATTCACCAGTTTATTACACACATCATGCAGTGATAAGCGGAACAATCCTCCGCAAT
CATATCCTTTACCAACAAAAGTACCATGTTTCGACACAACACATTTATTAGACTCAAGAACAACTTTATATCCATCTCGA
CATAGCATCGAAGCGCTAACGAGATTCTTCTTGATAGAGGGCACATGCTGCACGCTCTTCAATGGCACCGTCTTTCCCGA
AGTAAACTTCAGAATGACCGTACCAACACCAAGAACATGAGCACGCGACCCATTTCCCATCAACAAGGCGCCAGACCTCC
CGACCTGGTAGGAAGTGAACATAGAGGCATCAGCACACACATGAATGTTTGCACCACTGTCCATCCACCACTCAGGTGAA
TTACAGACTGAAAGAACAAATGGTAAAGAATTACCATACCCAGATGTTCCTTCTTCAGTTTCAGTGGTTACAACATTAGC
TGATTTCTTGTCTTGAGTGAACTTGCGATCAGGGCACTCTCTTGCCCAATGTTGATCACTGCCACAGACAAAGCATCCTC
CCTTTCCCTTGTTATTGTTGTTCTTCTTTTTAAACTGTGCTGTATGAACAGGCTTATTTGCATTCTCTTGTTTGTTCTGG
TTTTTCTTCTTGTTAAACTTGCGGAAGTTTCTCTTCTGCACCACATTAGCAGTAGAGGTCTCAACACCTTTTCCGCTGTC
>seq_2
CTTTGTTCTAGCCCTTTCCTCAACATCAAGAGTACCAATGAGCTCTTCCACATTGAACTCTTGTCTCTTATGTTTGAGAG
AGGTAGCAAAGTCCTTCCAAGAAGGTGGCAACTTAGCGATTATACCGCCAGCCACAAACTTGTCAGGCAAAGGACAAGGA
AAAAGTTCGAGTTCCTTAGCTAGTGCCTGAAACTCATGAGCCTGTTCCAATACAGATCGGTTCTCAACCATCTTGTAGTC
ATACAGCTGCTCCATGAGATACAGCTCGCTACCAGCGTCAGTAACTCCAAACTTTCCAACAAGAGCATCCCACAGCTCTT
TCCCCGTGGGAAGGATGATATAGCTTTTCTGGAATTTAGTATCCAGTGCGCTAATTACTGCTCCTCGAAAGAGGTTGTCT
TCAGCCTTAAACTTAGCCTCATCCTCAGGAGGTAAGTTTGCAGGCTTGCCCTCAGCGGCATGAAAACAAGACATTGCAGT
TAGCCACAATTCCATTTTAGCTTTCCATATCAAGAAGTTTTTACCATCAAAAGGATCAGGCTTTAGCACAGCAGCAAAAC
CTCTGACAGAAAAATGCCTAACATTAGGTTTTTGGATTGTTAGAAATATAGGCATTTTCTGTATTATTTTAATTCCATAA
ATTAACATTATGATGATGACATATAATAGATAATCAAACATAGAAAACGTGATCTCAAAAATATCCATAACAATATGGAT
CATGAGAACACAAAGCATATGAAACATGTAACTCATATAAATAAAATAAGCATATAAACATGGTTCATGGATTATTGCAG
AACAACTGGAAATAAACAGATAACGATATAAACAGGATGACTGTAAAATTAAGACAGACAGATATAACGTATTATAATAC
GATAGAGCAAAGCTACATACGACATATATAATATGCAGAATATAAAACTGTAATGAACTGAATTGATCATACCCTCCCAT
GCGCTCCGAGGATCCTGATCCTTGTCCAACTTCTCTTGTCATCCGATCGAGACGCGTTGGGCAGTCGCGAAGACGCTCCC
CAAAAACCTAATTGCCGATCCCCCGTGCAAGGTCTCGAACGTCACCGGCTTCGGAGGCACCTGCCCTCTCGCTTCTCTGT
GCGCGCAGAGTCACGAGATGGAAATACCCTCACTCGGCTGCTGGATTGTGAGACTAAAAAAGTGTTTCTTGTGTGTACCG
AGTGACAGGGGTGCTCCTCTATTTAACCTCTCGCAGAGGGAAGCTGAAGGAGAAAGGTCGCCGAGTCACGCCAAGAGTCG
GCCAGCTCTAGCCGAGTTATGCCATGAGTCGGCCAGCTCTTGCCGAGTCACGCCATAAGTCGGCAGCTGAAGGAGAAGGG
TCACTCGGCTGGCTGACGAAGAGACAGAGTCACTCGGCAGTCGAAGAGACAGGGTCACTCGGCCCGGCCCGGCCGGCGGC
GGCGGCGCGCGCGCGCGCGTGTGGCACGCCCTTGTCCATTTCTTGACTTCTCAAGTTAAGTGGAATAAATCCCACCATAT
AAGTCAAGGCAAAAGACCATTGGACTTCCAATGTGGTACTATTGGTATTCTCCACCATTACACACCATAGAGTTTATTCG`;
  maxHsps.value = 1;
  fastMode.value = true;
  selectedBlastdb.value = ['b73v5', 'b97'];
}

interface BlastHit {
  bit_score: number;
  evalue: string;
  identity: number;
  query_from: number;
  query_to: number;
  query_strand: string;
  hit_from: number;
  hit_to: number;
  hit_strand: string;
  align_len: number;
  gaps: number;
  qseq: string;
  hseq: string;
  midline: string;
}

interface BlastHits {
  hit_id: string;
  hitchr_len: number;
  hits: BlastHit[];
}

interface BlastResult {
  database: string;
  query_id: string;
  hits: BlastHits[];
}

const validDnaRegex = /^[ATCGNatcgn]+$/;
const parsedSeqs = computed<FastaSequence[]>(() => {
  const raw = dnaseqInput.value.trim();

  // 结果数组
  const result: FastaSequence[] = [];

  if (raw.includes('>')) {
    // 按 '>' 分割，去掉第一个空项（因为可能是以 > 开头）
    const blocks = raw.split(/(?=>)/).map(b => b.trim()).filter(b => b !== '');

    for (const block of blocks) {
      const lines = block.split(/\r?\n/).map(l => l.trim()).filter(l => l !== '');
      if (lines.length === 0) continue;
      const nameLine = lines[0];
      let name = "";
      if (nameLine.startsWith('>')) {
        name = nameLine.slice(1).trim();
      }
      const sequence = lines.slice(1).join(''); // 合并多行序列
      result.push({
        name,
        sequence
      });
    }
  } else {
    // 没有 '>'，整个当成一条序列
    const sequence = raw.replace(/\r?\n/g, '');
    result.push({
      name: 'seq_1', // 默认名称
      sequence
    });
  }
  return result;
})

const tableData = ref<Record<string, any>[]>([])


const submitblastn = async () => {
  const raw = dnaseqInput.value.trim();
  const lines = raw.split(/\r?\n/);
  if (lines.length === 0) {
    ElMessage.error('Sequence input is empty.');
    return;
  }

  const hasHeader = lines.some(line => line.startsWith('>'));


  const firstLineIsHeader = lines[0].startsWith('>');
  if (hasHeader && !firstLineIsHeader) {
    ElMessage.error('Invalid format: first line must start with ">" if using FASTA format.');
    return;
  }

  const result: { name: string; sequence: string }[] = [];
  if (hasHeader) {
    const blocks = raw.split(/(?=>)/).map(b => b.trim()).filter(b => b !== '');
    for (const block of blocks) {
      const lines = block.split(/\r?\n/).map(l => l.trim()).filter(Boolean);
      if (!lines[0].startsWith('>')) {
        ElMessage.error('Invalid FASTA format: each block must start with ">"');
        return;
      }
      const name = lines[0].slice(1).trim() || `seq_${result.length + 1}`;
      const sequence = lines.slice(1).join('').toUpperCase();
      result.push({ name, sequence });
    }
  } else {
    const sequence = lines.join('').toUpperCase();
    result.push({ name: 'seq_1', sequence });
  }

  // 校验 DNA 合法性
  const validDnaRegex = /^[ATCGNatcgn]+$/;
  const invalids = result.filter(seq => !validDnaRegex.test(seq.sequence));
  if (invalids.length > 0) {
    const msg = invalids
      .map(s => {
        const invalidChars = Array.from(s.sequence)
          .filter(c => !'ATCGNatcgn'.includes(c))
          .filter((c, i, arr) => arr.indexOf(c) === i) // 去重
          .join('');
        const name = s.name || '[unknown]';
        return `"${name}" (invalid: ${invalidChars || 'unknown'})`;
      })
      .join(', ');
    ElMessage.error(`Invalid DNA sequence(s): ${msg}`);
    return;
  }

  // 校验 ID 是否重复
  const names = result.map(s => s.name);
  const duplicates = names.filter((n, i) => names.indexOf(n) !== i);
  if (duplicates.length > 0) {
    ElMessage.error(`Duplicate sequence IDs: ${[...new Set(duplicates)].join(', ')}`);
    return;
  }


  // 所有合法 → 拼接并发送请求
  const fasta = result.map(s => `>${s.name}\n${s.sequence}`).join('\n');


  function strandToSymbol(strand: string) {
    if (!strand) return '';
    strand = strand.toLowerCase();
    if (strand === 'plus') return '+';
    if (strand === 'minus') return '-';
    return strand; // 其它情况原样返回
  }

  tableData.value = []
  try {
    loading_search.value = true
    // outisnone.value = false
    const response = await axios.post<BlastResult[]>(
      '/maizevarmap_api/query_by_sequence/',
      {
        sequence: fasta,
        evalue: selectedEvalue.value,
        blastdb: selectedBlastdb.value,
        wordsize: wordsize.value,
        blastTask: blastTask.value,
        filterLowComplexity: filterLowComplexity.value,
        maxHsps: maxHsps.value
      },
      {
        headers: { uuid: uuidStore.uuid }
      }
    );
    const allHsps: Record<string, any>[] = [];
    response.data.forEach((blastResult: any, idx: number) => {
      const hits = blastResult.hits;
      const queryId = blastResult.query_id;
      hits.forEach((hit: any) => {
        const targetId = `${blastResult.database}:${hit.hit_id}`;
        const hitchrlen = hit.hitchr_len;
        hit.hsps.forEach((hsp: any) => {
          allHsps.push({
            queryIndex: idx + 1,
            queryId: queryId,
            targetId: targetId,
            bitScore: hsp.bit_score,
            evalue: Number(hsp.evalue).toExponential(2),
            qstart: hsp.query_from,
            qend: hsp.query_to,
            qlen: hsp.query_to - hsp.query_from + 1,
            tstart: hsp.hit_from,
            tend: hsp.hit_to,
            tlen: hsp.hit_to - hsp.hit_from + 1,
            query_len: blastResult.query_len,
            hitchrlen: hitchrlen,
            identity: hsp.identity ?? null,
            gaps: hsp.gaps ?? null,
            strand: `${strandToSymbol(hsp.query_strand)}/${strandToSymbol(hsp.hit_strand)}`,
            qseq: hsp.qseq ?? '',
            hseq: hsp.hseq ?? '',
            midline: hsp.midline ?? ''

          });
        });

      });
    });
    tableData.value = allHsps;
    currentPage.value = 1;
    loading_search.value = false;

    if (tableData.value.length === 0) {
      outisnone.value = true;
      ElMessage.warning('No matching data found!');
    }
  } catch (error) {
    loading_search.value = false;
    console.error('Error:', error);
  }
}

// 表格分页
const pageSize = ref(20); // 每页显示的数量
const currentPage = ref(1); // 当前页码

// 排序
const sortProp = ref<string | null>(null)
const sortOrder = ref<'ascending' | 'descending' | null>(null)

//筛选

// 筛选后的数据
const selectedTargets = ref<string[]>([]) // 当前选中多个染色体，默认空表示不过滤
const selectedQuery = ref<string[]>([]) // 当前选中多个查询ID，默认空表示不过滤

const chromFilters = computed(() => {
  const set = new Set(tableData.value.map(item => item.targetId))
  const arr = Array.from(set)

  arr.sort((a, b) => {
    const [dbA, chrA] = a.split(':')
    const [dbB, chrB] = b.split(':')

    if (dbA !== dbB) return dbA.localeCompare(dbB)

    const numA = parseInt(chrA.replace(/\D/g, ''), 10)
    const numB = parseInt(chrB.replace(/\D/g, ''), 10)
    return numA - numB
  })

  return arr.map(chrom => ({ text: chrom, value: chrom }))
})

const queryFilters = computed(() => {
  const set = new Set(tableData.value.map(item => item.queryId))
  const arr = Array.from(set)
  return arr.map(query => ({ text: query, value: query }))
})


function handleFilterChange(filters: Record<string, string[]>) {
  if ('targetId' in filters) {
    selectedTargets.value = filters.targetId
  }
  if ('queryId' in filters) {
    selectedQuery.value = filters.queryId
  }
  currentPage.value = 1 // 筛选后回第一页
}

const filteredData = computed(() => {
  return tableData.value.filter(d => {
    const targetMatch = selectedTargets.value.length === 0 || selectedTargets.value.includes(d.targetId)
    const queryMatch = selectedQuery.value.length === 0 || selectedQuery.value.includes(d.queryId)
    return targetMatch && queryMatch
  })
})

const sortedData = computed(() => {
  if (!sortProp.value || !sortOrder.value) return filteredData.value
  return [...filteredData.value].sort((a, b) => {
    const aVal = a[sortProp.value!]
    const bVal = b[sortProp.value!]
    if (sortOrder.value === 'ascending') return aVal > bVal ? 1 : -1
    else return aVal < bVal ? 1 : -1
  })
})


const totalItems = computed(() => sortedData.value.length); // 数据总量

const paginatedData = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value;
  return sortedData.value.slice(start, start + pageSize.value);
});

function handleSort(e: { prop: string; order: 'ascending' | 'descending' | null }) {
  sortProp.value = e.prop
  sortOrder.value = e.order
  currentPage.value = 1
}

const handleCurrentChange = (page: number) => {
  currentPage.value = page;
};

// 下载所选
const loading_download = ref(false)
const downloadselect = async () => {
  try {
    loading_download.value = true
    const response = await fetch('/tips_api/download_blast_table/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'uuid': uuidStore.uuid
      },
      body: JSON.stringify({ download_type: 'mmseq2' }),
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
    a.download = 'mmseq2out.xlsx'; // 设置下载的文件名
    loading_download.value = false
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
  } catch (error) {
    ElMessage.error('Error downloading selected targets');
    console.error(error);
  }
}

const chunkSize = ref(60)  // 默认60

function updateChunkSize() {
  const w = window.innerWidth
  // 根据窗口宽度动态调整 chunkSize，简单示例
  if (w > 1400) chunkSize.value = 170
  else if (w > 800) chunkSize.value = 100
  else chunkSize.value = 60
}

onMounted(() => {
  updateChunkSize()
  window.addEventListener('resize', updateChunkSize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', updateChunkSize)
})

function formatAlignment(qseq: string, midline: string, hseq: string, size = chunkSize.value): string {
  const lines = []
  for (let i = 0; i < qseq.length; i += size) {
    const q = qseq.slice(i, i + size)
    const m = midline.slice(i, i + size)
    const h = hseq.slice(i, i + size)
    lines.push(`Q: ${q}\n   ${m}\nT: ${h}\n`)
  }
  return lines.join('\n')
}

</script>

<style scoped></style>