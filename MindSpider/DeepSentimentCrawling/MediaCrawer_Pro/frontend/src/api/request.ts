/**
 * Axios 请求封装
 */
import axios, { AxiosError, AxiosRequestConfig, AxiosResponse } from 'axios'
import { ElMessage } from 'element-plus'
import { API_BASE_URL, API_PREFIX } from './config'

// 创建 axios 实例
const request = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 请求拦截器
request.interceptors.request.use(
  (config) => {
    // 可以在这里添加 token 等认证信息
    // const token = localStorage.getItem('token')
    // if (token) {
    //   config.headers.Authorization = `Bearer ${token}`
    // }
    
    console.log('📤 API 请求:', config.method?.toUpperCase(), config.url)
    return config
  },
  (error) => {
    console.error('❌ 请求错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  (response: AxiosResponse) => {
    console.log('📥 API 响应:', response.config.url, response.data)
    
    const { data } = response
    
    // 后端返回格式: { code: 0, message: 'success', data: {...} }
    if (data.code === 0) {
      return data.data
    } else {
      // 业务错误
      ElMessage.error(data.message || '请求失败')
      return Promise.reject(new Error(data.message || '请求失败'))
    }
  },
  (error: AxiosError) => {
    console.error('❌ 响应错误:', error)
    
    let message = '网络请求失败'
    
    if (error.response) {
      // 服务器返回错误状态码
      const status = error.response.status
      switch (status) {
        case 400:
          message = '请求参数错误'
          break
        case 401:
          message = '未授权，请重新登录'
          break
        case 403:
          message = '拒绝访问'
          break
        case 404:
          message = '请求的资源不存在'
          break
        case 500:
          message = '服务器内部错误'
          break
        case 502:
          message = '网关错误'
          break
        case 503:
          message = '服务不可用'
          break
        default:
          message = `服务器错误 (${status})`
      }
      
      // 尝试从响应中获取错误信息
      const data = error.response.data as any
      if (data && data.message) {
        message = data.message
      }
    } else if (error.request) {
      // 请求已发出，但没有收到响应
      message = '无法连接到服务器，请检查后端服务是否启动'
    } else {
      // 其他错误
      message = error.message || '请求失败'
    }
    
    ElMessage.error(message)
    return Promise.reject(error)
  }
)

export default request
export { API_PREFIX }


