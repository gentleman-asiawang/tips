<template>
  <div ref="jbrowse"></div>
</template>

<script setup>
import { onMounted, onBeforeUnmount, watch, ref } from 'vue'
import '@fontsource/roboto'
import { JBrowseApp, createViewState } from '@jbrowse/react-app2'
import { createRoot } from 'react-dom/client'
import React, { Suspense } from 'react'

const props = defineProps({
  config: Object
})

const jbrowse = ref()
let root = null
// 添加错误边界组件
class ErrorBoundary extends React.Component {
  state = { hasError: false, error: null }

  static getDerivedStateFromError(error) {
    return { hasError: true, error }
  }

  render() {
    if (this.state.hasError) {
      return React.createElement('div', null,
        `JBrowse Error: ${this.state.error.message}`
      )
    }
    return this.props.children
  }
}
function renderJBrowse() {
  if (!jbrowse.value) return

  const viewState = createViewState({
    config: props.config,
    disableImportForm: true
  })

  // 每次渲染前清理旧内容
  if (root) {
    root.unmount()
    root = null
  }

  if (jbrowse.value) {
    root = createRoot(jbrowse.value)

    root.render(
      React.createElement(JBrowseApp, { viewState })
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
  () => props.config,
  () => {
    renderJBrowse()
  },
  { deep: true }
)

</script>


<!-- const config = {
  assemblies: [
    {
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
  ],
  tracks: [
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
  ],
  defaultSession: {
    name: 'maizevarmap',
    margin: 0,
    views: [
      {
        id: 'linearGenomeView',
        minimized: false,
        type: 'LinearGenomeView'
      },
    ],
  },
} -->