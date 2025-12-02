<template>
  <div class="tasks-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>任务管理</span>
          <el-button type="primary" :icon="Plus" @click="showCreateDialog = true">
            创建任务
          </el-button>
        </div>
      </template>

      <!-- 筛选条件 -->
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="平台">
          <el-select v-model="searchForm.platform" placeholder="请选择" clearable>
            <el-option label="全部" value="" />
            <el-option label="小红书" value="xhs" />
            <el-option label="抖音" value="douyin" />
            <el-option label="快手" value="kuaishou" />
            <el-option label="B站" value="bilibili" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="请选择" clearable>
            <el-option label="全部" value="" />
            <el-option label="待处理" value="pending" />
            <el-option label="运行中" value="running" />
            <el-option label="已完成" value="completed" />
            <el-option label="失败" value="failed" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadTasks">查询</el-button>
          <el-button @click="resetSearch">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- 任务列表 -->
      <el-table 
        :data="tasks" 
        v-loading="loading"
        style="width: 100%"
      >
        <el-table-column prop="task_id" label="任务ID" width="200" show-overflow-tooltip />
        <el-table-column prop="platform" label="平台" width="100">
          <template #default="{ row }">
            <el-tag>{{ getPlatformName(row.platform) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="type" label="类型" width="100" />
        <el-table-column prop="keywords" label="关键词" show-overflow-tooltip>
          <template #default="{ row }">
            {{ row.keywords?.join(', ') || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="进度" width="150">
          <template #default="{ row }">
            <el-progress 
              :percentage="getProgress(row)" 
              :status="row.status === 'failed' ? 'exception' : undefined"
            />
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button 
              v-if="row.status === 'pending'" 
              link 
              type="success" 
              size="small" 
              @click="startTask(row)"
            >
              启动
            </el-button>
            <el-button link type="primary" size="small" @click="viewDetail(row)">
              详情
            </el-button>
            <el-button link type="danger" size="small" @click="handleDeleteTask(row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.pageSize"
        :total="pagination.total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="loadTasks"
        @current-change="loadTasks"
        style="margin-top: 20px; justify-content: flex-end"
      />
    </el-card>

    <!-- 创建任务对话框 -->
    <el-dialog v-model="showCreateDialog" title="创建任务" width="600px">
      <el-form :model="taskForm" label-width="100px">
        <el-form-item label="平台" required>
          <el-select v-model="taskForm.platform" placeholder="请选择平台">
            <el-option label="小红书" value="xhs" />
            <el-option label="抖音" value="douyin" />
            <el-option label="快手" value="kuaishou" />
            <el-option label="B站" value="bilibili" />
          </el-select>
        </el-form-item>
        <el-form-item label="类型" required>
          <el-select v-model="taskForm.type" placeholder="请选择类型">
            <el-option label="关键词搜索" value="search" />
            <el-option label="首页推荐" value="homefeed" />
            <el-option label="指定笔记" value="note" />
          </el-select>
        </el-form-item>
        <el-form-item label="关键词" v-if="taskForm.type === 'search'">
          <el-select
            v-model="taskForm.keywords"
            multiple
            filterable
            allow-create
            placeholder="请输入关键词，回车添加"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="数量">
          <el-input-number v-model="taskForm.max_count" :min="1" :max="10000" />
        </el-form-item>
        <el-form-item label="爬取评论">
          <el-switch v-model="taskForm.enable_comment" />
        </el-form-item>
        <el-form-item label="下载视频">
          <el-switch v-model="taskForm.enable_download" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="createTask" :loading="creating">
          创建
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import * as api from '@/api'

const loading = ref(false)
const creating = ref(false)
const showCreateDialog = ref(false)

const searchForm = ref({
  platform: '',
  status: ''
})

const tasks = ref<api.Task[]>([])

const pagination = ref({
  page: 1,
  pageSize: 20,
  total: 0
})

const taskForm = ref({
  platform: 'xhs',
  type: 'search',
  keywords: [],
  max_count: 100,
  enable_comment: true,
  enable_download: false
})

const getPlatformName = (platform: string) => {
  const map: Record<string, string> = {
    'xhs': '小红书',
    'douyin': '抖音',
    'kuaishou': '快手',
    'bilibili': 'B站'
  }
  return map[platform] || platform
}

const getStatusType = (status: string) => {
  const map: Record<string, any> = {
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

const loadTasks = async () => {
  loading.value = true
  try {
    const result = await api.getTasks({
      page: pagination.value.page,
      page_size: pagination.value.pageSize,
      status: searchForm.value.status || undefined,
      platform: searchForm.value.platform || undefined
    })
    tasks.value = result.items
    pagination.value.total = result.total
  } catch (error: any) {
    console.error('加载任务列表失败:', error)
  } finally {
    loading.value = false
  }
}

const resetSearch = () => {
  searchForm.value = {
    platform: '',
    status: ''
  }
  pagination.value.page = 1
  loadTasks()
}

const createTask = async () => {
  creating.value = true
  try {
    await api.createTask({
      platform: taskForm.value.platform,
      type: taskForm.value.type,
      keywords: taskForm.value.keywords,
      max_count: taskForm.value.max_count,
      enable_comment: taskForm.value.enable_comment,
      enable_download: taskForm.value.enable_download
    })
    ElMessage.success('任务创建成功')
    showCreateDialog.value = false
    // 重置表单
    taskForm.value = {
      platform: 'xhs',
      type: 'search',
      keywords: [],
      max_count: 100,
      enable_comment: true,
      enable_download: false
    }
    loadTasks()
  } catch (error: any) {
    console.error('创建任务失败:', error)
  } finally {
    creating.value = false
  }
}

const viewDetail = (row: any) => {
  ElMessage.info('查看任务详情：' + row.id)
}

const startTask = async (row: any) => {
  try {
    await api.startTask(row.task_id)
    ElMessage.success('任务已提交执行')
    loadTasks()
  } catch (error: any) {
    console.error('启动任务失败:', error)
  }
}

const handleDeleteTask = async (row: any) => {
  try {
    await ElMessageBox.confirm('确定要删除这个任务吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await api.deleteTask(row.task_id)
    ElMessage.success('删除成功')
    loadTasks()
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('删除任务失败:', error)
    }
  }
}

onMounted(() => {
  loadTasks()
})
</script>

<style scoped>
.tasks-page {
  height: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.search-form {
  margin-bottom: 20px;
}
</style>




