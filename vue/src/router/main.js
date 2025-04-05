import Vue from 'vue'
import VueRouter from 'vue-router'
import Login from '@/views/Login.vue'
import Register from '@/views/Register.vue'
import Layout from '@/layout/Layout.vue'
import TraceDetail from '@/views/TraceDetail.vue'

Vue.use(VueRouter)

const routes = [
  {
    path: '/trace/:batchNumber',
    name: 'TraceDetail',
    component: TraceDetail,
    meta: { requiresAuth: false }
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
      {
        path: '',  // 添加默认子路由
        redirect: 'dashboard'
      },
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
      
      // 原材料管理
      {
        path: 'materials',
        name: 'Materials',
        component: () => import('@/views/materials/MaterialList'),
        meta: { requiresAuth: true, title: '原材料管理' }
      },
      {
        path: 'materials/batches',
        name: 'MaterialBatches',
        component: () => import('@/views/materials/MaterialBatches'),
        meta: { requiresAuth: true, title: '原材料批次' }
      },
      {
        path: 'materials/suppliers',
        name: 'SupplierList',
        component: () => import('@/views/materials/SupplierList'),
        meta: { requiresAuth: true, title: '供应商管理' }
      },

      // 产品原材料配方路由
      {
        path: 'products/detail/:id/materials',
        name: 'ProductMaterials',
        component: () => import('@/views/products/ProductMaterials'),
        meta: { 
          requiresAuth: true, 
          title: '原材料配方',
          activeMenu: '/products/list'
        },
        hidden: true
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
        meta: { requiresAuth: true, title: '数据概览' }
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
          console.log('Router guard userInfo:', {
            username: userInfo.username,
            role: userInfo.role,
            email: userInfo.email,
            id: userInfo.id
          })
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
          console.log('Router guard userInfo:', {
            username: userInfo.username,
            role: userInfo.role,
            email: userInfo.email,
            id: userInfo.id
          })
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
  },
  {
    path: '*',
    redirect: '/login'
  }
]

const router = new VueRouter({
  mode: 'hash',
  routes
})

router.beforeEach((to, from, next) => {
  console.log('Route check:', {
    path: to.path,
    name: to.name,
    matched: to.matched.map(r => r.path),
    params: to.params,
    fullPath: to.fullPath,
    hash: to.hash
  })

  // 公开路由，不需要登录
  if (to.path.startsWith('/trace/') || to.name === 'TraceDetail' || 
      to.path === '/login' || to.path === '/register') {
    console.log('Public route detected, allowing access without auth')
    next()
    return
  }

  const token = localStorage.getItem('token')
  
  // 未登录，跳转到登录页
  if (!token) {
    next('/login')
    return
  }
  
  // 已登录，检查权限
  const userInfo = JSON.parse(localStorage.getItem('userInfo') || '{}')
  const isAdmin = userInfo.role === 'admin'
  
  // 管理员路由
  const adminRoutes = ['/system/users','/dashboard', '/products', '/products/batches', 
    '/tracing/production', '/tracing/logistics', '/tracing/sales',
    '/trace', '/analysis', '/profile',
    // 添加原材料相关路由
    '/materials', '/materials/batches', '/materials/suppliers']
  // 普通用户路由
  const userRoutes = ['/dashboard', '/products', '/products/batches', 
    '/tracing/production', '/tracing/logistics', '/tracing/sales',
    '/trace', '/analysis', '/profile',
    // 添加原材料相关路由
    '/materials', '/materials/batches', '/materials/suppliers']
  
  // 管理员访问管理员路由
  if (isAdmin && (adminRoutes.includes(to.path) || adminRoutes.some(route => to.path.startsWith(route)))) {
    next()
  }
  // 普通用户访问普通用户路由
  else if (!isAdmin && (userRoutes.includes(to.path) || userRoutes.some(route => to.path.startsWith(route)))) {
    next()
  }
  // 根路径重定向
  else if (to.path === '/') {
    next(isAdmin ? '/system/users' : '/dashboard')
  }
  // 无权限访问
  else {
    next(isAdmin ? '/system/users' : '/dashboard')
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

console.log('TraceDetail component loaded:', TraceDetail)

// 添加路由错误处理
router.onError((error) => {
  console.error('Router error:', error)
})

export default router