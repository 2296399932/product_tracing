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
Vue.prototype.$axios =axios;

// Vue.prototype.$httpUrl = "http://8.140.192.183:8004";
Vue.prototype.$httpUrl = "http://127.0.0.1:8000";

// 配置默认值
axios.defaults.baseURL = 'http://127.0.0.1:8000'
axios.defaults.withCredentials = true

// 请求拦截器
axios.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
axios.interceptors.response.use(
  response => {
    return response
  },
  error => {
    if (error.response) {
      switch (error.response.status) {
        case 401:
          // token 过期或无效，清除本地存储并跳转到登录页
          localStorage.removeItem('token')
          localStorage.removeItem('user')
          if (router.currentRoute.path !== '/login') {
            router.push('/login')
          }
          break
        case 403:
          Vue.prototype.$message.error('权限不足')
          break
        default:
          Vue.prototype.$message.error(error.response.data.message || '请求失败')
      }
    }
    return Promise.reject(error)
  }
)

new Vue({
  router,
  render: h => h(App),
}).$mount('#app')
