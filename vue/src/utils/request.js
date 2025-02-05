import axios from 'axios'
import { Message } from 'element-ui'
import { router } from '../router'

const service = axios.create({
  baseURL: process.env.VUE_APP_BASE_API,
  timeout: 5000
})

// 请求拦截器
service.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token')
    console.log('Request config:', {
      url: config.url,
      method: config.method,
      data: config.data,
      params: config.params,
      token: token ? 'exists' : 'missing',
      headers: config.headers
    })
    
    if (token) {
      config.headers = config.headers || {}
      config.headers['Authorization'] = `Bearer ${token}`
      config.headers['Content-Type'] = 'application/json'
      config.headers['Accept'] = 'application/json'
      console.log('Final request headers:', config.headers)
    }
    return config
  },
  error => {
    console.error('Request interceptor error:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
service.interceptors.response.use(
  response => {
    console.log('Response:', {
      url: response.config.url,
      status: response.status,
      data: response.data
    })
    return response
  },
  error => {
    console.error('Response error:', {
      url: error.config?.url,
      status: error.response?.status,
      data: error.response?.data,
      message: error.message
    })
    if (error.response?.status === 403) {
      Message.error(error.response.data.detail || '您没有权限执行此操作')
    } else if (error.response?.status === 401) {
      Message.error('登录已过期，请重新登录')
      localStorage.removeItem('token')
      localStorage.removeItem('userInfo')
      router.push('/login')
    }
    return Promise.reject(error)
  }
)

export default service 