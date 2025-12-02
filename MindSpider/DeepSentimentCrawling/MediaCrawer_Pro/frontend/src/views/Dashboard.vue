<template>
  <div class="dashboard">
    <el-row :gutter="20" style="margin-bottom: 20px">
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-card">
            <el-icon class="stat-icon" color="#409EFF"><DocumentCopy /></el-icon>
            <div class="stat-content">
              <div class="stat-value">{{ stats.totalTasks }}</div>
              <div class="stat-label">总任务数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-card">
            <el-icon class="stat-icon" color="#67C23A"><Finished /></el-icon>
            <div class="stat-content">
              <div class="stat-value">{{ stats.completedTasks }}</div>
              <div class="stat-label">已完成</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-card">
            <el-icon class="stat-icon" color="#E6A23C"><Loading /></el-icon>
            <div class="stat-content">
              <div class="stat-value">{{ stats.runningTasks }}</div>
              <div class="stat-label">运行中</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-card">
            <el-icon class="stat-icon" color="#F56C6C"><Failed /></el-icon>
            <div class="stat-content">
              <div class="stat-value">{{ stats.failedTasks }}</div>
              <div class="stat-label">失败</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20">
      <el-col :span="16">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>最近任务</span>
            </div>
          </template>
          <el-table :data="recentTasks" style="width: 100%">
            <el-table-column prop="platform" label="平台" width="100">
              <template #default="{ row }">
                <el-tag>{{ row.platform }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="type" label="类型" width="100" />
            <el-table-column prop="keywords" label="关键词" />
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.status)">{{ row.status }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="progress" label="进度" width="120">
              <template #default="{ row }">
                <el-progress 
                  :percentage="getProgress(row)" 
                  :status="row.status === 'failed' ? 'exception' : undefined"
                />
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>系统状态</span>
            </div>
          </template>
          <div class="system-status">
            <div class="status-item">
              <span class="status-label">后端服务：</span>
              <el-tag :type="systemStatus.backend ? 'success' : 'danger'">
                {{ systemStatus.backend ? '正常' : '异常' }}
              </el-tag>
            </div>
            <div class="status-item">
              <span class="status-label">签名服务：</span>
              <el-tag :type="systemStatus.signature ? 'success' : 'danger'">
                {{ systemStatus.signature ? '正常' : '异常' }}
              </el-tag>
            </div>
            <div class="status-item">
              <span class="status-label">数据库：</span>
              <el-tag :type="systemStatus.database ? 'success' : 'danger'">
                {{ systemStatus.database ? '正常' : '异常' }}
              </el-tag>
            </div>
            <div class="status-item">
              <span class="status-label">Redis：</span>
              <el-tag :type="systemStatus.redis ? 'success' : 'danger'">
                {{ systemStatus.redis ? '正常' : '异常' }}
              </el-tag>
            </div>
          </div>
        </el-card>

        <el-card style="margin-top: 20px">
          <template #header>
            <div class="card-header">
              <span>快速操作</span>
            </div>
          </template>
          <div class="quick-actions">
            <el-button type="primary" :icon="Plus" @click="createTask">创建任务</el-button>
            <el-button type="success" :icon="Download" @click="downloadVideo">下载视频</el-button>
            <el-button type="warning" :icon="User" @click="manageAccounts">账号管理</el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Plus, Download, User } from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'
import * as api from '@/api'

const router = useRouter()

const stats = ref({
  totalTasks: 0,
  completedTasks: 0,
  runningTasks: 0,
  failedTasks: 0
})

const recentTasks = ref([])

const systemStatus = ref({
  backend: false,
  signature: false,
  database: false,
  redis: false
})

const getStatusType = (status: string) => {
  const map: Record<string, string> = {
    'pending': 'info',
    'running': 'warning',
    'completed': 'success',
    'failed': 'danger'
  }
  return map[status] || 'info'
}

const getProgress = (row: any) => {
  if (!row.progress) return 0
  return Math.floor((row.progress.crawled / row.progress.total) * 100) || 0
}

const createTask = () => {
  router.push('/tasks')
}

const downloadVideo = () => {
  router.push('/download')
}

const manageAccounts = () => {
  router.push('/accounts')
}

// 加载系统状态
const loadSystemStatus = async () => {
  try {
    const health = await api.checkHealth()
    console.log('健康检查结果:', health)
    systemStatus.value.backend = health.status === 'healthy'
    // 如果后端正常，则假设数据库和 Redis 也正常（因为启动时已连接）
    systemStatus.value.database = true
    systemStatus.value.redis = true
  } catch (error) {
    console.error('后端服务连接失败:', error)
    systemStatus.value.backend = false
    systemStatus.value.database = false
    systemStatus.value.redis = false
  }
}

// 加载统计数据
const loadStats = async () => {
  try {
    const result = await api.getTasks({ page: 1, page_size: 100 })
    const tasks = result.items
    
    stats.value.totalTasks = result.total
    stats.value.completedTasks = tasks.filter((t: any) => t.status === 'completed').length
    stats.value.runningTasks = tasks.filter((t: any) => t.status === 'running').length
    stats.value.failedTasks = tasks.filter((t: any) => t.status === 'failed').length
    
    // 最近的 5 个任务
    recentTasks.value = tasks.slice(0, 5)
  } catch (error) {
    console.error('加载统计数据失败:', error)
  }
}

onMounted(async () => {
  await loadSystemStatus()
  await loadStats()
})
</script>

<style scoped>
.dashboard {
  height: 100%;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 20px;
}

.stat-icon {
  font-size: 48px;
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 32px;
  font-weight: bold;
  color: #303133;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 5px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.system-status {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.status-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.status-label {
  font-weight: 500;
  color: #606266;
}

.quick-actions {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.quick-actions .el-button {
  width: 100%;
}
</style>




