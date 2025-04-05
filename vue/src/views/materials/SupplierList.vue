<template>
  <div class="supplier-container">
    <div class="page-header">
      <h2 class="page-title">供应商管理</h2>
      <el-button  v-if="!isAdmin" type="primary" @click="showAddDialog">添加供应商</el-button>
    </div>
    
    <!-- 搜索栏 -->
    <el-form :inline="true" :model="searchForm" class="search-form">
      <el-form-item label="供应商名称">
        <el-input v-model="searchForm.name" placeholder="请输入名称" clearable></el-input>
      </el-form-item>
      <el-form-item label="联系人">
        <el-input v-model="searchForm.contact_person" placeholder="请输入联系人" clearable></el-input>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="handleSearch">搜索</el-button>
        <el-button @click="resetSearch">重置</el-button>
      </el-form-item>
    </el-form>
    
    <!-- 供应商表格 -->
    <el-table :data="suppliers" border style="width: 100%" v-loading="loading">
      <el-table-column prop="name" label="供应商名称" width="180"></el-table-column>
      <el-table-column prop="contact_person" label="联系人" width="120"></el-table-column>
      <el-table-column prop="phone" label="联系电话" width="150"></el-table-column>
      <el-table-column prop="email" label="邮箱"></el-table-column>
      <el-table-column prop="address" label="地址"></el-table-column>
      <el-table-column label="操作" width="180">
        <template slot-scope="scope">
          <el-button v-if="!isAdmin" size="mini" @click="showEditDialog(scope.row)">编辑</el-button>
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
    
    <!-- 添加/编辑供应商对话框 -->
    <el-dialog :title="dialogType === 'add' ? '添加供应商' : '编辑供应商'" :visible.sync="dialogVisible" width="600px">
      <el-form :model="supplierForm" :rules="rules" ref="supplierForm" label-width="100px">
        <el-form-item label="名称" prop="name">
          <el-input v-model="supplierForm.name" placeholder="请输入供应商名称"></el-input>
        </el-form-item>
        <el-form-item label="联系人" prop="contact_person">
          <el-input v-model="supplierForm.contact_person" placeholder="请输入联系人姓名"></el-input>
        </el-form-item>
        <el-form-item label="联系电话" prop="phone">
          <el-input v-model="supplierForm.phone" placeholder="请输入联系电话"></el-input>
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="supplierForm.email" placeholder="请输入邮箱"></el-input>
        </el-form-item>
        <el-form-item label="地址" prop="address">
          <el-input v-model="supplierForm.address" placeholder="请输入地址"></el-input>
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
  name: 'SupplierList',
  data() {
    return {
      suppliers: [],
      loading: false,
      dialogVisible: false,
      dialogType: 'add',
         isAdmin: JSON.parse(localStorage.getItem('userInfo') || '{}').role === 'admin',
      supplierForm: {
        id: null,
        name: '',
        contact_person: '',
        phone: '',
        email: '',
        address: ''
      },
      rules: {
        name: [{ required: true, message: '请输入供应商名称', trigger: 'blur' }],
        contact_person: [{ required: true, message: '请输入联系人', trigger: 'blur' }],
        phone: [{ required: true, message: '请输入联系电话', trigger: 'blur' }]
      },
      searchForm: {
        name: '',
        contact_person: ''
      },
      pagination: {
        currentPage: 1,
        pageSize: 10,
        total: 0
      }
    }
  },
  created() {
    this.fetchSuppliers()
  },
  methods: {
    async fetchSuppliers() {
      this.loading = true
      try {
        const response = await this.$axios.get(this.$httpUrl + '/api/materials/suppliers/', {
          params: {
            page: this.pagination.currentPage,
            page_size: this.pagination.pageSize,
            ...this.searchForm
          }
        })
        this.suppliers = response.data.results || response.data
        this.pagination.total = response.data.count || this.suppliers.length
      } catch (error) {
        this.$message.error('获取供应商列表失败')
        console.error(error)
      } finally {
        this.loading = false
      }
    },
    showAddDialog() {
      this.dialogType = 'add'
      this.supplierForm = {
        id: null,
        name: '',
        contact_person: '',
        phone: '',
        email: '',
        address: ''
      }
      this.dialogVisible = true
    },
    showEditDialog(row) {
      this.dialogType = 'edit'
      this.supplierForm = { ...row }
      this.dialogVisible = true
    },
    submitForm() {
      this.$refs.supplierForm.validate(async valid => {
        if (valid) {
          try {
            if (this.dialogType === 'edit') {
              await this.$axios.put(this.$httpUrl + `/api/materials/suppliers/${this.supplierForm.id}/`, this.supplierForm)
              this.$message.success('更新成功')
            } else {
              await this.$axios.post(this.$httpUrl + '/api/materials/suppliers/', this.supplierForm)
              this.$message.success('添加成功')
            }
            this.dialogVisible = false
            this.fetchSuppliers()
          } catch (error) {
            this.$message.error(this.dialogType === 'edit' ? '更新失败' : '添加失败')
            console.error(error)
          }
        }
      })
    },
    handleDelete(row) {
      this.$confirm('此操作将永久删除该供应商, 是否继续?', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(async () => {
        try {
          await this.$axios.delete(this.$httpUrl + `/api/materials/suppliers/${row.id}/`)
          this.$message.success('删除成功')
          this.fetchSuppliers()
        } catch (error) {
          this.$message.error('删除失败')
          console.error(error)
        }
      }).catch(() => {
        this.$message.info('已取消删除')
      })
    },
    handleSearch() {
      this.pagination.currentPage = 1
      this.fetchSuppliers()
    },
    resetSearch() {
      this.searchForm = {
        name: '',
        contact_person: ''
      }
      this.pagination.currentPage = 1
      this.fetchSuppliers()
    },
    handleSizeChange(newSize) {
      this.pagination.pageSize = newSize
      this.pagination.currentPage = 1
      this.fetchSuppliers()
    },
    handleCurrentChange(newPage) {
      this.pagination.currentPage = newPage
      this.fetchSuppliers()
    }
  }
}
</script>

<style scoped>
.supplier-container {
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
</style> 