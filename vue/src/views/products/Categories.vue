<template>
  <div class="categories-container">
    <div class="page-header">
      <h2>商品分类管理</h2>
      <el-button type="primary" @click="handleAdd">添加分类</el-button>
    </div>
    
    <el-table :data="categories" border style="width: 100%">
      <el-table-column prop="name" label="分类名称"></el-table-column>
      <el-table-column prop="code" label="分类编码"></el-table-column>
      <el-table-column prop="level" label="层级"></el-table-column>
      <el-table-column prop="sort_order" label="排序"></el-table-column>
      <el-table-column prop="is_active" label="状态">
        <template slot-scope="scope">
          <el-tag :type="scope.row.is_active ? 'success' : 'danger'">
            {{ scope.row.is_active ? '启用' : '禁用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200">
        <template slot-scope="scope">
          <el-button size="mini" @click="handleEdit(scope.row)">编辑</el-button>
          <el-button size="mini" type="danger" @click="handleDelete(scope.row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 添加/编辑对话框 -->
    <el-dialog :title="dialogTitle" :visible.sync="dialogVisible">
      <el-form :model="form" :rules="rules" ref="form" label-width="100px">
        <el-form-item label="分类名称" prop="name">
          <el-input v-model="form.name"></el-input>
        </el-form-item>
        <el-form-item label="分类编码" prop="code">
          <el-input v-model="form.code"></el-input>
        </el-form-item>
        <el-form-item label="父级分类">
          <el-select v-model="form.parent" clearable placeholder="请选择">
            <el-option
              v-for="item in categories"
              :key="item.id"
              :label="item.name"
              :value="item.id">
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="排序">
          <el-input-number v-model="form.sort_order" :min="0"></el-input-number>
        </el-form-item>
        <el-form-item label="状态">
          <el-switch v-model="form.is_active"></el-switch>
        </el-form-item>
      </el-form>
      <div slot="footer">
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
export default {
  name: 'ProductCategories',
  data() {
    return {
      categories: [],
      dialogVisible: false,
      dialogTitle: '添加分类',
      form: {
        name: '',
        code: '',
        parent: null,
        sort_order: 0,
        is_active: true
      },
      rules: {
        name: [
          { required: true, message: '请输入分类名称', trigger: 'blur' }
        ],
        code: [
          { required: true, message: '请输入分类编码', trigger: 'blur' }
        ]
      }
    }
  },
  created() {
    this.fetchData()
  },
  methods: {
    fetchData() {
      this.$axios.get(this.$httpUrl + '/api/products/categories/')
        .then(res => {
          this.categories = res.data
        })
        .catch(err => {
          this.$message.error('获取分类列表失败')
          console.error(err)
        })
    },
    handleAdd() {
      this.dialogTitle = '添加分类'
      this.form = {
        name: '',
        code: '',
        parent: null,
        sort_order: 0,
        is_active: true
      }
      this.dialogVisible = true
    },
    handleEdit(row) {
      this.dialogTitle = '编辑分类'
      this.form = { ...row }
      this.dialogVisible = true
    },
    handleDelete(row) {
      this.$confirm('确认删除该分类?', '提示', {
        type: 'warning'
      }).then(() => {
        this.$axios.delete(this.$httpUrl + `/api/products/categories/${row.id}/`)
          .then(() => {
            this.$message.success('删除成功')
            this.fetchData()
          })
          .catch(err => {
            this.$message.error('删除失败')
            console.error(err)
          })
      })
    },
    handleSubmit() {
      this.$refs.form.validate(valid => {
        if (valid) {
          const method = this.form.id ? 'put' : 'post'
          const url = this.form.id 
            ? `/api/products/categories/${this.form.id}/`
            : '/api/products/categories/'
          
          this.$axios[method](this.$httpUrl + url, this.form)
            .then(() => {
              this.$message.success(this.form.id ? '更新成功' : '添加成功')
              this.dialogVisible = false
              this.fetchData()
            })
            .catch(err => {
              this.$message.error(this.form.id ? '更新失败' : '添加失败')
              console.error(err)
            })
        }
      })
    }
  }
}
</script>

<style scoped>
.categories-container {
  padding: 20px;
}
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
</style> 