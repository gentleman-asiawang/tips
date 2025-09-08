import { defineStore } from 'pinia';
import { ElMessage } from 'element-plus';
import { ref, computed } from 'vue';
import axios from 'axios';
import { getLogger } from '@/utils/logger';

const log = getLogger('baseinfo.ts'); // 当前组件名
log.setLevel('debug'); // 只打开这个组件的调试日志

// 定义接口
export interface SampleInfo {
  sample_id: number;
  project_name: string;
  sample_name: string;
  population: string;
  bases_mapped: number;
  source_id: string;
  country: string;
  population_group: string;
  info: string;
  latitude: number;
  longitude: number;
  species: string;
  accession_id: string;
}

export interface PopulationInfo {
  population_id: number;
  population: string;
  population_count: number;
}

// 定义 store
export const useSamplesinfoStore = defineStore('fileinfo', () => {
  const samplesinfoData = ref<SampleInfo[]>([]);
  const querySampleinfo = async (uuid: string) => {
    samplesinfoData.value = [];
    try {
      const response = await axios.get('/maizevarmap_api/get_sample_info/', {
        headers: { 'uuid': uuid },
      });
      if (response.status === 200) {
        samplesinfoData.value = response.data.map((item: any) => ({ ...item }));
      } else {
        ElMessage.error('Unregistered uuid, please refresh the page and try again!');
      };
    } catch (error) {
      ElMessage.error('An error occurred while fetching data!');
    }
  };
  return { samplesinfoData, querySampleinfo };
})

export const usePopulationsStore = defineStore('populations', () => {
  const populationsData = ref<PopulationInfo[]>([]);
  const queryPopulationsInfo = async (uuid: string) => {
    populationsData.value = [];
    try {
      const response = await axios.get('/maizevarmap_api/get_populations_info/', {
        headers: { 'uuid': uuid },
      });
      if (response.status === 200) {
        populationsData.value = response.data.map((item: any) => ({ ...item }));
      } else {
        ElMessage.error('Unregistered uuid, please refresh the page and try again!');
      };
    } catch (error) {
      ElMessage.error('An error occurred while fetching data!');
    }
  };
  return { populationsData, queryPopulationsInfo };
})

export const useChromStore = defineStore('chrom', () => {
  const chromLengths = ref<Record<string, number>>({
    chr1: 308452471,
    chr2: 243675191,
    chr3: 238017767,
    chr4: 250330460,
    chr5: 226353449,
    chr6: 181357234,
    chr7: 185808916,
    chr8: 182411202,
    chr9: 163004744,
    chr10: 152435371,
  });

  const chromNames = computed(() => Object.keys(chromLengths.value));

  return {
    chromNames,
    chromLengths,
  };
});