import axios from 'axios'
import { Message } from 'element-ui'

const service = axios.create({
  baseURL: 'http://192.168.1.7:8000',
  timeout: 5000
})

// 请求拦截器
service.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`
    }
    return config
  },
  error => {
    console.log(error)
    return Promise.reject(error)
  }
)

// 响应拦截器
service.interceptors.response.use(
  response => response.data,
  error => {
    if (error.response && error.response.status === 403) {
      // 处理权限错误
      console.error('权限不足')
    }
    Message({
      message: error.response?.data?.error || '请求失败',
      type: 'error',
      duration: 5 * 1000
    })
    return Promise.reject(error)
  }
)

export default service 