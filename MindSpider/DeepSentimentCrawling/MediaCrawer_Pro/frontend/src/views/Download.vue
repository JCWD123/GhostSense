<template>
  <div class="download-page">
    <el-card>
      <template #header>
        <span>视频下载</span>
      </template>

      <el-form :model="downloadForm" label-width="100px">
        <el-form-item label="下载方式">
          <el-radio-group v-model="downloadMode">
            <el-radio label="url">URL 下载</el-radio>
            <el-radio label="batch">批量下载</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="视频URL" v-if="downloadMode === 'url'">
          <el-input 
            v-model="downloadForm.url" 
            placeholder="请输入视频URL"
            clearable
          />
        </el-form-item>

        <el-form-item label="URL列表" v-if="downloadMode === 'batch'">
          <el-input
            v-model="downloadForm.urls"
            type="textarea"
            :rows="6"
            placeholder="每行一个URL"
          />
        </el-form-item>

        <el-form-item label="保存路径">
          <el-input v-model="downloadForm.savePath" placeholder="留空使用默认路径" />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="startDownload" :loading="downloading">
            开始下载
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card style="margin-top: 20px">
      <template #header>
        <span>下载列表</span>
      </template>
      <el-table :data="downloadList" style="width: 100%">
        <el-table-column prop="filename" label="文件名" show-overflow-tooltip />
        <el-table-column prop="size" label="大小" width="120" />
        <el-table-column label="进度" width="200">
          <template #default="{ row }">
            <el-progress :percentage="row.progress" />
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'completed' ? 'success' : 'info'">
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage } from 'element-plus'

const downloadMode = ref('url')
const downloading = ref(false)

const downloadForm = ref({
  url: '',
  urls: '',
  savePath: ''
})

const downloadList = ref([
  {
    filename: 'video1.mp4',
    size: '25.6 MB',
    progress: 100,
    status: 'completed'
  },
  {
    filename: 'video2.mp4',
    size: '18.3 MB',
    progress: 65,
    status: 'downloading'
  }
])

const startDownload = async () => {
  if (!downloadForm.value.url && !downloadForm.value.urls) {
    ElMessage.warning('请输入下载URL')
    return
  }

  downloading.value = true
  try {
    // TODO: 调用下载 API
    await new Promise(resolve => setTimeout(resolve, 1000))
    ElMessage.success('下载任务已添加')
  } finally {
    downloading.value = false
  }
}
</script>

<style scoped>
.download-page {
  height: 100%;
}
</style>




