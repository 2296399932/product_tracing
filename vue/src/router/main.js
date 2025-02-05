import Vue from 'vue'
import VueRouter from 'vue-router'
import Login from '@/views/Login.vue'
import Register from '@/views/Register.vue'
import Layout from '@/layout/Layout.vue'

Vue.use(VueRouter)

const routes = [
  {
    path: '/',
    redirect: '/dashboard'
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { requiresAuth: false }
  },
  {
    path: '/register',
    name: 'Register',
    component: Register,
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    component: Layout,
    children: [
      // 仪表盘
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/Dashboard.vue'),
        meta: { 
          requiresAuth: true,
          title: '仪表盘'
        }
      },
      
      // 产品管理
      {
        path: 'products',
        name: 'Products',
        component: () => import('@/views/products/Products.vue'),
        meta: { requiresAuth: true, title: '商品管理' }
      },
      {
        path: 'products/batches',
        name: 'Batches',
        component: () => import('@/views/products/Batches.vue'),
        meta: { requiresAuth: true, title: '批次管理' }
      },

      // 追溯管理
      {
        path: 'tracing/production',
        name: 'Production',
        component: () => import('@/views/tracing/Production.vue'),
        meta: { requiresAuth: true, title: '生产记录' }
      },
      {
        path: 'tracing/logistics',
        name: 'Logistics',
        component: () => import('@/views/tracing/Logistics.vue'),
        meta: { requiresAuth: true, title: '物流记录' }
      },
      {
        path: 'tracing/sales',
        name: 'Sales',
        component: () => import('@/views/tracing/Sales.vue'),
        meta: { requiresAuth: true, title: '销售记录' }
      },

      // 追溯查询
      {
        path: 'trace',
        name: 'Trace',
        component: () => import('@/views/tracing/Trace.vue'),
        meta: { requiresAuth: true, title: '追溯查询' }
      },

      // 数据分析
      {
        path: 'analysis',
        name: 'Analysis',
        component: () => import('@/views/analysis/Analysis.vue'),
        meta: { requiresAuth: true, title: '数据分析' }
      },

      // 系统管理
      {
        path: 'system/users',
        name: 'Users',
        component: () => import('@/views/system/Users.vue'),
        meta: {
          requiresAdmin: true,
          title: '用户管理'
        },
        beforeEnter: (to, from, next) => {
          const userInfo = JSON.parse(localStorage.getItem('userInfo') || '{}')
          if (userInfo.role === 'admin') {
            next()
          } else {
            next('/')
          }
        }
      },
      // 用户详情
      {
        path: 'system/users/:id',
        name: 'UserDetail',
        component: () => import('@/views/system/Users.vue'),
        meta: {
          requiresAdmin: true,
          title: '用户详情'
        },
        beforeEnter: (to, from, next) => {
          const userInfo = JSON.parse(localStorage.getItem('userInfo') || '{}')
          if (userInfo.role === 'admin') {
            next()
          } else {
            next('/')
          }
        }
      },
      {
        path: 'profile',
        name: 'Profile',
        component: () => import('@/views/Profile.vue'),
        meta: { requiresAuth: true, title: '个人中心' }
      }
    ]
  }
]

const router = new VueRouter({
  routes
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  
  if (to.meta.requiresAuth === false) {
    // 登录和注册页面不需要验证
    if (token && (to.path === '/login' || to.path === '/register')) {
      next('/')
    } else {
      next()
    }
  } else {
    if (token) {
      next()
    } else {
      next('/login')
    }
  }
})

// 全局前置守卫
// router.beforeEach((to, from, next) => {
//     const user = store.state.user; // 假设用户信息保存在 Vuex 的 store 中
//     const isAuthenticated = !!user; // 判断用户是否已登录
//
//     if (to.meta.requiresAuth && !isAuthenticated) {
//         // 如果需要认证且用户未登录，重定向到登录页面
//         next('/');
//     } else if (to.meta.roles && !to.meta.roles.includes(user.role_id)) {
//         // 如果角色不符合要求，重定向到未授权页面或其他页面
//         next('/'); // 或者 `next({ path: '/unauthorized' })`
//     } else {
//         // 允许访问
//         next();
//     }
// });
export default router