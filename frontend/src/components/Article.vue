<template>
    <p class="p2">
        Wu W., Cui C., Zhu Y., Chen J., Zhuang Q., Wang Y., Liu Z., Gao H., Ou G.-Z., Liu C., Tao M., Chen Y., Pan R.,
        Zhang G.,
        Cai H., Yang J., Chen X., Zhou X., Wang S., & Shen X.-X. 2026. Structural genomics sheds light on protein
        functions and remote homologs across the insect tree of life. <em>Cell Research</em>, 36(6):411–425.<a
            style="color: #409eff;font-size: 22px;margin-left: 8px;cursor: pointer;vertical-align: baseline;"
            href="javascript:void(0)" @click="!downloading && downloadPdf()">PDF</a>
    </p>
</template>


<script lang="ts" setup>
import { ref } from 'vue';

const downloading = ref(false);

const downloadPdf = async () => {
  if (downloading.value) return;
  downloading.value = true;
  try {
    const url = 'https://tips.shenxlab.com/tips_data/2026_Wu_etal_Cell_Res.pdf';
    const response = await fetch(url, { mode: 'cors' });
    const blob = await response.blob();
    const blobUrl = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = blobUrl;
    a.download = '2026_Wu_etal_Cell_Res.pdf';
    document.body.appendChild(a);
    a.click();
    a.remove();
    window.URL.revokeObjectURL(blobUrl);
  } finally {
    downloading.value = false;
  }
};
</script>

<style scoped>
.p2 {
  font-family: "Helvetica", Times, Sans-serif;
  font-size: 22px;
  line-height: 1.25;
  margin-top: 20px;
  text-align: justify;
}
</style>
