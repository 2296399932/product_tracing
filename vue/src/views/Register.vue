<template>
  <div class="register-container">
    <el-form ref="registerForm" :model="registerForm" :rules="registerRules" class="register-form">
      <h3 class="title">用户注册</h3>
      <el-form-item prop="username">
        <el-input v-model="registerForm.username" placeholder="用户名" />
      </el-form-item>
      <el-form-item prop="email">
        <el-input v-model="registerForm.email" placeholder="邮箱" />
      </el-form-item>
      <el-form-item prop="phone">
        <el-input v-model="registerForm.phone" placeholder="手机号" />
      </el-form-item>
      <el-form-item prop="company_name">
        <el-input v-model="registerForm.company_name" placeholder="公司名称" />
      </el-form-item>
      <el-form-item prop="address">
        <el-input v-model="registerForm.address" placeholder="地址" />
      </el-form-item>
      <el-form-item prop="password">
        <el-input v-model="registerForm.password" type="password" placeholder="密码" />
      </el-form-item>
      <el-form-item prop="confirmPassword">
        <el-input v-model="registerForm.confirmPassword" type="password" placeholder="确认密码" />
      </el-form-item>
      <el-form-item>
        <el-button :loading="loading" type="primary" @click="handleRegister">注册</el-button>
      </el-form-item>
      <div class="tips">
        <span>已有账号？</span>
        <router-link to="/login">立即登录</router-link>
      </div>
    </el-form>
  </div>
</template>

<script>
export default {
  name: 'Register',
  data() {
    // 密码验证规则
    const validatePass = (rule, value, callback) => {
      if (value === '') {
        callback(new Error('请输入密码'))
      } else {
        if (this.registerForm.confirmPassword !== '') {
          this.$refs.registerForm.validateField('confirmPassword')
        }
        callback()
      }
    }
    // 确认密码验证规则
    const validatePass2 = (rule, value, callback) => {
      if (value === '') {
        callback(new Error('请再次输入密码'))
      } else if (value !== this.registerForm.password) {
        callback(new Error('两次输入密码不一致!'))
      } else {
        callback()
      }
    }
    
    return {
      registerForm: {
        username: '',
        email: '',
        phone: '',
        company_name: '',
        address: '',
        password: '',
        confirmPassword: ''
      },
      registerRules: {
        username: [
          { required: true, message: '请输入用户名', trigger: 'blur' },
          { min: 3, max: 20, message: '长度在 3 到 20 个字符', trigger: 'blur' }
        ],
        email: [
          { required: true, message: '请输入邮箱地址', trigger: 'blur' },
          { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
        ],
        phone: [
          { required: true, message: '请输入手机号', trigger: 'blur' },
          { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号', trigger: 'blur' }
        ],
        company_name: [
          { max: 100, message: '公司名称不能超过100个字符', trigger: 'blur' }
        ],
        address: [
          { max: 200, message: '地址不能超过200个字符', trigger: 'blur' }
        ],
        password: [
          { required: true, validator: validatePass, trigger: 'blur' },
          { min: 6, message: '密码长度不能小于6位', trigger: 'blur' }
        ],
        confirmPassword: [
          { required: true, validator: validatePass2, trigger: 'blur' }
        ]
      },
      loading: false
    }
  },
  methods: {
    handleRegister() {
      this.$refs.registerForm.validate(async valid => {
        if (valid) {
          this.loading = true
          try {
            const response = await this.$axios.post('/api/users/auth/register/', {
              username: this.registerForm.username,
              email: this.registerForm.email,
              phone: this.registerForm.phone,
              company_name: this.registerForm.company_name,
              address: this.registerForm.address,
              password: this.registerForm.password,
              confirm_password: this.registerForm.confirmPassword
            })
            
            if (response.data.message === '注册成功') {
              this.$message.success('注册成功')
              this.$router.push('/login')
            } else {
              this.$message.error(response.data.message)
            }
          } catch (error) {
            if (error.response?.data) {
              const { message, errors } = error.response.data
              if (errors && errors.length > 0) {
                // 使用 Message Box 显示所有错误
                this.$alert(errors.join('<br>'), '注册失败', {
                  dangerouslyUseHTMLString: true,
                  type: 'error',
                  confirmButtonText: '确定'
                })
              } else {
                this.$message.error(message || '注册失败')
              }
            } else {
              this.$message.error('注册失败，请稍后重试')
            }
          } finally {
            this.loading = false
          }
        }
      })
    }
  }
}
</script>

<style lang="scss" scoped>
.register-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: #f3f3f3;
}

.register-form {
  width: 400px;
  padding: 35px;
  background: #fff;
  border-radius: 5px;
  box-shadow: 0 2px 12px 0 rgba(0,0,0,.1);
  
  .title {
    text-align: center;
    margin-bottom: 30px;
  }
  
  .el-button {
    width: 100%;
  }
  
  .tips {
    text-align: center;
    margin-top: 20px;
    color: #666;
    
    a {
      color: #409EFF;
      margin-left: 10px;
      text-decoration: none;
      
      &:hover {
        text-decoration: underline;
      }
    }
  }
}
</style> 