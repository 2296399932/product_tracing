<template>
  <el-container class="layout-container">
    <el-aside :width="isCollapse ? '64px' : '200px'">
      <div class="logo-container">
        <img src="@/assets/logo.png" class="logo-img">
        <span class="logo-text" v-show="!isCollapse">产品追溯系统</span>
      </div>
      <el-menu
        :default-active="$route.path"
        class="el-menu-vertical"
        background-color="#304156"
        text-color="#fff"
        active-text-color="#409EFF"
        :collapse="isCollapse"
        :collapse-transition="false"
        router>
        
        <!-- 仪表盘 -->
        <el-menu-item index="/dashboard">
          <i class="el-icon-monitor"></i>
          <span slot="title">仪表盘</span>
        </el-menu-item>

        <!-- 个人中心 -->
        <el-menu-item index="/profile">
          <i class="el-icon-user"></i>
          <span slot="title">个人中心</span>
        </el-menu-item>

        <!-- 系统管理 - 仅管理员可见 -->
        <el-submenu index="system" v-if="userInfo.role === 'admin'">
          <template slot="title">
            <i class="el-icon-setting"></i>
            <span>系统管理</span>
          </template>
          <el-menu-item index="/system/users">用户管理</el-menu-item>
        </el-submenu>

        <!-- 产品管理 -->
        <el-submenu index="products">
          <template slot="title">
            <i class="el-icon-goods"></i>
            <span>产品管理</span>
          </template>
          <el-menu-item index="/products">商品列表</el-menu-item>
          <el-menu-item index="/products/batches">批次管理</el-menu-item>
        </el-submenu>
        
        <!-- 追溯管理 -->
        <el-submenu index="tracing">
          <template slot="title">
            <i class="el-icon-document"></i>
            <span>追溯管理</span>
          </template>
          <el-menu-item index="/tracing/production">生产记录</el-menu-item>
          <el-menu-item index="/tracing/logistics">物流记录</el-menu-item>
          <el-menu-item index="/tracing/sales">销售记录</el-menu-item>
        </el-submenu>

        <!-- 追溯查询 -->
        <el-menu-item index="/trace">
          <i class="el-icon-search"></i>
          <span slot="title">追溯查询</span>
        </el-menu-item>

        <!-- 数据分析 -->
        <el-menu-item index="/analysis">
          <i class="el-icon-data-analysis"></i>
          <span slot="title">数据分析</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    
    <el-container>
      <el-header>
        <div class="header-left">
          <i 
            :class="isCollapse ? 'el-icon-s-unfold' : 'el-icon-s-fold'"
            @click="toggleCollapse"
            class="collapse-btn">
          </i>
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item v-for="(item, index) in breadcrumbs" 
              :key="index">{{ item }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <div class="header-right">
          <!-- 全屏按钮 -->
          <el-tooltip content="全屏" placement="bottom">
            <i class="header-icon" 
              :class="isFullscreen ? 'el-icon-aim' : 'el-icon-full-screen'"
              @click="toggleFullScreen">
            </i>
          </el-tooltip>
          
          <!-- 用户信息 -->
          <!-- 通知 -->
      

          <!-- 用户信息 -->
          <el-dropdown @command="handleCommand" trigger="click">
            <span class="el-dropdown-link">
              <el-avatar size="small" :src="userInfo.avatar || defaultAvatar"></el-avatar>
              <span class="username">{{ userInfo.username }}</span>
              <i class="el-icon-arrow-down el-icon--right"></i>
            </span>
            <el-dropdown-menu slot="dropdown">
              <el-dropdown-item command="profile">
                <i class="el-icon-user"></i> 个人信息
              </el-dropdown-item>
       
              <el-dropdown-item divided command="logout">
                <i class="el-icon-switch-button"></i> 退出登录
              </el-dropdown-item>
            </el-dropdown-menu>
          </el-dropdown>
        </div>
      </el-header>
      
      <el-main>
        <transition name="fade-transform" mode="out-in">
          <router-view></router-view>
        </transition>
      </el-main>
    </el-container>

    <!-- 通知抽屉 -->
    <el-drawer
      title="通知中心"
      :visible.sync="notificationDrawer"
      direction="rtl"
      size="300px">
      <el-tabs v-model="activeNotificationTab">
        <el-tab-pane label="未读消息" name="unread">
          <div v-if="unreadNotifications.length === 0" class="empty-text">
            暂无未读消息
          </div>
          <div v-else class="notification-list">
            <div v-for="item in unreadNotifications" 
              :key="item.id" 
              class="notification-item">
              <div class="notification-title">{{ item.title }}</div>
              <div class="notification-content">{{ item.content }}</div>
              <div class="notification-time">{{ item.time }}</div>
            </div>
          </div>
        </el-tab-pane>
        <el-tab-pane label="全部消息" name="all">
          <!-- 全部消息列表 -->
        </el-tab-pane>
      </el-tabs>
    </el-drawer>
  </el-container>
</template>

<script>
export default {
  name: 'MainLayout',
  data() {
    return {
      isCollapse: false,
      isFullscreen: false,
      userInfo: JSON.parse(localStorage.getItem('userInfo') || '{}'),
      defaultAvatar: '', // Element UI 会显示默认头像
      notificationCount: 0,
      notificationDrawer: false,
      activeNotificationTab: 'unread',
      unreadNotifications: [],
      breadcrumbs: []
    }
  },
  watch: {
    '$route': {
      handler: function(route) {
        this.updateBreadcrumbs(route)
      },
      immediate: true
    }
  },
  created() {
    console.log('Layout userInfo:', {
      username: this.userInfo.username,
      role: this.userInfo.role,
      email: this.userInfo.email,
      id: this.userInfo.id
    })
  },
  methods: {
    toggleCollapse() {
      this.isCollapse = !this.isCollapse
    },
    toggleFullScreen() {
      if (!document.fullscreenElement) {
        document.documentElement.requestFullscreen()
        this.isFullscreen = true
      } else {
        if (document.exitFullscreen) {
          document.exitFullscreen()
          this.isFullscreen = false
        }
      }
    },
    handleCommand(command) {
      if (command === 'logout') {
        this.$confirm('确认退出登录?', '提示', {
          type: 'warning'
        }).then(() => {
          // 调用登出API
          this.$axios.post(this.$httpUrl + '/api/users/auth/logout/')
            .then(() => {
              localStorage.removeItem('token')
              localStorage.removeItem('userInfo')
              this.$router.push('/login')
            })
            .catch(err => {
              console.error('登出失败:', err)
              // 即使API调用失败也清除本地存储
              localStorage.removeItem('token')
              localStorage.removeItem('userInfo')
              this.$router.push('/login')
            })
        })
      } else if (command === 'profile') {
        this.$router.push('/profile')
      } else if (command === 'settings') {
        this.$router.push('/settings')
      }
    },
    updateBreadcrumbs(route) {
      // 根据路由更新面包屑
      this.breadcrumbs = route.matched
        .filter(item => item.meta && item.meta.title)
        .map(item => item.meta.title)
    }
  }
}
</script>

<style scoped>
.layout-container {
  height: 100vh;
}
.logo-container {
  height: 60px;
  padding: 10px;
  display: flex;
  align-items: center;
  background: #2b2f3a;
}
.logo-img {
  height: 32px;
  width: 32px;
  margin-right: 12px;
}
.logo-text {
  color: #fff;
  font-size: 20px;
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
}
.el-header {
  background-color: #fff;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 1px 4px rgba(0,21,41,.08);
  padding: 0 20px;
}
.header-left {
  display: flex;
  align-items: center;
}
.collapse-btn {
  font-size: 20px;
  margin-right: 20px;
  cursor: pointer;
}
.header-right {
  display: flex;
  align-items: center;
}
.header-icon {
  font-size: 20px;
  padding: 0 10px;
  cursor: pointer;
  color: #666;
}
.header-icon:hover {
  color: #409EFF;
}
.notification-badge {
  margin: 0 10px;
}
.el-dropdown-link {
  display: flex;
  align-items: center;
  cursor: pointer;
}
.username {
  margin: 0 8px;
  color: #666;
}
.el-aside {
  background-color: #304156;
  transition: width 0.3s;
  overflow-x: hidden;
}
.el-menu {
  border-right: none;
}
.el-menu:not(.el-menu--collapse) {
  width: 200px;
}
.notification-list {
  padding: 10px;
}
.notification-item {
  padding: 10px;
  border-bottom: 1px solid #eee;
}
.notification-title {
  font-weight: bold;
  margin-bottom: 5px;
}
.notification-content {
  color: #666;
  font-size: 14px;
}
.notification-time {
  color: #999;
  font-size: 12px;
  margin-top: 5px;
}
.empty-text {
  text-align: center;
  color: #999;
  padding: 20px;
}
/* 路由过渡动画 */
.fade-transform-enter-active,
.fade-transform-leave-active {
  transition: all .5s;
}
.fade-transform-enter {
  opacity: 0;
  transform: translateX(-30px);
}
.fade-transform-leave-to {
  opacity: 0;
  transform: translateX(30px);
}
</style> 