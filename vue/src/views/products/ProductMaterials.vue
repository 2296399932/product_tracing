<template>
  <div class="product-materials-container">
    <div class="page-header">
      <h2 class="page-title">{{ product.name }} - 原材料配方</h2>
      <el-button type="primary" @click="showAddDialog">添加原材料</el-button>
    </div>
    
    <el-table :data="productMaterials" border style="width: 100%" v-loading="loading">
      <el-table-column prop="material_name" label="原材料名称" width="180"></el-table-column>
      <el-table-column prop="batch_number" label="批次号" width="150"></el-table-column>
      <el-table-column prop="quantity" label="使用数量" width="120"></el-table-column>
      <el-table-column prop="unit" label="单位" width="80"></el-table-column>
      <el-table-column prop="supplier_name" label="供应商"></el-table-column>
      <el-table-column label="操作" width="120">
        <template slot-scope="scope">
          <el-button size="small" type="danger" @click="handleDelete(scope.row)">
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>
    
    <!-- 添加原材料对话框 -->
    <el-dialog title="添加原材料" :visible.sync="dialogVisible" width="600px">
      <el-form :model="form" :rules="rules" ref="materialForm" label-width="100px">
        <el-form-item label="原材料" prop="material_batch_id">
          <el-select 
            v-model="form.material_batch_id" 
            filterable 
            placeholder="选择原材料批次"
            style="width: 100%">
            <el-option
              v-for="item in materialBatches"
              :key="item.id"
              :label="`${item.material_name} (${item.batch_number})`"
              :value="item.id">
              <div>
                <div>{{ item.material_name }} - {{ item.batch_number }}</div>
                <small style="color: #999">
                  供应商: {{ item.supplier_name }} | 
                  库存: {{ item.quantity }}{{ item.unit }}
                </small>
              </div>
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="使用数量" prop="quantity">
          <el-input-number v-model="form.quantity" :min="0.01" :precision="2"></el-input-number>
        </el-form-item>
        <el-form-item label="单位" prop="unit">
          <el-input v-model="form.unit"></el-input>
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm">确定</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import api from '@/api'

export default {
  name: 'ProductMaterials',
  data() {
    return {
      product: {},
      productMaterials: [],
      materialBatches: [],
      loading: false,
      dialogVisible: false,
      form: {
        material_batch_id: '',
        quantity: 1,
        unit: ''
      },
      rules: {
        material_batch_id: [
          { required: true, message: '请选择原材料批次', trigger: 'change' }
        ],
        quantity: [
          { required: true, message: '请输入使用数量', trigger: 'blur' }
        ],
        unit: [
          { required: true, message: '请输入单位', trigger: 'blur' }
        ]
      }
    }
  },
  created() {
    this.fetchProduct()
    this.fetchProductMaterials()
    this.fetchMaterialBatches()
  },
  methods: {
    async fetchProduct() {
      try {
        const response = await api.get(`/products/${this.$route.params.id}/`)
        this.product = response.data
      } catch (error) {
        this.$message.error('获取产品信息失败')
        console.error(error)
      }
    },
    async fetchProductMaterials() {
      this.loading = true
      try {
        const response = await api.get(`/products/${this.$route.params.id}/materials/`)
        this.productMaterials = response.data
      } catch (error) {
        this.$message.error('获取原材料配方失败')
        console.error(error)
      } finally {
        this.loading = false
      }
    },
    async fetchMaterialBatches() {
      try {
        const response = await api.get('/materials/batches/', {
          params: { status: 'in_storage' }
        })
        this.materialBatches = response.data
      } catch (error) {
        this.$message.error('获取原材料批次失败')
        console.error(error)
      }
    },
    showAddDialog() {
      this.form = {
        material_batch_id: '',
        quantity: 1,
        unit: ''
      }
      this.dialogVisible = true
    },
    async submitForm() {
      this.$refs.materialForm.validate(async valid => {
        if (valid) {
          try {
            await api.post(`/products/${this.$route.params.id}/materials/`, this.form)
            this.$message.success('添加成功')
            this.dialogVisible = false
            this.fetchProductMaterials()
          } catch (error) {
            this.$message.error('添加失败')
            console.error(error)
          }
        }
      })
    },
    handleDelete(row) {
      this.$confirm('确认删除该原材料配方?', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(async () => {
        try {
          await api.delete(`/products/${this.$route.params.id}/materials/${row.id}/`)
          this.$message.success('删除成功')
          this.fetchProductMaterials()
        } catch (error) {
          this.$message.error('删除失败')
          console.error(error)
        }
      }).catch(() => {})
    }
  }
}
</script>

<style scoped>
.product-materials-container {
  padding: 20px;
  background: var(--background-secondary);
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-title {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
}
</style> 