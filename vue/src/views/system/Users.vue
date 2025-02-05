<template>
  <div v-if="isAdmin">
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
          <el-table-column prop="last_login" label="最后登录时间" width="180"></el-table-column>
          <el-table-column label="操作" width="250">
            <template slot-scope="scope">
              <el-button size="mini" @click="handleEdit(scope.row)">编辑</el-button>
              <el-button 
                size="mini" 
                type="primary" 
                @click="$router.push(`/system/users/${scope.row.id}`)">
                查看详情
              </el-button>
              <el-button 
                size="mini" 
                :type="scope.row.status ? 'warning' : 'success'"
                @click="handleToggleStatus(scope.row)">
                {{ scope.row.status ? '禁用' : '启用' }}
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
            :current-page="page"
            :page-sizes="[10, 20, 50, 100]"
            :page-size="pageSize"
            layout="total, sizes, prev, pager, next, jumper"
            :total="total">
          </el-pagination>
        </div>
      </el-card>

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
          <el-form-item label="角色" prop="role">
            <el-select v-model="form.role">
              <el-option label="管理员" value="admin"></el-option>
              <el-option label="普通用户" value="user"></el-option>
            </el-select>
          </el-form-item>
        </el-form>
        <div slot="footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSubmit">确定</el-button>
        </div>
      </el-dialog>
    </div>
  </div>
  <div v-else class="unauthorized-container">
    <el-result
      icon="error"
      title="无权访问"
      sub-title="抱歉，您没有权限访问用户管理页面">
      <template slot="extra">
        <el-button type="primary" @click="$router.push('/')">返回首页</el-button>
      </template>
    </el-result>
  </div>
</template>

<script>
export default {
  name: 'UserManagement',
  data() {
    return {
      isAdmin: false,
      searchForm: {
        username: '',
        role: ''
      },
      users: [],
      page: 1,
      pageSize: 10,
      total: 0,
      dialogVisible: false,
      dialogTitle: '添加用户',
      form: {
        username: '',
        password: '',
        email: '',
        phone: '',
        role: 'user'
      },
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
        ],
        role: [
          { required: true, message: '请选择角色', trigger: 'change' }
        ]
      }
    }
  },
  created() {
    this.checkPermission()
  },
  methods: {
    checkPermission() {
      const userInfo = JSON.parse(localStorage.getItem('userInfo') || '{}')
      this.isAdmin = userInfo.role === 'admin'
      
      if (!this.isAdmin) {
        this.$message.warning('您没有权限访问此页面')
        return
      }
      
      this.fetchUsers()
    },
    fetchUsers() {
      if (!this.isAdmin) return
      
      const params = {
        page: this.page,
        page_size: this.pageSize,
        username: this.searchForm.username,
        role: this.searchForm.role
      }
      
      this.$axios.get(this.$httpUrl + '/api/users/users/', { params })
        .then(res => {
          this.users = res.data.results
          this.total = res.data.count
        })
        .catch(err => {
          this.$message.error('获取用户列表失败')
          console.error(err)
        })
    },
    handleSearch() {
      this.page = 1
      this.fetchUsers()
    },
    handleAdd() {
      this.dialogTitle = '添加用户'
      this.form = {
        username: '',
        password: '',
        email: '',
        phone: '',
        role: 'user'
      }
      this.dialogVisible = true
    },
    handleEdit(row) {
      this.dialogTitle = '编辑用户'
      this.form = { ...row }
      delete this.form.password
      this.dialogVisible = true
    },
    handleToggleStatus(row) {
      this.$confirm(`确认${row.status ? '禁用' : '启用'}该用户?`, '提示', {
        type: 'warning'
      }).then(() => {
        this.$axios.patch(this.$httpUrl + `/api/users/users/${row.id}/`, {
          status: !row.status
        })
          .then(() => {
            this.$message.success(`${row.status ? '禁用' : '启用'}成功`)
            this.fetchUsers()
          })
          .catch(err => {
            this.$message.error(`${row.status ? '禁用' : '启用'}失败`)
            console.error(err)
          })
      })
    },
    handleDelete(row) {
      this.$confirm('确认删除该用户?', '提示', {
        type: 'warning'
      }).then(() => {
        this.$axios.delete(this.$httpUrl + `/api/users/users/${row.id}/`)
          .then(() => {
            this.$message.success('删除成功')
            this.fetchUsers()
          })
          .catch(err => {
            this.$message.error('删除失败')
            console.error(err)
          })
      })
    },
    handleSubmit() {
      this.$refs.form.validate(valid => {
        if (valid) {
          const method = this.form.id ? 'put' : 'post'
          const url = this.form.id 
            ? `/api/users/users/${this.form.id}/`
            : '/api/users/users/'
          
          this.$axios[method](this.$httpUrl + url, this.form)
            .then(() => {
              this.$message.success(this.form.id ? '更新成功' : '添加成功')
              this.dialogVisible = false
              this.fetchUsers()
            })
            .catch(err => {
              this.$message.error(this.form.id ? '更新失败' : '添加失败')
              console.error(err)
            })
        }
      })
    },
    handleSizeChange(val) {
      this.pageSize = val
      this.fetchUsers()
    },
    handleCurrentChange(val) {
      this.page = val
      this.fetchUsers()
    }
  }
}
</script>

<style scoped>
.users-container {
  padding: 20px;
}
.unauthorized-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: calc(100vh - 120px);
}
.filter-card {
  margin-bottom: 20px;
}
.pagination-container {
  margin-top: 20px;
  text-align: right;
}
</style> 