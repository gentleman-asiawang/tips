import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'


import 'element-plus/dist/index.css'
import 'element-plus/theme-chalk/dark/css-vars.css'
import "@/assets/styles/theme.scss"; // 引入自定义主题


import App from './App.vue'
import router from './router'

/* add fontawesome core */
import { library } from '@fortawesome/fontawesome-svg-core'
/* import font awesome icon component */
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'

import { fas } from '@fortawesome/free-solid-svg-icons'
import { far } from '@fortawesome/free-regular-svg-icons'
import { fab } from '@fortawesome/free-brands-svg-icons'

library.add(fas, far, fab)

const app = createApp(App)

app.use(ElementPlus)
app.component('font-awesome-icon', FontAwesomeIcon)
app.use(createPinia())
app.use(router)


app.mount('#app')
