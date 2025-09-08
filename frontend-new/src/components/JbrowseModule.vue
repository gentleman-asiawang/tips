<template>
  <div ref="jbrowse"></div>
</template>

<script setup>
import { onMounted, onBeforeUnmount, watch, ref } from 'vue'
import '@fontsource/roboto'
import { JBrowseLinearGenomeView, createViewState } from '@jbrowse/react-linear-genome-view2'
import { createRoot } from 'react-dom/client'
import React from 'react'

const props = defineProps({
  defaultLoc: ''
})

const assembly = {
  name: 'maizeb73v5',
  sequence: {
    type: 'ReferenceSequenceTrack',
    trackId: 'maize_b73v5-ReferenceSequenceTrack',
    adapter: {
      type: 'BgzipFastaAdapter',
      fastaLocation: {
        uri: 'http://172.31.2.238/jbrowse-genomes/B73.fasta.gz',
      },
      faiLocation: {
        uri: 'http://172.31.2.238/jbrowse-genomes/B73.fasta.gz.fai',
      },
      gziLocation: {
        uri: 'http://172.31.2.238/jbrowse-genomes/B73.fasta.gz.gzi',
      },
    },
    displays: [
      {
        type: 'LinearReferenceSequenceDisplay',
        displayId:
          'maize_b73v5-ReferenceSequenceTrack-LinearReferenceSequenceDisplay',
        renderer: {
          type: 'DivSequenceRenderer',
        },
      },
    ],
  }
}

const tracks = [
  {
    type: 'FeatureTrack',
    trackId: 'genes',
    name: 'gff3',
    assemblyNames: ['maizeb73v5'],
    category: ['Genes'],
    adapter: {
      type: 'Gff3TabixAdapter',
      uri: 'http://172.31.2.238/jbrowse-genomes/B73.gff3.gz',
    },
    textSearching: {
      textSearchAdapter: {
        type: 'TrixTextSearchAdapter',
        textSearchAdapterId: 'gff3tabix_genes-index',
        uri: 'http://172.31.2.238/jbrowse-genomes/B73.gff3.gz.tbi',
        assemblyNames: ['maizeb73v5'],
      },
    },
  },
  {
    type: 'VariantTrack',
    trackId: 'all_indel_vcf',
    name: 'All Indel Calls',
    assemblyNames: ['maizeb73v5'],
    category: ['Variants'],
    adapter: {
      type: 'VcfTabixAdapter',
      vcfGzLocation: {
        uri: "http://172.31.2.238/jbrowse-genomes/indel_jbrowse.vcf.gz",
        locationType: "UriLocation"
      },
      index: {
        indexType: "CSI",
        location: {
          uri: "http://172.31.2.238/jbrowse-genomes/indel_jbrowse.vcf.gz.csi",
          locationType: "UriLocation"
        }
      },
    },
  },
  {
    type: 'VariantTrack',
    trackId: 'all_snp_vcf',
    name: 'All SNP Calls',
    assemblyNames: ['maizeb73v5'],
    category: ['Variants'],
    adapter: {
      type: 'VcfTabixAdapter',
      vcfGzLocation: {
        uri: "http://172.31.2.238/jbrowse-genomes/snp_jbrowse.vcf.gz",
        locationType: "UriLocation"
      },
      index: {
        indexType: "CSI",
        location: {
          uri: "http://172.31.2.238/jbrowse-genomes/snp_jbrowse.vcf.gz.csi",
          locationType: "UriLocation"
        }
      },
    },
  }
]

function getDefaultSession(loc) {
  return {
    name: 'My session',
    view: {
      id: 'linearGenomeView',
      type: 'LinearGenomeView',
      hideHeader: false,
      showCenterLine: true,
      init: {
        assembly: 'maizeb73v5',
        loc,
        tracks: [
          'maize_b73v5-ReferenceSequenceTrack',
          'genes',
          'all_indel_vcf',
          'all_snp_vcf',
        ],
      },
    },
  }
}

const configuration = {
  "disableAnalytics": true,
  "theme": {
    "palette": {
      "primary": {
        "main": "#008800"
      },
      "secondary": {
        "main": "#008800"
      },
      "tertiary": {
        "main": "#008800"
      },
      "quaternary": {
        "main": "#008800"
      }
    }
  }
}



const jbrowse = ref()
let viewState = null
let root = null

function renderJBrowse() {
  if (!jbrowse.value) return

  const defaultSession = getDefaultSession(props.defaultLoc)

  viewState = createViewState({
    assembly,
    tracks,
    defaultSession,
    configuration,
  })

  // 每次渲染前清理旧内容
  if (root) {
    root.unmount()
    root = null
  }

  if (jbrowse.value) {
    root = createRoot(jbrowse.value)

    root.render(
      React.createElement(JBrowseLinearGenomeView, { viewState })
    )
  }
}

onMounted(() => {
  renderJBrowse()

})

onBeforeUnmount(() => {
  // 组件卸载时清理 React 根节点
  if (root) {
    root.unmount()
    root = null
  }
})

watch(
  () => props.defaultLoc,
  (newLoc) => {
    console.log('defaultLoc changed:', newLoc)
    renderJBrowse()
  }

)

</script>
