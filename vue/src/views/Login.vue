<template>
  <div class="login-container">
    <el-form ref="loginForm" :model="loginForm" :rules="loginRules" class="login-form">
      <h3 class="title">商品追溯系统</h3>
      <el-form-item prop="username">
        <el-input v-model="loginForm.username" placeholder="用户名" />
      </el-form-item>
      <el-form-item prop="password">
        <el-input v-model="loginForm.password" type="password" placeholder="密码" />
      </el-form-item>
      <el-form-item>
        <el-button :loading="loading" type="primary" @click="handleLogin">登录</el-button>
      </el-form-item>
      <div class="tips">
        <span>还没有账号？</span>
        <router-link to="/register">立即注册</router-link>
      </div>
    </el-form>
  </div>
</template>

<script>
export default {
  name: 'Login',
  data() {
    return {
      loginForm: {
        username: '',
        password: ''
      },
      loginRules: {
        username: [
          { required: true, message: '请输入用户名', trigger: 'blur' },
          { min: 3, max: 20, message: '用户名长度在 3 到 20 个字符', trigger: 'blur' }
        ],
        password: [
          { required: true, message: '请输入密码', trigger: 'blur' },
          { min: 6, message: '密码长度不能小于6个字符', trigger: 'blur' }
        ]
      },
      loading: false
    }
  },
  methods: {
    handleLogin() {
      this.$refs.loginForm.validate(async valid => {
        if (valid) {
          this.loading = true
          try {
            const response = await this.$axios.post('/api/users/auth/login/', this.loginForm)
            console.log('Login response:', response)
            
            if (response.data && response.data.token) {
              console.log('Storing token:', response.data.token)
              localStorage.setItem('token', response.data.token)
              localStorage.setItem('userInfo', JSON.stringify(response.data.user))
              
              this.$message.success('登录成功')
              this.$router.push('/')
            } else {
              this.$message.error('登录失败：响应格式错误')
              console.error('Invalid login response:', response)
            }
          } catch (error) {
            console.error('Login error:', error)
            this.$message.error(error.response?.data?.error || '登录失败')
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
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: #f3f3f3;
}

.login-form {
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
</style> 