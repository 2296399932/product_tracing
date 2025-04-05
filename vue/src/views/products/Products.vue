<template>
  <div class="products-container">
    <div class="page-header">
      <h2>商品列表</h2>
      <div>
        <el-button type="primary" @click="handleAddCategory" style="margin-right: 10px">添加分类</el-button>
        <el-button type="primary" @click="handleAdd" v-if="!isAdmin">添加商品</el-button>
      </div>
    </div>

    <!-- 搜索栏 -->
    <el-form :inline="true" :model="searchForm" class="search-form">
      <el-form-item label="商品名称">
        <el-input v-model="searchForm.name" placeholder="请输入商品名称"></el-input>
      </el-form-item>
      <el-form-item label="商品分类">
        <el-select v-model="searchForm.category" placeholder="请选择分类">
          <el-option
            v-for="item in categories"
            :key="item.id"
            :label="item.name"
            :value="item.id">
          </el-option>
        </el-select>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="handleSearch">查询</el-button>
        <el-button @click="resetSearch">重置</el-button>
      </el-form-item>
    </el-form>

    <!-- 商品列表 -->
    <el-table :data="products" border style="width: 100%">
      <el-table-column prop="code" label="商品编码" width="120"></el-table-column>
      <el-table-column label="商品图片" width="100">
        <template slot-scope="scope">
          <el-image 
            style="width: 50px; height: 50px"
            :src="scope.row.image || defaultImage"
            :preview-src-list="scope.row.image ? [scope.row.image] : []"
            fit="cover">
            <div slot="error" class="image-slot">
              <i class="el-icon-picture-outline"></i>
            </div>
          </el-image>
        </template>
      </el-table-column>
      <el-table-column prop="name" label="商品名称"></el-table-column>
      <el-table-column prop="category_name" label="商品分类"></el-table-column>
      <el-table-column prop="price" label="价格" width="100">
        <template slot-scope="scope">
          ¥{{ scope.row.price }}
        </template>
      </el-table-column>
      <el-table-column prop="unit" label="单位" width="80"></el-table-column>
      <el-table-column label="规格参数" width="150">
        <template slot-scope="scope">
          <el-popover
            placement="top-start"
            width="300"
            trigger="hover">
            <div v-html="formatSpecifications(scope.row.specifications)"></div>
            <el-button slot="reference" type="text">查看规格</el-button>
          </el-popover>
        </template>
      </el-table-column>
      <el-table-column label="商品描述" width="150">
        <template slot-scope="scope">
          <el-tooltip :content="scope.row.description" placement="top" effect="light" :disabled="!scope.row.description">
            <span>{{ scope.row.description ? scope.row.description.substring(0, 20) + (scope.row.description.length > 20 ? '...' : '') : '无' }}</span>
          </el-tooltip>
        </template>
      </el-table-column>
      <el-table-column prop="stock" label="库存" width="100">
        <template slot-scope="scope">
          {{ scope.row.stock || 0 }}
        </template>
      </el-table-column>
      <el-table-column prop="status" label="状态" width="100">
        <template slot-scope="scope">
          <el-tag :type="scope.row.status ? 'success' : 'danger'">
            {{ scope.row.status ? '上架' : '下架' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200">
        <template slot-scope="scope">
          <el-button size="mini" @click="handleEdit(scope.row)" v-if="!isAdmin">编辑</el-button>
          <el-button size="mini" type="danger" @click="handleDelete(scope.row)" v-if="!isAdmin">删除</el-button>
          <el-button size="mini" @click="handleView(scope.row)" v-if="isAdmin">查看</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <div class="pagination-container">
      <el-pagination
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
        :current-page="page"
        :page-sizes="[10, 20, 50, 100]"
        :page-size="pageSize"
        layout="total, sizes, prev, pager, next, jumper"
        :total="total">
      </el-pagination>
    </div>

    <!-- 添加/编辑对话框 -->
    <el-dialog :title="dialogTitle" :visible.sync="dialogVisible" width="50%">
      <el-form :model="form" :rules="rules" ref="form" label-width="100px">
        <el-form-item label="商品名称" prop="name">
          <el-input v-model="form.name"></el-input>
        </el-form-item>
        <el-form-item label="商品编码" prop="code">
          <el-input v-model="form.code"></el-input>
        </el-form-item>
        <el-form-item label="商品分类" prop="category">
          <el-select v-model="form.category" placeholder="请选择分类">
            <el-option
              v-for="item in categories"
              :key="item.id"
              :label="item.name"
              :value="item.id">
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="商品图片">
          <el-upload
            class="avatar-uploader"
            :action="uploadUrl"
            :headers="uploadHeaders"
            :show-file-list="false"
            :on-success="handleImageSuccess"
            :before-upload="beforeImageUpload">
            <img v-if="form.image" :src="form.image" class="avatar">
            <i v-else class="el-icon-plus avatar-uploader-icon"></i>
          </el-upload>
          <div class="image-tip">建议上传尺寸: 300x300px, 大小不超过2MB</div>
        </el-form-item>
        <el-form-item label="价格" prop="price">
          <el-input-number v-model="form.price" :precision="2" :step="0.1" :min="0"></el-input-number>
        </el-form-item>
        <el-form-item label="单位" prop="unit">
          <el-input v-model="form.unit"></el-input>
        </el-form-item>
        <el-form-item label="规格参数">
          <el-input type="textarea" v-model="form.specifications"></el-input>
        </el-form-item>
        <el-form-item label="商品描述">
          <el-input type="textarea" v-model="form.description"></el-input>
        </el-form-item>
        <el-form-item label="状态">
          <el-switch v-model="form.status"></el-switch>
        </el-form-item>
      </el-form>
      <div slot="footer">
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </div>
    </el-dialog>

    <!-- 分类管理对话框 -->
    <el-dialog title="添加分类" :visible.sync="categoryDialogVisible" width="30%">
      <el-form :model="categoryForm" :rules="categoryRules" ref="categoryForm" label-width="80px">
        <el-form-item label="分类名称" prop="name">
          <el-input v-model="categoryForm.name"></el-input>
        </el-form-item>
        <el-form-item label="分类编码" prop="code">
          <el-input v-model="categoryForm.code"></el-input>
        </el-form-item>
      </el-form>
      <div slot="footer">
        <el-button @click="categoryDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitCategory">确定</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
export default {
  name: 'ProductList',
  data() {
    return {

      searchForm: {
        name: '',
        category: ''
      },
      products: [],
      categories: [],
      page: 1,
      pageSize: 10,
      total: 0,
      dialogVisible: false,
      dialogTitle: '添加商品',

      form: {
        name: '',
        code: '',
        category: '',
        price: 0,
        unit: '',
        specifications: '',
        description: '',
        status: true,
        image: ''
      },
      rules: {
        name: [{ required: true, message: '请输入商品名称', trigger: 'blur' }],
        code: [{ required: true, message: '请输入商品编码', trigger: 'blur' }],
        category: [{ required: true, message: '请选择商品分类', trigger: 'change' }],
        price: [{ required: true, message: '请输入价格', trigger: 'blur' }],
        unit: [{ required: true, message: '请输入原材料', trigger: 'blur' }]
      },
      categoryDialogVisible: false,
      categoryForm: {
        name: '',
        code: '',
        level: 1,
        sort_order: 0
      },
      categoryRules: {
        name: [
          { required: true, message: '请输入分类名称', trigger: 'blur' }
        ],
        code: [
          { required: true, message: '请输入分类编码', trigger: 'blur' }
        ]
      },
      defaultImage: require('@/assets/img/bo.jpg'),
      uploadUrl: this.$httpUrl + '/api/products/upload-image/',
      uploadHeaders: {
        Authorization: 'Bearer ' + localStorage.getItem('token')
      },
      isAdmin: JSON.parse(localStorage.getItem('userInfo') || '{}').role === 'admin'
    }
  },
  created() {
    this.fetchCategories()
    this.fetchProducts()
  },
  methods: {
    fetchCategories() {
      this.$axios.get(this.$httpUrl + '/api/products/categories/')
        .then(res => {
          this.categories = res.data
          console.log( this.categories )
        })
        .catch(err => {
          this.$message.error('获取分类列表失败')
          console.error(err)
        })
    },
    fetchProducts() {
      const params = {
        page: this.page,
        page_size: this.pageSize,
        name: this.searchForm.name,
        category: this.searchForm.category
      }
      this.$axios.get(this.$httpUrl + '/api/products/list/', { params })
        .then(res => {
          this.products = res.data.results
          console.log('Products details:', this.products.map(p => ({
            id: p.id,
            name: p.name,
            stock: p.stock,
            batches: p.batches,
            image: p.image
          })))
          this.total = res.data.count
        })
        .catch(err => {
          this.$message.error('获取商品列表失败')
          console.error(err)
        })
    },
    handleSearch() {
      this.page = 1
      this.fetchProducts()
    },
    resetSearch() {
      this.searchForm = {
        name: '',
        category: ''
      }
      this.handleSearch()
    },
    handleSizeChange(val) {
      this.pageSize = val
      this.fetchProducts()
    },
    handleCurrentChange(val) {
      this.page = val
      this.fetchProducts()
    },
    handleAdd() {
      this.dialogTitle = '添加商品'
      this.form = {
        name: '',
        code: '',
        category: '',
        price: 0,
        unit: '',
        specifications: '',
        description: '',
        status: true,
        image: ''
      }
      this.dialogVisible = true
    },
    handleEdit(row) {
      this.dialogTitle = '编辑商品'
      this.form = {
        ...row,
        status: row.status === 'active',
        specifications: row.specifications || {},
        category: row.category?.id || row.category
      }
      this.dialogVisible = true
    },
    handleDelete(row) {
      this.$confirm('确认删除该商品?', '提示', {
        type: 'warning'
      }).then(() => {
        this.$axios.delete(this.$httpUrl + `/api/products/${row.id}/`)
          .then(() => {
            this.$message.success('删除成功')
            this.fetchProducts()
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
            ? `/api/products/${this.form.id}/`
            : '/api/products/list/'
          
          // 创建 FormData 对象来处理文件上传
          const formData = new FormData()
          
          // 处理规格字段
          let specifications = this.form.specifications
          if (typeof specifications === 'string') {
            try {
              specifications = JSON.parse(specifications)
            } catch (e) {
              specifications = { description: specifications }
            }
          } else if (!specifications) {
            specifications = {}
          }
          
          // 添加所有字段到 FormData
          formData.append('name', this.form.name)
          formData.append('code', this.form.code)
          formData.append('category', this.form.category)
          formData.append('price', this.form.price)
          formData.append('unit', this.form.unit)
          formData.append('specifications', JSON.stringify(specifications))
          formData.append('description', this.form.description || '')
          formData.append('status', this.form.status ? 'active' : 'inactive')
          
          // 如果有新的图片文件，添加到 FormData
          if (this.form.imageFile) {
            formData.append('image', this.form.imageFile)
          }
          
          // 设置请求配置
          const config = {
            headers: {
              'Content-Type': 'multipart/form-data'
            }
          }
          
          console.log('Submitting form data:', {
            name: this.form.name,
            code: this.form.code,
            category: this.form.category,
            specifications: specifications,
            image: this.form.imageFile ? 'File present' : 'No file'
          })
          
          this.$axios[method](this.$httpUrl + url, formData, config)
            .then(response => {
              console.log('Submit response:', response)
              this.$message.success(this.form.id ? '更新成功' : '添加成功')
              this.dialogVisible = false
              this.fetchProducts()
            })
            .catch(err => {
              console.error('Submit error:', err.response?.data || err)
              this.$message.error(err.response?.data?.error || (this.form.id ? '更新失败' : '添加失败'))
            })
        }
      })
    },
    handleAddCategory() {
      this.categoryForm = {
        name: '',
        code: '',
        level: 1,
        sort_order: 0
      }
      this.categoryDialogVisible = true
    },
    submitCategory() {
      this.$refs.categoryForm.validate(valid => {
        if (valid) {
          this.$axios.post(this.$httpUrl + '/api/products/categories/', this.categoryForm)
            .then(() => {
              this.$message.success('添加分类成功')
              this.categoryDialogVisible = false
              this.fetchCategories()
            })
            .catch(err => {
              this.$message.error('添加分类失败')
              console.error(err)
            })
        }
      })
    },
    // 图片上传相关方法
    handleImageSuccess(res, file) {
      if (res.image_url) {
        this.form.image = res.image_url
        this.form.imageFile = file.raw  // 保存文件对象以供后续提交
        this.$message.success('图片上传成功')
      } else {
        this.$message.error('图片上传失败')
      }
    },
    beforeImageUpload(file) {
      const isJPG = file.type === 'image/jpeg' || file.type === 'image/png'
      const isLt2M = file.size / 1024 / 1024 < 2

      if (!isJPG) {
        this.$message.error('上传图片只能是 JPG 或 PNG 格式!')
      }
      if (!isLt2M) {
        this.$message.error('上传图片大小不能超过 2MB!')
      }
      
      if (isJPG && isLt2M) {
        // 保存文件对象
        this.form.imageFile = file
        return true
      }
      return false
    },
    formatSpecifications(specifications) {
      if (typeof specifications === 'string') {
        return specifications.replace(/\n/g, '<br>')
      } else if (typeof specifications === 'object') {
        return Object.entries(specifications).map(([key, value]) => {
          return `<strong>${key}:</strong> ${value}`
        }).join('<br>')
      }
      return '无'
    }
  }
}
</script>

<style scoped>
.products-container {
  padding: 20px;
}
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
.search-form {
  margin-bottom: 20px;
}
.pagination-container {
  margin-top: 20px;
  text-align: right;
}
.avatar-uploader .el-upload {
  border: 1px dashed #d9d9d9;
  border-radius: 6px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
}
.avatar-uploader .el-upload:hover {
  border-color: #409EFF;
}
.avatar-uploader-icon {
  font-size: 28px;
  color: #8c939d;
  width: 100px;
  height: 100px;
  line-height: 100px;
  text-align: center;
}
.avatar {
  width: 100px;
  height: 100px;
  display: block;
  object-fit: cover;
}
.image-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
}
.image-slot {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  height: 100%;
  background: #f5f7fa;
}
</style> 