<template>
  <div class="accounts-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>账号管理</span>
          <el-button type="primary" :icon="Plus" @click="showAddDialog = true">
            添加账号
          </el-button>
        </div>
      </template>

      <el-table :data="accounts" v-loading="loading">
        <el-table-column prop="platform" label="平台" width="120">
          <template #default="{ row }">
            <el-tag>{{ getPlatformName(row.platform) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="username" label="用户名" width="150" />
        <el-table-column label="Cookie" show-overflow-tooltip>
          <template #default="{ row }">
            {{ row.cookie || JSON.stringify(row.cookies || {}).substring(0, 50) + '...' }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'danger'">
              {{ row.status || 'active' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="b1" width="140">
          <template #default="{ row }">
            <el-tag :type="row.b1 ? 'success' : 'info'">
              {{ row.b1 ? '已配置' : '未配置' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="use_count" label="使用次数" width="100" />
        <el-table-column label="成功率" width="100">
          <template #default="{ row }">
            {{ row.success_count && row.use_count ? Math.round((row.success_count / row.use_count) * 100) : 0 }}%
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button link type="danger" size="small" @click="deleteAccount(row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 添加账号对话框 -->
    <el-dialog v-model="showAddDialog" title="添加账号" width="600px">
      <el-form :model="accountForm" label-width="100px">
        <el-form-item label="平台" required>
          <el-select v-model="accountForm.platform" placeholder="请选择平台">
            <el-option label="小红书" value="xhs" />
            <el-option label="抖音" value="douyin" />
            <el-option label="快手" value="kuaishou" />
            <el-option label="B站" value="bilibili" />
          </el-select>
        </el-form-item>
        <el-form-item label="用户名">
          <el-input v-model="accountForm.username" placeholder="可选，默认为平台名称" />
        </el-form-item>
        <el-form-item label="Cookie" required>
          <el-input
            v-model="accountForm.cookie"
            type="textarea"
            :rows="4"
            placeholder="格式: a1=xxx; web_session=xxx; webId=xxx"
          />
          <div style="margin-top: 8px; font-size: 12px; color: #999;">
            提示：从浏览器开发者工具的 Network 标签中复制完整的 Cookie
          </div>
        </el-form-item>
        <el-form-item label="b1">
          <el-input
            v-model="accountForm.b1"
            placeholder="可选，localStorage.getItem('b1')"
          />
          <div style="margin-top: 8px; font-size: 12px; color: #999;">
            提示：打开小红书网页版控制台，执行 localStorage.getItem('b1') 获取该值，可用于生成 x-s-common
          </div>
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="accountForm.note" placeholder="可选" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" @click="addAccount" :loading="adding">
          添加
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import * as api from '../api'

const loading = ref(false)
const adding = ref(false)
const showAddDialog = ref(false)

const accounts = ref([])

const accountForm = ref({
  platform: 'xhs',
  cookie: '',
  username: '',
  weight: 1,
  note: '',
  b1: ''
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

const loadAccounts = async () => {
  loading.value = true
  try {
    const result = await api.getAccounts()
    accounts.value = result || []
  } catch (error) {
    console.error('加载账号列表失败:', error)
    ElMessage.error('加载账号列表失败')
  } finally {
    loading.value = false
  }
}

const addAccount = async () => {
  if (!accountForm.value.cookie) {
    ElMessage.warning('请输入 Cookie')
    return
  }

  adding.value = true
  try {
    // 解析 Cookie 字符串为对象
    const cookieObj: Record<string, string> = {}
    accountForm.value.cookie.split(';').forEach(item => {
      const [key, value] = item.trim().split('=')
      if (key && value) {
        cookieObj[key.trim()] = value.trim()
      }
    })

    await api.addAccount({
      platform: accountForm.value.platform,
      username: accountForm.value.username || `${getPlatformName(accountForm.value.platform)}账号`,
      cookie: accountForm.value.cookie,
      cookies: cookieObj,
      b1: accountForm.value.b1 || undefined
    })
    
    ElMessage.success('账号添加成功')
    showAddDialog.value = false
    
    // 重置表单
    accountForm.value = {
      platform: 'xhs',
      cookie: '',
      username: '',
      weight: 1,
      note: '',
      b1: ''
    }
    
    loadAccounts()
  } catch (error) {
    console.error('添加账号失败:', error)
    ElMessage.error('添加账号失败')
  } finally {
    adding.value = false
  }
}

const deleteAccount = async (row: any) => {
  try {
    await ElMessageBox.confirm('确定要删除这个账号吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await api.deleteAccount(row._id)
    ElMessage.success('删除成功')
    loadAccounts()
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('删除账号失败:', error)
      ElMessage.error('删除账号失败')
    }
  }
}

onMounted(() => {
  loadAccounts()
})
</script>

<style scoped>
.accounts-page {
  height: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>



