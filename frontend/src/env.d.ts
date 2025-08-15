/// <reference types="vite/client" />

declare module '*.vue' {
  import { DefineComponent } from 'vue'
  const component: DefineComponent<{}, {}, any>
  export default component
}



declare global {
  const PDBeMolstarPlugin: any; // 声明通过 CDN 引入的第三方库
  const phyloview: any;
}


export {};