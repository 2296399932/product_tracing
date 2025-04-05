<template>
  <div class="material-container">
    <div class="page-header">
      <h2 class="page-title">原材料管理</h2>
      <el-button   v-if="!isAdmin" type="primary" @click="showAddDialog">添加原材料</el-button>
    </div>
    
    <!-- 搜索栏 -->
    <el-form :inline="true" :model="searchForm" class="search-form">
      <el-form-item label="原材料名称">
        <el-input v-model="searchForm.name" placeholder="请输入名称" clearable></el-input>
      </el-form-item>
      <el-form-item label="分类">
        <el-select v-model="searchForm.category" placeholder="请选择分类" clearable>
          <el-option v-for="item in categoryOptions" :key="item" :label="item" :value="item"></el-option>
        </el-select>
      </el-form-item>
      <el-form-item label="状态">
        <el-select v-model="searchForm.status" placeholder="请选择状态" clearable>
          <el-option label="活跃" value="active"></el-option>
          <el-option label="停用" value="inactive"></el-option>
        </el-select>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="handleSearch">搜索</el-button>
        <el-button @click="resetSearch">重置</el-button>
      </el-form-item>
    </el-form>
    
    <!-- 原材料表格 -->
    <el-table :data="materials" border style="width: 100%" v-loading="loading">
      <el-table-column prop="code" label="编码" width="120"></el-table-column>
      <el-table-column prop="name" label="名称" width="180"></el-table-column>
      <el-table-column prop="category" label="分类" width="120"></el-table-column>
      <el-table-column prop="specification" label="规格"></el-table-column>
      <el-table-column prop="origin" label="产地" width="150"></el-table-column>
      <el-table-column label="供应商" width="180">
        <template slot-scope="scope">
          <el-tag 
            v-for="supplier in getSuppliers(scope.row)" 
            :key="supplier.id"
            size="small"
            :type="supplier.is_preferred ? 'success' : 'info'"
            style="margin-right: 5px; margin-bottom: 5px;">
            {{ supplier.supplier_name }}
          </el-tag>
          <span v-if="!getSuppliers(scope.row).length" class="no-data">无供应商</span>
        </template>
      </el-table-column>
      <el-table-column prop="status" label="状态" width="100">
        <template slot-scope="scope">
          <el-tag :type="scope.row.status === 'active' ? 'success' : 'info'">
            {{ scope.row.status === 'active' ? '活跃' : '停用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="300">
        <template slot-scope="scope">
          <el-button v-if="!isAdmin" size="mini" @click="showEditDialog(scope.row)">编辑</el-button>
          <el-button  v-if="!isAdmin" size="mini" type="success" @click="manageSuppliers(scope.row)">供应商</el-button>
          <el-button  v-if="!isAdmin" size="mini" type="primary" @click="viewBatches(scope.row)">批次</el-button>
          <el-button v-if="!isAdmin" size="mini" type="danger" @click="handleDelete(scope.row)">删除</el-button>
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
    
    <!-- 添加/编辑原材料对话框 -->
    <el-dialog :title="dialogType === 'add' ? '添加原材料' : '编辑原材料'" :visible.sync="dialogVisible" width="600px">
      <el-form :model="materialForm" :rules="rules" ref="materialForm" label-width="100px">
        <el-form-item label="名称" prop="name">
          <el-input v-model="materialForm.name" placeholder="请输入原材料名称"></el-input>
        </el-form-item>
        <el-form-item label="编码" prop="code">
          <el-input v-model="materialForm.code" placeholder="请输入原材料编码" :disabled="dialogType === 'edit'"></el-input>
        </el-form-item>
        <el-form-item label="分类" prop="category">
          <el-select v-model="materialForm.category" placeholder="请选择分类" style="width: 100%">
            <el-option v-for="item in categoryOptions" :key="item" :label="item" :value="item"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="规格" prop="specification">
          <el-input v-model="materialForm.specification" placeholder="请输入规格"></el-input>
        </el-form-item>
        <el-form-item label="产地" prop="origin">
          <el-input v-model="materialForm.origin" placeholder="请输入产地"></el-input>
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input type="textarea" v-model="materialForm.description" placeholder="请输入描述"></el-input>
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-radio-group v-model="materialForm.status">
            <el-radio label="active">活跃</el-radio>
            <el-radio label="inactive">停用</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="供应商" prop="selectedSuppliers">
          <el-select
            v-model="materialForm.selectedSuppliers"
            multiple
            filterable
            placeholder="请选择供应商"
            style="width: 100%">
            <el-option
              v-for="item in allSuppliers"
              :key="item.id"
              :label="item.name"
              :value="item.id">
            </el-option>
          </el-select>
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="dialogVisible = false">取 消</el-button>
        <el-button type="primary" @click="submitForm">确 定</el-button>
      </div>
    </el-dialog>
    
    <!-- 管理供应商对话框 -->
    <el-dialog title="管理供应商" :visible.sync="supplierDialogVisible" width="700px">
      <div class="supplier-header">
        <h3>{{ currentMaterial.name }} 的供应商</h3>
        <el-button type="primary" size="small" @click="showAddSupplierDialog">添加供应商</el-button>
      </div>
      
      <el-table :data="materialSuppliers" border style="width: 100%" v-loading="supplierLoading">
        <el-table-column prop="supplier_name" label="供应商名称" width="180"></el-table-column>
        <el-table-column prop="price" label="采购价格" width="120">
          <template slot-scope="scope">
            {{ scope.row.price ? `¥${scope.row.price}` : '未设置' }}
          </template>
        </el-table-column>
        <el-table-column prop="is_preferred" label="首选供应商" width="120">
          <template slot-scope="scope">
            <el-tag :type="scope.row.is_preferred ? 'success' : 'info'">
              {{ scope.row.is_preferred ? '是' : '否' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template slot-scope="scope">
            <el-button size="mini" @click="editSupplier(scope.row)">编辑</el-button>
            <el-button size="mini" type="danger" @click="removeSupplier(scope.row)">移除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>
    
    <!-- 添加/编辑供应商关联对话框 -->
    <el-dialog :title="supplierFormType === 'add' ? '添加供应商' : '编辑供应商'" :visible.sync="supplierFormVisible" width="500px">
      <el-form :model="supplierForm" :rules="supplierRules" ref="supplierForm" label-width="100px">
        <el-form-item label="供应商" prop="supplier_id" v-if="supplierFormType === 'add'">
          <el-select v-model="supplierForm.supplier_id" placeholder="请选择供应商" filterable style="width: 100%">
            <el-option 
              v-for="item in availableSuppliers" 
              :key="item.id" 
              :label="item.name" 
              :value="item.id">
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="采购价格" prop="price">
          <el-input-number v-model="supplierForm.price" :precision="2" :step="0.1" :min="0" style="width: 100%"></el-input-number>
        </el-form-item>
        <el-form-item label="首选供应商" prop="is_preferred">
          <el-switch v-model="supplierForm.is_preferred"></el-switch>
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="supplierFormVisible = false">取 消</el-button>
        <el-button type="primary" @click="submitSupplierForm">确 定</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
export default {
  name: 'MaterialList',
  data() {
    return {
         isAdmin: JSON.parse(localStorage.getItem('userInfo') || '{}').role === 'admin',
      materials: [],
      loading: false,
      dialogVisible: false,
      dialogType: 'add',
      materialForm: {
        id: null,
        code: '',
        name: '',
        category: '',
        specification: '',
        origin: '',
        description: '',
        status: 'active',
        selectedSuppliers: []
      },
      rules: {
        code: [{ required: true, message: '请输入原材料编码', trigger: 'blur' }],
        name: [{ required: true, message: '请输入原材料名称', trigger: 'blur' }],
        category: [{ required: true, message: '请选择分类', trigger: 'change' }],
        origin: [{ required: true, message: '请输入产地', trigger: 'blur' }]
      },
      searchForm: {
        name: '',
        category: '',
        status: ''
      },
      categoryOptions: ['原料', '包装材料', '添加剂', '其他'],
      pagination: {
        currentPage: 1,
        pageSize: 10,
        total: 0
      },
      supplierDialogVisible: false,
      supplierLoading: false,
      supplierFormVisible: false,
      supplierFormType: 'add',
      supplierForm: {
        supplier_id: null,
        price: 0,
        is_preferred: false
      },
      supplierRules: {
        supplier_id: [{ required: true, message: '请选择供应商', trigger: 'change' }],
        price: [{ required: true, message: '请输入采购价格', trigger: 'change' }]
      },
      currentMaterial: {},
      materialSuppliers: [],
      availableSuppliers: [],
      allSuppliers: []
    }
  },
  created() {
    this.checkServerConnection();
  },
  methods: {
    async checkServerConnection() {
      try {
        const response = await this.$axios.get(this.$httpUrl + '/api/health-check/');
        console.log('服务器连接正常:', response.data);
        this.fetchMaterials();
      } catch (error) {
        console.error('服务器连接失败:', error);
        this.$message.error('无法连接到服务器，请确保后端服务正在运行');
      }
    },
    async fetchMaterials() {
      this.loading = true;
      try {
        const params = {
          page: this.pagination.currentPage,
          page_size: this.pagination.pageSize
        };
        
        if (this.searchForm.name) params.name = this.searchForm.name;
        if (this.searchForm.category) params.category = this.searchForm.category;
        if (this.searchForm.status) params.status = this.searchForm.status;
        
        const response = await this.$axios.get(this.$httpUrl + '/api/materials/materials/', { params });
        
        if (response.data.results) {
          this.materials = response.data.results;
          this.pagination.total = response.data.count;
        } else {
          this.materials = response.data;
          this.pagination.total = response.data.length;
        }
        
        for (const material of this.materials) {
          try {
            const supplierResponse = await this.$axios.get(
              this.$httpUrl + `/api/materials/materials/${material.id}/suppliers/`
            );
            material.suppliers = supplierResponse.data;
          } catch (error) {
            console.error(`获取材料ID ${material.id} 的供应商失败:`, error);
            material.suppliers = [];
          }
        }
      } catch (error) {
        this.$message.error('获取原材料列表失败');
        console.error(error);
        this.materials = [];
      } finally {
        this.loading = false;
      }
    },
    showAddDialog() {
      this.dialogType = 'add'
      this.materialForm = {
        id: null,
        code: '',
        name: '',
        category: '',
        specification: '',
        origin: '',
        description: '',
        status: 'active',
        selectedSuppliers: []
      }
      if (this.allSuppliers.length === 0) {
        this.fetchAvailableSuppliers()
      }
      this.dialogVisible = true
    },
    async showEditDialog(row) {
      this.dialogType = 'edit'
      this.materialForm = { ...row, selectedSuppliers: [] }
      
      try {
        const response = await this.$axios.get(this.$httpUrl + `/api/materials/materials/${row.id}/suppliers/`)
        this.materialForm.selectedSuppliers = response.data.map(s => s.supplier_id)
      } catch (error) {
        console.error('获取原材料供应商失败:', error)
      }
      
      this.dialogVisible = true
    },
    submitForm() {
      this.$refs.materialForm.validate(async valid => {
        if (valid) {
          try {
            const formData = { ...this.materialForm }
            const selectedSuppliers = [...(formData.selectedSuppliers || [])]
            delete formData.selectedSuppliers
            delete formData.suppliers
            
            let materialId;
            
            if (this.dialogType === 'edit') {
              await this.$axios.put(this.$httpUrl + `/api/materials/materials/${formData.id}/`, formData)
              materialId = formData.id
              this.$message.success('更新成功')
            } else {
              const response = await this.$axios.post(this.$httpUrl + '/api/materials/materials/', formData)
              materialId = response.data.id
              this.$message.success('添加成功')
            }
            
            if (materialId && selectedSuppliers.length > 0) {
              const existingResponse = await this.$axios.get(this.$httpUrl + `/api/materials/materials/${materialId}/suppliers/`)
              const existingSuppliers = existingResponse.data
              
              const suppliersToRemove = existingSuppliers.filter(s => !selectedSuppliers.includes(s.supplier_id))
              
              const existingSupplierIds = existingSuppliers.map(s => s.supplier_id)
              const suppliersToAdd = selectedSuppliers.filter(id => !existingSupplierIds.includes(id))
              
              for (const supplier of suppliersToRemove) {
                await this.$axios.delete(this.$httpUrl + `/api/materials/materials/${materialId}/suppliers/${supplier.id}/`)
              }
              
              for (const supplierId of suppliersToAdd) {
                await this.$axios.post(this.$httpUrl + `/api/materials/materials/${materialId}/suppliers/`, {
                  supplier_id: supplierId,
                  price: 0,
                  is_preferred: false
                })
              }
            }
            
            this.dialogVisible = false
            this.fetchMaterials()
          } catch (error) {
            this.$message.error(this.dialogType === 'edit' ? '更新失败' : '添加失败')
            console.error(error)
          }
        }
      })
    },
    viewBatches(material) {
      this.$router.push({
        name: 'MaterialBatches',
        params: { materialId: material.id }
      })
    },
    handleSearch() {
      this.pagination.currentPage = 1;
      this.fetchMaterials();
    },
    resetSearch() {
      this.searchForm = {
        name: '',
        category: '',
        status: ''
      };
      this.pagination.currentPage = 1;
      this.fetchMaterials();
    },
    handleSizeChange(newSize) {
      this.pagination.pageSize = newSize
      this.pagination.currentPage = 1
      this.fetchMaterials()
    },
    handleCurrentChange(newPage) {
      this.pagination.currentPage = newPage
      this.fetchMaterials()
    },
    getSuppliers(material) {
      return material.suppliers || []
    },
    manageSuppliers(material) {
      this.currentMaterial = material
      this.fetchMaterialSuppliers(material.id)
      this.fetchAvailableSuppliers()
      this.supplierDialogVisible = true
    },
    async fetchMaterialSuppliers(materialId) {
      this.supplierLoading = true
      try {
        const response = await this.$axios.get(this.$httpUrl + `/api/materials/materials/${materialId}/suppliers/`)
        this.materialSuppliers = response.data
      } catch (error) {
        this.$message.error('获取原材料供应商失败')
        console.error(error)
      } finally {
        this.supplierLoading = false
      }
    },
    async fetchAvailableSuppliers() {
      try {
        const response = await this.$axios.get(this.$httpUrl + '/api/materials/suppliers/', {
          params: {
            page: 1,
            page_size: 100
          }
        });
        
        const suppliers = response.data.results || response.data;
        const existingIds = this.materialSuppliers.map(s => s.supplier_id);
        this.availableSuppliers = suppliers.filter(s => !existingIds.includes(s.id));
        this.allSuppliers = suppliers;
      } catch (error) {
        this.$message.error('获取供应商列表失败');
        console.error(error);
      }
    },
    showAddSupplierDialog() {
      this.supplierFormType = 'add'
      this.supplierForm = {
        supplier_id: null,
        price: 0,
        is_preferred: false
      }
      this.supplierFormVisible = true
    },
    editSupplier(supplier) {
      this.supplierFormType = 'edit'
      this.supplierForm = {
        id: supplier.id,
        supplier_id: supplier.supplier_id,
        price: supplier.price || 0,
        is_preferred: supplier.is_preferred
      }
      this.supplierFormVisible = true
    },
    removeSupplier(supplier) {
      this.$confirm('确定要移除该供应商吗?', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(async () => {
        try {
          await this.$axios.delete(this.$httpUrl + `/api/materials/materials/${this.currentMaterial.id}/suppliers/${supplier.id}/`)
          this.$message.success('移除成功')
          this.fetchMaterialSuppliers(this.currentMaterial.id)
          this.fetchAvailableSuppliers()
        } catch (error) {
          this.$message.error('移除失败')
          console.error(error)
        }
      }).catch(() => {})
    },
    submitSupplierForm() {
      this.$refs.supplierForm.validate(async valid => {
        if (valid) {
          try {
            // 先检查该供应商是否已关联
            if (this.supplierFormType === 'add') {
              const existingSupplier = this.materialSuppliers.find(
                s => s.supplier_id === this.supplierForm.supplier_id
              );
              
              if (existingSupplier) {
                // 供应商已关联，提示用户并提供更新选项
                this.$confirm('该供应商已关联到此材料，是否要更新关联信息?', '提示', {
                  confirmButtonText: '更新',
                  cancelButtonText: '取消',
                  type: 'warning'
                }).then(async () => {
                  // 更新现有关联
                  await this.$axios.put(
                    this.$httpUrl + `/api/materials/materials/${this.currentMaterial.id}/suppliers/${existingSupplier.id}/`, 
                    {
                      price: this.supplierForm.price,
                      is_preferred: this.supplierForm.is_preferred
                    }
                  );
                  this.$message.success('更新成功');
                  this.supplierFormVisible = false;
                  this.fetchMaterialSuppliers(this.currentMaterial.id);
                  this.fetchAvailableSuppliers();
                }).catch(() => {
                  // 用户取消操作
                });
                return;
              }
            }
            
            // 原有逻辑，处理编辑或新增(没有冲突的情况)
            if (this.supplierFormType === 'edit') {
              await this.$axios.put(
                this.$httpUrl + `/api/materials/materials/${this.currentMaterial.id}/suppliers/${this.supplierForm.id}/`, 
                {
                  price: this.supplierForm.price,
                  is_preferred: this.supplierForm.is_preferred
                }
              );
              this.$message.success('更新成功');
            } else {
              await this.$axios.post(
                this.$httpUrl + `/api/materials/materials/${this.currentMaterial.id}/suppliers/`, 
                {
                  supplier_id: this.supplierForm.supplier_id,
                  price: this.supplierForm.price,
                  is_preferred: this.supplierForm.is_preferred
                }
              );
              this.$message.success('添加成功');
            }
            
            this.supplierFormVisible = false;
            this.fetchMaterialSuppliers(this.currentMaterial.id);
            this.fetchAvailableSuppliers();
          } catch (error) {
            console.error('操作失败:', error.response?.data);
            this.$message.error(error.response?.data?.error || (this.supplierFormType === 'edit' ? '更新失败' : '添加失败'));
          }
        }
      });
    },
    async toggleStatus(row) {
      try {
        const newStatus = row.status === 'active' ? 'inactive' : 'active'
        await this.$axios.patch(this.$httpUrl + `/api/materials/materials/${row.id}/`, { status: newStatus })
        row.status = newStatus
        this.$message.success('状态更新成功')
      } catch (error) {
        this.$message.error('状态更新失败')
        console.error(error)
      }
    },
    async handleDelete(row) {
      try {
        await this.$axios.delete(this.$httpUrl + `/api/materials/materials/${row.id}/`)
        this.$message.success('删除成功')
        this.fetchMaterials()
      } catch (error) {
        this.$message.error('删除失败')
        console.error(error)
      }
    },
    addSupplier() {
      // 先检查该供应商是否已关联
      this.$axios.get(this.$httpUrl + `/api/materials/materials/${this.editedMaterialId}/suppliers/`)
        .then(response => {
          // 检查当前选择的供应商是否已在关联列表中
          const isAlreadyLinked = response.data.some(item => item.supplier === this.supplierForm.supplier_id);
          
          if (isAlreadyLinked) {
            // 供应商已关联，提示用户并提供更新选项
            this.$confirm('该供应商已关联到此材料，是否要更新关联信息?', '提示', {
              confirmButtonText: '更新',
              cancelButtonText: '取消',
              type: 'warning'
            }).then(() => {
              // 更新关联
              this.updateSupplierLink();
            }).catch(() => {
              // 用户取消操作
            });
          } else {
            // 供应商未关联，直接添加新关联
            this.createSupplierLink();
          }
        })
        .catch(err => {
          console.error('获取关联失败:', err);
          this.$message.error('获取供应商关联失败');
        });
    },
    // 创建新关联
    createSupplierLink() {
      this.$axios.post(this.$httpUrl + `/api/materials/materials/${this.editedMaterialId}/suppliers/`, this.supplierForm)
        .then(() => {
          this.$message.success('添加供应商关联成功');
          this.supplierDialog = false;
          // 刷新供应商列表
          this.getSuppliers(this.editedMaterialId);
        })
        .catch(err => {
          console.error('添加失败:', err.response?.data);
          this.$message.error(err.response?.data?.error || '添加供应商关联失败');
        });
    },
    // 更新已有关联
    updateSupplierLink() {
      // 查找关联ID
      this.$axios.get(this.$httpUrl + `/api/materials/materials/${this.editedMaterialId}/suppliers/`)
        .then(response => {
          const existingLink = response.data.find(item => item.supplier === this.supplierForm.supplier_id);
          if (existingLink) {
            // 使用PUT请求更新现有关联
            this.$axios.put(
              this.$httpUrl + `/api/materials/materials/${this.editedMaterialId}/suppliers/${existingLink.id}/`, 
              this.supplierForm
            )
            .then(() => {
              this.$message.success('更新供应商关联成功');
              this.supplierDialog = false;
              // 刷新供应商列表
              this.getSuppliers(this.editedMaterialId);
            })
            .catch(err => {
              console.error('更新失败:', err.response?.data);
              this.$message.error(err.response?.data?.error || '更新供应商关联失败');
            });
          }
        })
        .catch(err => {
          console.error('获取关联ID失败:', err);
          this.$message.error('更新供应商关联失败');
        });
    }
  }
}
</script>

<style scoped>
.material-container {
  padding: var(--spacing-xl);
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

.supplier-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.supplier-header h3 {
  margin: 0;
  font-size: 18px;
}

.no-data {
  color: var(--text-secondary);
  font-style: italic;
}
</style> 