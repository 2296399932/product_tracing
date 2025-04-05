import Vue from 'vue'
import App from './App.vue'
import ElementUI from 'element-ui';
import 'element-ui/lib/theme-chalk/index.css';
import './assets/allCss.css'
import VueRouter from "vue-router"; //路由
import router from "@/router/main";
import axios from 'axios';

Vue.use(VueRouter);
Vue.use(ElementUI);
Vue.config.productionTip = false
Vue.prototype.$axios = axios;

// 使用实际的服务器IP地址
Vue.prototype.$httpUrl = 'http://192.168.1.108:8000'
// 或者考虑自动获取当前主机
// Vue.prototype.$httpUrl = window.location.protocol + '//' + window.location.hostname + ':8000'

// 配置默认值
axios.defaults.baseURL = 'http://127.0.0.1:8000'
axios.defaults.withCredentials = true

// 请求拦截器
axios.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`  // 使用 Bearer 前缀
    }
    console.log('Request config:', {
      url: config.url,
      method: config.method,
      headers: config.headers,
      data: config.data
    })
    return config
  },
  error => {
    console.error('Request error:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
axios.interceptors.response.use(
  response => {
    console.log('Response:', response)
    return response
  },
  error => {
    console.error('Response error:', {
      status: error.response?.status,
      data: error.response?.data,
      config: error.config
    })
    if (error.response) {
      switch (error.response.status) {
        case 401:
          localStorage.removeItem('token')
          localStorage.removeItem('userInfo')
          router.push('/login')
          break
        case 403:
          Vue.prototype.$message.error('权限不足')
          break
        default:
          Vue.prototype.$message.error(error.response.data?.message || '请求失败')
      }
    } else {
      Vue.prototype.$message.error('服务器连接失败')
    }
    return Promise.reject(error)
  }
)

new Vue({
  router,
  render: h => h(App),
}).$mount('#app')
