<template>
  <div>
    <div class="users-container">
      <!-- 搜索栏 -->
      <el-card class="filter-card">
        <el-form :inline="true" :model="searchForm">
          <el-form-item label="用户名">
            <el-input v-model="searchForm.username" placeholder="请输入用户名"></el-input>
          </el-form-item>
          <el-form-item label="角色">
            <el-select v-model="searchForm.role" placeholder="请选择角色">
              <el-option label="全部" value=""></el-option>
              <el-option label="管理员" value="admin"></el-option>
              <el-option label="普通用户" value="user"></el-option>
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleSearch">查询</el-button>
            <el-button @click="handleAdd">添加用户</el-button>
          </el-form-item>
        </el-form>
      </el-card>

      <!-- 用户列表 -->
      <el-card>
        <el-table :data="users" border style="width: 100%">
          <el-table-column prop="username" label="用户名"></el-table-column>
          <el-table-column prop="email" label="邮箱"></el-table-column>
          <el-table-column prop="phone" label="手机号"></el-table-column>
          <el-table-column prop="company_name" label="公司名称"></el-table-column>
          <el-table-column prop="address" label="地址"></el-table-column>
          <el-table-column prop="role" label="角色">
            <template slot-scope="scope">
              <el-tag :type="scope.row.role === 'admin' ? 'danger' : ''">
                {{ scope.row.role === 'admin' ? '管理员' : '普通用户' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="status" label="状态">
            <template slot-scope="scope">
              <el-tag :type="scope.row.status ? 'success' : 'info'">
                {{ scope.row.status ? '启用' : '禁用' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="创建时间" width="180"></el-table-column>
          <el-table-column prop="last_login" label="最后登录时间" width="180"></el-table-column>
          <el-table-column label="操作" width="250">
            <template slot-scope="scope">
              <el-button size="mini" @click="handleEdit(scope.row)">编辑</el-button>
              <el-button 
                size="mini" 
                type="primary" 
                @click="handleViewDetails(scope.row)">
                查看详情
              </el-button>
              <el-button 
                size="mini" 
                type="danger"
                @click="handleDelete(scope.row)"
                :disabled="scope.row.role === 'admin'">
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>

        <div class="pagination-container">
          <el-pagination
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
            :current-page="currentPage"
            :page-sizes="[10, 20, 50, 100]"
            :page-size="pageSize"
            layout="total, sizes, prev, pager, next, jumper"
            :total="total">
          </el-pagination>
        </div>
      </el-card>

      <!-- 用户详情抽屉 -->
      <el-drawer
        title="用户详情"
        :visible.sync="drawerVisible"
        direction="rtl"
        size="500px">
        <div class="drawer-content">
          <el-descriptions :column="1" border>
            <el-descriptions-item label="用户名">{{ currentUser.username }}</el-descriptions-item>
            <el-descriptions-item label="邮箱">{{ currentUser.email }}</el-descriptions-item>
            <el-descriptions-item label="手机号">{{ currentUser.phone }}</el-descriptions-item>
            <el-descriptions-item label="公司名称">{{ currentUser.company_name }}</el-descriptions-item>
            <el-descriptions-item label="地址">{{ currentUser.address }}</el-descriptions-item>
            <el-descriptions-item label="角色">
              {{ currentUser.role === 'admin' ? '管理员' : '普通用户' }}
            </el-descriptions-item>
            <el-descriptions-item label="状态">
              <el-tag :type="currentUser.status ? 'success' : 'info'">
                {{ currentUser.status ? '启用' : '禁用' }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="创建时间">
              {{ formatDate(currentUser.created_at) }}
            </el-descriptions-item>
            <el-descriptions-item label="最后登录">
              {{ formatDate(currentUser.last_login) }}
            </el-descriptions-item>
          </el-descriptions>
        </div>
      </el-drawer>

      <!-- 添加/编辑对话框 -->
      <el-dialog :title="dialogTitle" :visible.sync="dialogVisible" width="500px">
        <el-form :model="form" :rules="rules" ref="form" label-width="100px">
          <el-form-item label="用户名" prop="username">
            <el-input v-model="form.username" :disabled="!!form.id"></el-input>
          </el-form-item>
          <el-form-item label="密码" prop="password" v-if="!form.id">
            <el-input type="password" v-model="form.password"></el-input>
          </el-form-item>
          <el-form-item label="邮箱" prop="email">
            <el-input v-model="form.email"></el-input>
          </el-form-item>
          <el-form-item label="手机号" prop="phone">
            <el-input v-model="form.phone"></el-input>
          </el-form-item>
          <el-form-item label="公司名称" prop="company_name">
            <el-input v-model="form.company_name"></el-input>
          </el-form-item>
          <el-form-item label="地址" prop="address">
            <el-input v-model="form.address"></el-input>
          </el-form-item>
          <el-form-item label="角色" prop="role">
            <el-select v-model="form.role">
              <el-option label="管理员" value="admin"></el-option>
              <el-option label="普通用户" value="user"></el-option>
            </el-select>
          </el-form-item>
          <el-form-item label="状态" prop="is_active" v-if="form.id">
            <el-switch
              v-model="form.is_active"
              active-text="启用"
              inactive-text="禁用">
            </el-switch>
          </el-form-item>
        </el-form>
        <div slot="footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSubmit">确定</el-button>
        </div>
      </el-dialog>
    </div>
  </div>
</template>

<script>
export default {
  name: 'UserManagement',
  data() {
    return {
      searchForm: {
        username: '',
        role: ''
      },
      users: [],
      currentPage: 1,
      pageSize: 10,
      total: 0,
      dialogVisible: false,
      dialogTitle: '添加用户',
      form: this.getDefaultForm(),
      rules: {
        username: [
          { required: true, message: '请输入用户名', trigger: 'blur' },
          { min: 3, max: 20, message: '长度在 3 到 20 个字符', trigger: 'blur' }
        ],
        password: [
          { required: true, message: '请输入密码', trigger: 'blur' },
          { min: 6, message: '密码长度至少为6个字符', trigger: 'blur' }
        ],
        email: [
          { required: true, message: '请输入邮箱地址', trigger: 'blur' },
          { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
        ],
        phone: [
          { required: true, message: '请输入手机号', trigger: 'blur' },
          { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号', trigger: 'blur' }
        ]
      },
      drawerVisible: false,
      currentUser: {}
    }
  },
  created() {
    this.fetchUsers()
  },
  methods: {
    getDefaultForm() {
      return {
        username: '',
        password: '',
        email: '',
        phone: '',
        company_name: '',
        address: '',
        role: 'user',
        is_active: true
      }
    },
    
    async fetchUsers() {
      try {
        const response = await this.$axios.get('/api/users/users/', {
          params: {
            page: this.currentPage,
            page_size: this.pageSize,
            username: this.searchForm.username,
            role: this.searchForm.role
          }
        })

        const { results, count } = response.data.data
        this.users = results.map(user => ({
          ...user,
          status: user.is_active,
          last_login: user.last_login ? new Date(user.last_login).toLocaleString() : '从未登录',
          created_at: new Date(user.created_at).toLocaleString(),
          updated_at: new Date(user.updated_at).toLocaleString()
        }))
        this.total = count
      } catch (error) {
        this.$message.error(error.response?.data?.message || '获取用户列表失败')
      }
    },

    handleError(error) {
      this.$message.error(error.response?.data?.message || '操作失败')
    },

    handleSubmit() {
      this.$refs.form.validate(async valid => {
        if (valid) {
          try {
            const method = this.form.id ? 'put' : 'post'
            const url = this.form.id 
              ? `/api/users/users/${this.form.id}/`
              : '/api/users/users/'
            
            const data = { ...this.form }
            if (!this.form.id) {
              delete data.is_active
            }
            
            const response = await this.$axios[method](url, data)
            
            this.$message.success(response.data.message)
            this.dialogVisible = false
            this.fetchUsers()
          } catch (error) {
            this.handleError(error)
          }
        }
      })
    },

    handleAdd() {
      this.dialogTitle = '添加用户'
      this.form = this.getDefaultForm()
      this.dialogVisible = true
    },

    handleEdit(row) {
      this.dialogTitle = '编辑用户'
      this.form = {
        ...row,
        is_active: row.status
      }
      delete this.form.password
      this.dialogVisible = true
    },

    handleViewDetails(row) {
      this.currentUser = { ...row }
      this.drawerVisible = true
    },

    async handleDelete(row) {
      try {
        await this.$confirm('确认删除该用户?', '提示', {
          type: 'warning'
        })
        
        const response = await this.$axios.delete(`/api/users/users/${row.id}/`)
        this.$message.success(response.data.message)
        this.fetchUsers()
      } catch (error) {
        if (error !== 'cancel') {
          this.handleError(error)
        }
      }
    },

    handleSearch() {
      this.currentPage = 1
      this.fetchUsers()
    },

    handleSizeChange(val) {
      this.pageSize = val
      this.fetchUsers()
    },

    handleCurrentChange(val) {
      this.currentPage = val
      this.fetchUsers()
    },

    formatDate(date) {
      return date ? new Date(date).toLocaleString() : '未知'
    }
  }
}
</script>

<style scoped>
.users-container {
  padding: 20px;
}
.filter-card {
  margin-bottom: 20px;
}
.pagination-container {
  margin-top: 20px;
  text-align: right;
}
.drawer-content {
  padding: 20px;
}
.el-descriptions {
  margin: 20px;
}
</style> 