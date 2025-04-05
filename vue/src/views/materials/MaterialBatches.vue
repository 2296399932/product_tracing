<template>
  <div class="material-batches-container">
    <div class="page-header">
      <h2 class="page-title">原材料批次管理</h2>
      <el-button v-if="!isAdmin" type="primary" @click="showAddDialog">添加批次</el-button>
    </div>
    
    <!-- 搜索栏 -->
    <el-form :inline="true" :model="searchForm" class="search-form">
      <el-form-item label="原材料">
        <el-select v-model="searchForm.material_id" placeholder="请选择原材料" clearable filterable>
          <el-option 
            v-for="item in materials" 
            :key="item.id" 
            :label="item.name" 
            :value="item.id">
          </el-option>
        </el-select>
      </el-form-item>
      <el-form-item label="批次号">
        <el-input v-model="searchForm.batch_number" placeholder="请输入批次号" clearable></el-input>
      </el-form-item>
      <el-form-item label="状态">
        <el-select v-model="searchForm.status" placeholder="请选择状态" clearable>
          <el-option label="在库" value="in_storage"></el-option>
          <el-option label="已使用" value="used"></el-option>
          <el-option label="已过期" value="expired"></el-option>
          <el-option label="已退货" value="returned"></el-option>
        </el-select>
      </el-form-item>
      <el-form-item label="生产日期">
        <el-date-picker
          v-model="searchForm.production_date"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          value-format="yyyy-MM-dd">
        </el-date-picker>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="handleSearch">搜索</el-button>
        <el-button @click="resetSearch">重置</el-button>
      </el-form-item>
    </el-form>
    
    <!-- 批次表格 -->
    <el-table :data="batches" border style="width: 100%" v-loading="loading">
      <el-table-column prop="material_name" label="原材料" width="150"></el-table-column>
      <el-table-column prop="batch_number" label="批次号" width="120"></el-table-column>
      <el-table-column prop="supplier_name" label="供应商" width="150"></el-table-column>
      <el-table-column prop="production_date" label="生产日期" width="120"></el-table-column>
      <el-table-column prop="expiry_date" label="有效期" width="120"></el-table-column>
      <el-table-column label="数量" width="120">
        <template slot-scope="scope">
          {{ scope.row.quantity || 0 }} {{ scope.row.unit }}
        </template>
      </el-table-column>
      <el-table-column label="采购价" width="120">
        <template slot-scope="scope">
          ¥{{ scope.row.price || 0 }}
        </template>
      </el-table-column>
      <el-table-column prop="status" label="状态" width="100">
        <template slot-scope="scope">
          <el-tag :type="getStatusType(scope.row.status)">
            {{ getStatusText(scope.row.status) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200">
        <template slot-scope="scope">
          <el-button v-if="!isAdmin" size="mini" @click="showEditDialog(scope.row)">编辑</el-button>
          <el-button 
            size="mini" 
            type="warning" 
            @click="changeStatus(scope.row, 'used')"
            v-if="scope.row.status === 'in_storage' && !isAdmin">
            标记使用
          </el-button>
          <el-button 
            size="mini" 
            type="danger" 
            @click="changeStatus(scope.row, 'returned')"
            v-if="scope.row.status === 'in_storage' && !isAdmin">
            退货
          </el-button>
        </template>
      </el-table-column>
    </el-table>
    
    <!-- 分页 -->
    <div class="pagination-container">
      <el-pagination
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
        :current-page="pagination.currentPage"
        :page-sizes="[10, 20, 50, 100]"
        :page-size="pagination.pageSize"
        layout="total, sizes, prev, pager, next, jumper"
        :total="pagination.total">
      </el-pagination>
    </div>
    
    <!-- 添加/编辑批次对话框 -->
    <el-dialog :title="dialogType === 'add' ? '添加批次' : '编辑批次'" :visible.sync="dialogVisible" width="600px">
      <el-form :model="batchForm" :rules="rules" ref="batchForm" label-width="100px">
        <el-form-item label="原材料" prop="material_id" v-if="dialogType === 'add'">
          <el-select v-model="batchForm.material_id" placeholder="请选择原材料" filterable style="width: 100%">
            <el-option 
              v-for="item in materials" 
              :key="item && item.id ? item.id : index"
              :label="item && item.name ? item.name : ''"
              :value="item && item.id ? item.id : null">
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="批次号" prop="batch_number">
          <el-input v-model="batchForm.batch_number" placeholder="请输入批次号" :disabled="dialogType === 'edit'"></el-input>
        </el-form-item>
        <el-form-item label="供应商" prop="supplier_id">
          <el-select 
            v-model="batchForm.supplier_id" 
            placeholder="请选择供应商" 
            filterable 
            style="width: 100%"
            @change="handleSupplierChange">
            <el-option 
              v-for="(item, index) in suppliers" 
              :key="item && item.id ? item.id : 'supplier-' + index"
              :label="item && item.name ? item.name : ''"
              :value="item && item.id ? item.id : null">
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="生产日期" prop="production_date">
          <el-date-picker
            v-model="batchForm.production_date"
            type="date"
            placeholder="选择日期"
            value-format="yyyy-MM-dd"
            style="width: 100%">
          </el-date-picker>
        </el-form-item>
        <el-form-item label="有效期" prop="expiry_date">
          <el-date-picker
            v-model="batchForm.expiry_date"
            type="date"
            placeholder="选择日期"
            value-format="yyyy-MM-dd"
            style="width: 100%">
          </el-date-picker>
        </el-form-item>
        <el-form-item label="数量" prop="quantity">
          <el-input-number v-model="batchForm.quantity" :min="0" :precision="2" style="width: 100%"></el-input-number>
        </el-form-item>
        <el-form-item label="单位" prop="unit">
          <el-select v-model="batchForm.unit" placeholder="请选择单位" style="width: 100%">
            <el-option 
              v-for="item in unitOptions" 
              :key="item" 
              :label="item" 
              :value="item">
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="采购价" prop="price">
          <el-input-number v-model="batchForm.price" :min="0" :precision="2" style="width: 100%"></el-input-number>
        </el-form-item>
     
        <el-form-item label="状态" prop="status">
          <el-select v-model="batchForm.status" placeholder="请选择状态" style="width: 100%">
            <el-option label="在库" value="in_storage"></el-option>
            <el-option label="已使用" value="used"></el-option>
            <el-option label="已过期" value="expired"></el-option>
            <el-option label="已退货" value="returned"></el-option>
          </el-select>
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="dialogVisible = false">取 消</el-button>
        <el-button type="primary" @click="submitForm">确 定</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
export default {
  name: 'MaterialBatches',
  data() {
    return {
         isAdmin: JSON.parse(localStorage.getItem('userInfo') || '{}').role === 'admin',
      material: {},
      batches: [],
      loading: false,
      dialogVisible: false,
      dialogType: 'add',
      searchForm: {
        material_id: '',
        batch_number: '',
        status: '',
        production_date: []
      },
      batchForm: {
        id: null,
        material_id: null,
        batch_number: '',
        supplier_id: null,
        quantity: 1,
        unit: 'kg',
        production_date: '',
        expiry_date: '',
        price: 0,
        quality_certificate: '',
        status: 'in_storage'
      },
      rules: {
        batch_number: [{ required: true, message: '请输入批次号', trigger: 'blur' }],
        supplier_id: [{ required: true, message: '请选择供应商', trigger: 'change' }],
        quantity: [{ required: true, message: '请输入数量', trigger: 'blur' }],
        unit: [{ required: true, message: '请选择单位', trigger: 'change' }],
        production_date: [{ required: true, message: '请选择生产日期', trigger: 'change' }],
        expiry_date: [{ required: true, message: '请选择过期日期', trigger: 'change' }]
      },
      suppliers: [],
      unitOptions: ['kg', 'g', 'l', 'ml', '箱', '个', '袋'],
      materials: [],
      pagination: {
        currentPage: 1,
        pageSize: 10,
        total: 0
      }
    };
  },
  created() {
    const materialId = this.$route.params.materialId || null
    // 获取所有材料列表
    this.fetchMaterials()
    this.fetchSuppliers()
    
    if (materialId) {
      // 如果有指定材料ID，设置搜索条件并获取该材料的批次
      this.searchForm.material_id = materialId
      this.fetchMaterial(materialId)
      this.fetchBatches(materialId)
    } else {
      // 如果没有指定材料ID，获取所有批次
      this.fetchBatches()
    }
  },
  methods: {
    async fetchMaterial(id) {
      if (!id) return;
      
      try {
        const response = await this.$axios.get(this.$httpUrl + `/api/materials/materials/${id}/`)
        this.material = response.data
      } catch (error) {
        this.$message.error('获取材料信息失败')
        console.error(error)
        this.material = {}  // 失败时设置为空对象而不是 null
      }
    },
    async fetchSuppliers() {
      try {
        const response = await this.$axios.get(this.$httpUrl + '/api/materials/suppliers/', {
          params: { page: 1, page_size: 100 }
        });
        this.suppliers = (response.data.results || response.data || []).filter(s => s != null);
      } catch (error) {
        this.$message.error('获取供应商列表失败');
        console.error('获取供应商列表失败:', error);
        this.suppliers = [];
      }
    },
    async fetchBatches(materialId = null) {
      this.loading = true
      try {
        const params = {
          page: this.pagination.currentPage,
          page_size: this.pagination.pageSize
        }
        
        // 添加搜索条件
        if (materialId || this.searchForm.material_id) {
          params.material_id = materialId || this.searchForm.material_id
        }
        if (this.searchForm.batch_number) {
          params.batch_number__icontains = this.searchForm.batch_number
        }
        if (this.searchForm.status) {
          params.status = this.searchForm.status
        }
        if (this.searchForm.production_date && this.searchForm.production_date.length === 2) {
          params.production_date_start = this.searchForm.production_date[0]
          params.production_date_end = this.searchForm.production_date[1]
        }

        const response = await this.$axios.get(this.$httpUrl + '/api/materials/batches/', { params })
        this.batches = response.data.results || response.data
        if (response.data.count !== undefined) {
          this.pagination.total = response.data.count
        }
      } catch (error) {
        this.$message.error('获取批次列表失败')
        console.error('获取批次列表失败:', error)
      } finally {
        this.loading = false
      }
    },
    showAddDialog() {
      this.dialogType = 'add';
      this.batchForm = {
        material_id: this.$route.params.materialId || null,
        batch_number: '',
        supplier_id: null,
        quantity: 1,
        unit: 'kg',
        production_date: '',
        expiry_date: '',
        price: 0,
        quality_certificate: '',
        status: 'in_storage'
      };
      this.dialogVisible = true;
      this.$nextTick(() => {
        this.$refs.batchForm && this.$refs.batchForm.clearValidate();
      });
    },
    async showEditDialog(row) {
      this.dialogType = 'edit';
      this.batchForm = {
        id: row.id,
        material_id: row.material,
        batch_number: row.batch_number,
        supplier_id: row.supplier,
        quantity: row.quantity,
        unit: row.unit,
        production_date: row.production_date,
        expiry_date: row.expiry_date,
        price: row.price || 0,
        status: row.status
      };
      
      // 获取供应商价格
      if (row.material && row.supplier) {
        const price = await this.getSupplierPrice(row.material, row.supplier)
        this.batchForm.price = price || row.price || 0
      }
      
      this.dialogVisible = true;
      this.$nextTick(() => {
        this.$refs.batchForm && this.$refs.batchForm.clearValidate();
      });
    },
    submitForm() {
      this.$refs.batchForm.validate(valid => {
        if (valid) {
          const isAdd = this.dialogType === 'add';
          const method = isAdd ? 'post' : 'put';
          const url = isAdd 
            ? this.$httpUrl + '/api/materials/batches/' 
            : this.$httpUrl + `/api/materials/batches/${this.batchForm.id}/`;
          
          // 准备提交的数据，确保 material 字段有值
          const materialId = this.batchForm.material_id || this.$route.params.materialId;
          if (!materialId) {
            this.$message.error('请选择原材料');
            return;
          }
          
          const submitData = {
            material: materialId,
            supplier: this.batchForm.supplier_id,
            batch_number: this.batchForm.batch_number,
            quantity: this.batchForm.quantity,
            unit: this.batchForm.unit,
            production_date: this.batchForm.production_date,
            expiry_date: this.batchForm.expiry_date,
            price: this.batchForm.price || 0,
            status: this.batchForm.status
          };
          
          this.loading = true;
          this.$axios[method](url, submitData)
            .then(() => {
              this.$message.success(isAdd ? '添加成功' : '更新成功');
              this.dialogVisible = false;
              this.fetchBatches(this.$route.params.materialId);
            })
            .catch(error => {
              console.error(isAdd ? '添加失败:' : '更新失败:', error);
              // 显示具体的错误信息
              if (error.response && error.response.data) {
                const errorMsg = Object.entries(error.response.data)
                  .map(([key, value]) => `${key}: ${value}`)
                  .join('\n');
                this.$message.error(errorMsg);
              } else {
                this.$message.error(isAdd ? '添加失败' : '更新失败');
              }
            })
            .finally(() => {
              this.loading = false;
            });
        }
      });
    },
    changeStatus(row, status) {
      const statusMap = {
        'used': '使用',
        'expired': '过期',
        'returned': '退货'
      };
      
      this.$confirm(`确认将该批次标记为${statusMap[status]}?`, '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        this.$axios.patch(this.$httpUrl + `/api/materials/batches/${row.id}/`, { status })
          .then(() => {
            this.$message.success(`标记为${statusMap[status]}成功`);
            this.fetchBatches(this.$route.params.materialId);
          })
          .catch(error => {
            console.error(`标记失败:`, error);
            this.$message.error(`标记失败`);
          });
      }).catch(() => {});
    },
    getStatusType(status) {
      const statusMap = {
        'in_storage': 'success',
        'used': 'info',
        'expired': 'danger',
        'returned': 'warning'
      };
      return statusMap[status] || 'info';
    },
    getStatusText(status) {
      const statusMap = {
        'in_storage': '在库',
        'used': '已使用',
        'expired': '已过期',
        'returned': '已退货'
      };
      return statusMap[status] || status;
    },
    handleSearch() {
      this.pagination.currentPage = 1
      this.fetchBatches()
    },
    resetSearch() {
      const materialId = this.$route.params.materialId
      this.searchForm = {
        material_id: materialId || '', // 如果有指定材料ID，保留该条件
        batch_number: '',
        status: '',
        production_date: []
      }
      this.pagination.currentPage = 1
      this.fetchBatches(materialId)
    },
    handleSizeChange(val) {
      this.pagination.pageSize = val;
      this.fetchBatches();
    },
    handleCurrentChange(val) {
      this.pagination.currentPage = val;
      this.fetchBatches();
    },
    async fetchMaterials() {
      try {
        const response = await this.$axios.get(this.$httpUrl + '/api/materials/materials/', {
          params: { page: 1, page_size: 100, status: 'active' }
        });
        this.materials = (response.data.results || response.data || []).filter(m => m != null);
      } catch (error) {
        this.$message.error('获取材料列表失败');
        console.error(error);
        this.materials = [];
      }
    },
    async getSupplierPrice(materialId, supplierId) {
      if (!materialId || !supplierId) return 0;
      
      try {
        const response = await this.$axios.get(
          this.$httpUrl + `/api/materials/materials/${materialId}/suppliers/`
        )
        
        // 打印完整响应，查看数据结构
        console.log('供应商关联数据:', response.data)
        console.log('查找的供应商ID:', supplierId)
        
        // 尝试不同的查找方式
        let materialSupplier = null
        
        // 方法1: 直接使用supplier字段
        materialSupplier = response.data.find(ms => ms.supplier === parseInt(supplierId))
        
        // 方法2: 如果方法1失败，尝试使用supplier_id字段
        if (!materialSupplier) {
          materialSupplier = response.data.find(ms => ms.supplier_id === parseInt(supplierId))
        }
        
        // 方法3: 如果前两种方法都失败，尝试查找supplier对象
        if (!materialSupplier) {
          materialSupplier = response.data.find(ms => 
            (ms.supplier && typeof ms.supplier === 'object' && ms.supplier.id === parseInt(supplierId))
          )
        }
        
        console.log('找到的供应商关联:', materialSupplier)
        return materialSupplier && materialSupplier.price ? materialSupplier.price : 0
      } catch (error) {
        console.error('获取供应商价格失败:', error)
        return 0
      }
    },
    async handleSupplierChange(supplierId) {
      if (supplierId && this.batchForm.material_id) {
        const price = await this.getSupplierPrice(this.batchForm.material_id, supplierId)
        this.batchForm.price = price || 0
      }
    }
  }
};
</script>

<style scoped>
.material-batches-container {
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

.search-form {
  margin-bottom: 20px;
  padding: 15px;
  background: var(--background-primary);
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.pagination-container {
  margin-top: 20px;
  text-align: right;
}
</style> 