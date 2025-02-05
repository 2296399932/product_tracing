<template>
  <div class="batches-container">
    <div class="page-header">
      <h2>批次管理</h2>
      <el-button type="primary" @click="handleAdd">新增批次</el-button>
    </div>

    <!-- 搜索栏 -->
    <el-form :inline="true" :model="searchForm" class="search-form">
      <el-form-item label="批次号">
        <el-input v-model="searchForm.batch_number" placeholder="请输入批次号"></el-input>
      </el-form-item>
      <el-form-item label="商品">
        <el-select v-model="searchForm.product" placeholder="请选择商品">
          <el-option
            v-for="item in products"
            :key="item.id"
            :label="item.name"
            :value="item.id">
          </el-option>
        </el-select>
      </el-form-item>
      <el-form-item label="生产日期">
        <el-date-picker
          v-model="searchForm.date_range"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期">
        </el-date-picker>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="handleSearch">查询</el-button>
        <el-button @click="resetSearch">重置</el-button>
      </el-form-item>
    </el-form>

    <!-- 批次列表 -->
    <el-table :data="batches" border style="width: 100%">
      <el-table-column prop="batch_number" label="批次号" width="180"></el-table-column>
      <el-table-column prop="product_name" label="商品名称"></el-table-column>
      <el-table-column prop="production_date" label="生产日期" width="120">
        <template slot-scope="scope">
          {{ scope.row.production_date | formatDate }}
        </template>
      </el-table-column>
      <el-table-column prop="expiry_date" label="有效期" width="120">
        <template slot-scope="scope">
          {{ scope.row.expiry_date | formatDate }}
        </template>
      </el-table-column>
      <el-table-column prop="quantity" label="数量" width="100"></el-table-column>
      <el-table-column prop="cost_price" label="成本价" width="100">
        <template slot-scope="scope">
          ¥{{ scope.row.cost_price }}
        </template>
      </el-table-column>
      <el-table-column prop="status" label="状态">
        <template #default="scope">
          <el-tag :type="getBatchStatusType(scope.row.status)">
            {{ getBatchStatusText(scope.row.status) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="250">
        <template slot-scope="scope">
          <el-button size="mini" @click="handleEdit(scope.row)">编辑</el-button>
          <el-button size="mini" type="success" @click="handleViewQR(scope.row)">查看二维码</el-button>

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
        <el-form-item label="商品" prop="product">
          <el-select v-model="form.product" placeholder="请选择商品">
            <el-option
              v-for="item in products"
              :key="item.id"
              :label="item.name"
              :value="item.id">
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="批次号" prop="batch_number">
          <el-input v-model="form.batch_number"></el-input>
        </el-form-item>
        <el-form-item label="生产日期" prop="production_date">
          <el-date-picker
            v-model="form.production_date"
            type="date"
            placeholder="选择日期">
          </el-date-picker>
        </el-form-item>
        <el-form-item label="有效期" prop="expiry_date">
          <el-date-picker
            v-model="form.expiry_date"
            type="date"
            placeholder="选择日期">
          </el-date-picker>
        </el-form-item>
        <el-form-item label="数量" prop="quantity">
          <el-input-number v-model="form.quantity" :min="0"></el-input-number>
        </el-form-item>
        <el-form-item label="成本价" prop="cost_price">
          <el-input-number v-model="form.cost_price" :precision="2" :step="0.1" :min="0"></el-input-number>
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-select v-model="form.status" placeholder="请选择状态">
            <el-option
              v-for="item in statusOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value">
            </el-option>
          </el-select>
        </el-form-item>
      </el-form>
      <div slot="footer">
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </div>
    </el-dialog>

    <!-- 二维码对话框 -->
    <el-dialog title="批次二维码" :visible.sync="qrDialogVisible" width="30%">
      <div class="qr-container">
        <img :src="currentQRCode" v-if="currentQRCode" />
        <div v-else>暂无二维码</div>
      </div>
      <div slot="footer">
        <el-button @click="qrDialogVisible = false">关闭</el-button>
        <el-button type="primary" @click="handleDownloadQR">下载</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
export default {
  name: 'BatchList',
  filters: {
    formatDate(value) {
      if (!value) return ''
      return new Date(value).toLocaleDateString()
    }
  },
  data() {
    return {
      searchForm: {
        batch_number: '',
        product: '',
        date_range: []
      },
      batches: [],
      products: [],
      page: 1,
      pageSize: 10,
      total: 0,
      dialogVisible: false,
      qrDialogVisible: false,
      dialogTitle: '新增批次',
      currentQRCode: '',
      form: {
        product: '',
        batch_number: '',
        production_date: '',
        expiry_date: '',
        quantity: 0,
        cost_price: 0,
        status: 'active'
      },
      rules: {
        product: [{ required: true, message: '请选择商品', trigger: 'change' }],
        batch_number: [{ required: true, message: '请输入批次号', trigger: 'blur' }],
        production_date: [{ required: true, message: '请选择生产日期', trigger: 'change' }],
        expiry_date: [{ required: true, message: '请选择有效期', trigger: 'change' }],
        quantity: [{ required: true, message: '请输入数量', trigger: 'blur' }],
        cost_price: [{ required: true, message: '请输入成本价', trigger: 'blur' }]
      },
      statusOptions: [
        { value: 'active', label: '正常' },
        { value: 'sold_out', label: '售罄' },
        { value: 'expired', label: '过期' },
        { value: 'disabled', label: '停用' }
      ]
    }
  },
  created() {
    this.fetchProducts()
    this.fetchBatches()
  },
  methods: {
    getBatchStatusType(status) {
      const types = {
        'active': 'success',    // 正常 - 绿色
        'sold_out': 'info',     // 售罄 - 灰色
        'expired': 'warning',   // 过期 - 黄色
        'disabled': 'danger'    // 停用 - 红色
      }
      return types[status] || ''
    },
    getBatchStatusText(status) {
      const texts = {
        'active': '正常',
        'sold_out': '售罄',
        'expired': '过期',
        'disabled': '停用'
      }
      return texts[status] || status
    },
    fetchProducts() {
      this.$axios.get(this.$httpUrl + '/api/products/list/')
        .then(res => {
          this.products = res.data.results
          console.log('Products loaded:', this.products)
        })
        .catch(err => {
          this.$message.error('获取商品列表失败')
          console.error(err)
        })
    },
    fetchBatches() {
      const params = {
        page: this.page,
        page_size: this.pageSize,
        batch_number: this.searchForm.batch_number,
        product: this.searchForm.product,
        production_date_from: this.searchForm.date_range?.[0],
        production_date_to: this.searchForm.date_range?.[1]
      }
      this.$axios.get(this.$httpUrl + '/api/products/batches/', { params })
        .then(res => {
          this.batches = res.data.results
          this.total = res.data.count
        })
        .catch(err => {
          this.$message.error('获取批次列表失败')
          console.error(err)
        })
    },
    handleSearch() {
      this.page = 1
      this.fetchBatches()
    },
    resetSearch() {
      this.searchForm = {
        batch_number: '',
        product: '',
        date_range: []
      }
      this.handleSearch()
    },
    handleSizeChange(val) {
      this.pageSize = val
      this.fetchBatches()
    },
    handleCurrentChange(val) {
      this.page = val
      this.fetchBatches()
    },
    handleAdd() {
      this.dialogTitle = '新增批次'
      this.form = {
        product: '',
        batch_number: '',
        production_date: '',
        expiry_date: '',
        quantity: 0,
        cost_price: 0,
        status: 'active'
      }
      this.dialogVisible = true
    },
    handleEdit(row) {
      this.form = { ...row }
      if (!['active', 'sold_out', 'expired', 'disabled'].includes(this.form.status)) {
        this.form.status = 'active'
      }
      this.dialogVisible = true
      this.dialogTitle = '编辑批次'
    },
    handleViewQR(row) {
      this.$axios.get(this.$httpUrl + `/api/products/qrcode/${row.batch_number}/`)
        .then(res => {
          this.currentQRCode = res.data.qrcode_url
          this.qrDialogVisible = true
        })
        .catch(err => {
          this.$message.error('获取二维码失败')
          console.error(err)
        })
    },
    handleTrace(row) {
      // 跳转到追溯页面
      this.$router.push(`/trace/${row.batch_number}`)
    },
    handleDownloadQR() {
      // 下载二维码图片
      if (this.currentQRCode) {
        const link = document.createElement('a')
        link.href = this.currentQRCode
        link.download = 'qrcode.png'
        link.click()
      }
    },
    handleSubmit() {
      this.$refs.form.validate(valid => {
        if (valid) {
          // 格式化日期
          const formData = {
            ...this.form,
            production_date: this.formatDate(this.form.production_date),
            expiry_date: this.formatDate(this.form.expiry_date)
          };
          
          const method = this.form.id ? 'put' : 'post';
          const url = this.form.id 
            ? `/api/products/batches/${this.form.id}/`
            : '/api/products/batches/';
          
          this.$axios[method](this.$httpUrl + url, formData)
            .then(() => {
              this.$message.success(this.form.id ? '更新成功' : '添加成功');
              this.dialogVisible = false;
              this.fetchBatches();
            })
            .catch(err => {
              console.error('Error:', err.response?.data || err);
              this.$message.error(err.response?.data?.error || (this.form.id ? '更新失败' : '添加失败'));
            });
        }
      });
    },
    formatDate(date) {
      if (!date) return null;
      if (typeof date === 'string') return date;
      return date.toISOString().split('T')[0];
    }
  }
}
</script>

<style scoped>
.batches-container {
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
.qr-container {
  text-align: center;
}
.qr-container img {
  max-width: 200px;
}
</style> 