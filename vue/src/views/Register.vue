<template>
  <div class="register-container">
    <el-form ref="registerForm" :model="registerForm" :rules="registerRules" class="register-form">
      <h3 class="title">用户注册</h3>
      <el-form-item prop="username">
        <el-input v-model="registerForm.username" placeholder="用户名" />
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
        password: '',
        confirmPassword: ''
      },
      registerRules: {
        username: [
          { required: true, message: '请输入用户名', trigger: 'blur' },
          { min: 3, max: 20, message: '长度在 3 到 20 个字符', trigger: 'blur' }
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
  width: 350px;
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