/**
 * API 接口统一导出
 */
import request, { API_PREFIX } from './request'

// ============ 任务管理 ============
export interface Task {
  id: string
  platform: string
  type: string
  status: string
  keywords?: string[]
  max_count?: number
  progress?: {
    total: number
    crawled: number
    failed: number
  }
  created_at: string
  updated_at: string
}

export interface CreateTaskParams {
  platform: string
  type: string
  keywords?: string[]
  max_count?: number
  enable_comment?: boolean
  enable_download?: boolean
}

export interface TaskListParams {
  page?: number
  page_size?: number
  status?: string
  platform?: string
}

export interface TaskListResponse {
  items: Task[]
  total: number
  page: number
  page_size: number
}

// 获取任务列表
export const getTasks = (params?: TaskListParams) => {
  return request.get<any, TaskListResponse>(`${API_PREFIX}/tasks`, { params })
}

// 创建任务
export const createTask = (data: CreateTaskParams) => {
  return request.post<any, Task>(`${API_PREFIX}/tasks`, data)
}

// 获取任务详情
export const getTask = (taskId: string) => {
  return request.get<any, Task>(`${API_PREFIX}/tasks/${taskId}`)
}

// 启动任务
export const startTask = (taskId: string) => {
  return request.put(`${API_PREFIX}/tasks/${taskId}`)
}

// 删除任务
export const deleteTask = (taskId: string) => {
  return request.delete(`${API_PREFIX}/tasks/${taskId}`)
}

// ============ 账号管理 ============
export interface Account {
  id: string
  platform: string
  username: string
  status: string
  cookie?: string
  cookies?: Record<string, any>
  b1?: string
  created_at: string
}

export interface AddAccountParams {
  platform: string
  username: string
  cookie?: string
  cookies?: Record<string, any>
  b1?: string
}

// 获取账号列表
export const getAccounts = (platform?: string, status?: string) => {
  const params: any = {}
  if (platform) params.platform = platform
  if (status) params.status = status
  return request.get<any, Account[]>(`${API_PREFIX}/accounts`, { params })
}

// 添加账号
export const addAccount = (data: AddAccountParams) => {
  return request.post<any, Account>(`${API_PREFIX}/accounts`, data)
}

// 删除账号
export const deleteAccount = (accountId: string) => {
  return request.delete(`${API_PREFIX}/accounts/${accountId}`)
}

// ============ 代理管理 ============
export interface Proxy {
  id: string
  host: string
  port: number
  username?: string
  password?: string
  status: string
  created_at: string
}

export interface AddProxyParams {
  host: string
  port: number
  username?: string
  password?: string
}

// 获取代理列表
export const getProxies = (status?: string) => {
  const params: any = {}
  if (status) params.status = status
  return request.get<any, Proxy[]>(`${API_PREFIX}/proxies`, { params })
}

// 添加代理
export const addProxy = (data: AddProxyParams) => {
  return request.post<any, Proxy>(`${API_PREFIX}/proxies`, data)
}

// 删除代理
export const deleteProxy = (proxyId: string) => {
  return request.delete(`${API_PREFIX}/proxies/${proxyId}`)
}

// ============ 下载管理 ============
export interface DownloadParams {
  url: string
  save_path?: string
  filename?: string
}

export interface DownloadResponse {
  file_path: string
  file_size: number
}

// 下载文件
export const downloadFile = (data: DownloadParams) => {
  return request.post<any, DownloadResponse>(`${API_PREFIX}/download`, data)
}

// ============ 推荐流 ============
export interface HomeFeedParams {
  platform?: string
  page?: number
}

// 获取推荐流
export const getHomeFeed = (params?: HomeFeedParams) => {
  return request.get(`${API_PREFIX}/homefeed`, { params })
}

// ============ 断点续爬 ============
// 获取断点列表
export const getCheckpoints = () => {
  return request.get(`${API_PREFIX}/checkpoints`)
}

// 获取指定任务的断点
export const getCheckpoint = (taskId: string) => {
  return request.get(`${API_PREFIX}/checkpoints/${taskId}`)
}

// ============ 健康检查 ============
export interface HealthResponse {
  status: string
  version: string
  app_name: string
}

// 健康检查
export const checkHealth = () => {
  return request.get<any, HealthResponse>('/health')
}

