<template>
  <div class="profile-container">
    <el-card class="profile-card">
      <div slot="header">
        <span>个人信息</span>
        <el-button style="float: right; padding: 3px 0" type="text" @click="handleEdit">
          {{ isEditing ? '取消' : '编辑' }}
        </el-button>
      </div>
      
      <!-- 个人信息表单 -->
      <el-form :model="form" :rules="rules" ref="form" label-width="100px" :disabled="!isEditing">
        <el-form-item label="用户名">
          <el-input v-model="form.username" disabled></el-input>
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
        <el-form-item label="角色">
          <el-input v-model="form.role" disabled></el-input>
        </el-form-item>
        <el-form-item label="创建时间">
          <el-input v-model="formattedCreatedAt" disabled></el-input>
        </el-form-item>
        <el-form-item label="最后登录">
          <el-input v-model="formattedLastLogin" disabled></el-input>
        </el-form-item>
        <el-form-item v-if="isEditing">
          <el-button type="primary" @click="handleSubmit">保存</el-button>
          <el-button @click="handleEdit">取消</el-button>
        </el-form-item>
      </el-form>

      <!-- 修改密码表单 -->
      <div class="password-section">
        <div class="section-title">修改密码</div>
        <el-form :model="passwordForm" :rules="passwordRules" ref="passwordForm" label-width="100px">
          <el-form-item label="原密码" prop="old_password">
            <el-input type="password" v-model="passwordForm.old_password"></el-input>
          </el-form-item>
          <el-form-item label="新密码" prop="new_password">
            <el-input type="password" v-model="passwordForm.new_password"></el-input>
          </el-form-item>
          <el-form-item label="确认密码" prop="confirm_password">
            <el-input type="password" v-model="passwordForm.confirm_password"></el-input>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleChangePassword">修改密码</el-button>
          </el-form-item>
        </el-form>
      </div>
    </el-card>
  </div>
</template>

<script>
export default {
  name: 'UserProfile',
  data() {
    const validatePass = (rule, value, callback) => {
      if (value === '') {
        callback(new Error('请输入新密码'))
      } else {
        if (this.passwordForm.confirm_password !== '') {
          this.$refs.passwordForm.validateField('confirm_password')
        }
        callback()
      }
    }
    const validatePass2 = (rule, value, callback) => {
      if (value === '') {
        callback(new Error('请再次输入新密码'))
      } else if (value !== this.passwordForm.new_password) {
        callback(new Error('两次输入密码不一致!'))
      } else {
        callback()
      }
    }
    return {
      isEditing: false,
      form: {
        username: '',
        email: '',
        phone: '',
        company_name: '',
        address: '',
        role: '',
        created_at: '',
        last_login: '',
        is_active: true
      },
      passwordForm: {
        old_password: '',
        new_password: '',
        confirm_password: ''
      },
      rules: {
        email: [
          { required: true, message: '请输入邮箱地址', trigger: 'blur' },
          { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
        ],
        phone: [
          { required: true, message: '请输入手机号', trigger: 'blur' },
          { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号', trigger: 'blur' }
        ]
      },
      passwordRules: {
        old_password: [
          { required: true, message: '请输入原密码', trigger: 'blur' }
        ],
        new_password: [
          { required: true, validator: validatePass, trigger: 'blur' },
          { min: 6, message: '密码长度至少为6个字符', trigger: 'blur' }
        ],
        confirm_password: [
          { required: true, validator: validatePass2, trigger: 'blur' }
        ]
      }
    }
  },
  computed: {
    formattedCreatedAt() {
      return this.form.created_at ? new Date(this.form.created_at).toLocaleString() : '未知'
    },
    formattedLastLogin() {
      return this.form.last_login ? new Date(this.form.last_login).toLocaleString() : '从未登录'
    }
  },
  created() {
    this.fetchUserInfo()
  },
  methods: {
    fetchUserInfo() {
      this.$axios.get('/api/users/profile/')
        .then(res => {
          const roleMap = {
            'admin': '管理员',
            'user': '普通用户'
          }
          res.data.role = roleMap[res.data.role] || res.data.role
          this.form = res.data
        })
        .catch(err => {
          this.$message.error('获取用户信息失败')
          console.error(err)
        })
    },
    handleEdit() {
      if (this.isEditing) {
        this.fetchUserInfo()
      }
      this.isEditing = !this.isEditing
    },
    handleSubmit() {
      this.$refs.form.validate(valid => {
        if (valid) {
          this.$axios.put('/api/users/profile/', {
            email: this.form.email,
            phone: this.form.phone,
            company_name: this.form.company_name,
            address: this.form.address
          })
            .then(() => {
              this.$message.success('更新成功')
              this.isEditing = false
              this.fetchUserInfo()
            })
            .catch(err => {
              this.$message.error('更新失败')
              console.error(err)
            })
        }
      })
    },
    handleChangePassword() {
      this.$refs.passwordForm.validate(valid => {
        if (valid) {
          // eslint-disable-next-line no-unused-vars
          /* eslint-disable */
          const { confirm_password, ...data } = this.passwordForm
          this.$axios.post(this.$httpUrl + '/api/users/profile/change-password/', data)
            .then(() => {
              this.$message.success('密码修改成功，请重新登录')
              localStorage.removeItem('token')
              localStorage.removeItem('userInfo')
              this.$router.push('/login')
            })
            .catch(err => {
              this.$message.error(err.response?.data?.error || '密码修改失败')
            })
        }
      })
    }
  }
}
</script>

<style scoped>
.profile-container {
  padding: 20px;
}
.profile-card {
  max-width: 800px;
  margin: 0 auto;
}
.password-section {
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #eee;
}
.section-title {
  font-size: 18px;
  margin-bottom: 20px;
}
.el-form-item {
  margin-bottom: 22px;
}
.disabled-input .el-input__inner {
  background-color: #f5f7fa;
  color: #909399;
}
</style> 