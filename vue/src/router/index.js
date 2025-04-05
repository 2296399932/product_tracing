{
  path: '/materials/batches/:materialId?',
  name: 'MaterialBatches',
  component: () => import('../views/materials/MaterialBatches.vue'),
  meta: { requiresAuth: true }
} 