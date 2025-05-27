// src/main.ts
import { createApp } from 'vue'
import App from './App.vue'
import { router } from './router'
import { pinia } from '@/store'

import 'vuetify/styles'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import '@mdi/font/css/materialdesignicons.css'
import Datepicker from '@vuepic/vue-datepicker'
import '@vuepic/vue-datepicker/dist/main.css'

const vuetify = createVuetify({
  components,
  directives,
})

const app = createApp(App)
app.use(router)
app.use(pinia)
app.use(vuetify)

// 글로벌 컴포넌트로 등록
app.component('Datepicker', Datepicker)

app.mount('#app')
