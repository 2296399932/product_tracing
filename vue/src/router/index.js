router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  
  if (to.path === '/login') {
    if (token) {
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

const routes = [
  {
    path: '/trace',
    name: 'Trace',
    component: () => import('@/views/tracing/Trace.vue'),
    meta: { requiresAuth: true }
  }
] 