<template>
  <div class="sales-container">
    <div class="page-header">
      <h2>销售记录管理</h2>
      <el-button type="primary" @click="handleAdd">添加销售记录</el-button>
    </div>

    <!-- 搜索栏 -->
    <el-form :inline="true" :model="searchForm" class="search-form">
      <el-form-item label="批次号">
        <el-select v-model="searchForm.batch" placeholder="请选择批次" filterable>
          <el-option
            v-for="item in batches"
            :key="item.id"
            :label="item.batch_number"
            :value="item.id">
          </el-option>
        </el-select>
      </el-form-item>
      <el-form-item label="销售日期">
        <el-date-picker
          v-model="searchForm.date_range"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期">
        </el-date-picker>
      </el-form-item>
      <el-form-item label="客户">
        <el-input v-model="searchForm.customer" placeholder="请输入客户名称"></el-input>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="handleSearch">查询</el-button>
        <el-button @click="resetSearch">重置</el-button>
      </el-form-item>
    </el-form>

    <!-- 销售记录列表 -->
    <el-table :data="records" border style="width: 100%" v-loading="loading">
      <el-table-column label="批次号" width="180">
        <template slot-scope="scope">
          {{ scope.row.batch_number || '-' }}
        </template>
      </el-table-column>
      <el-table-column label="商品名称" width="150">
        <template slot-scope="scope">
          {{ scope.row.batch_details?.product?.name || '-' }}
        </template>
      </el-table-column>
      <el-table-column label="商品分类" width="120">
        <template slot-scope="scope">
          {{ scope.row.batch_details?.product?.category_name || '-' }}
        </template>
      </el-table-column>
      <el-table-column label="库存" width="100">
        <template slot-scope="scope">
          {{ scope.row.batch_details?.quantity || 0 }}
        </template>
      </el-table-column>
      <el-table-column label="客户" width="120">
        <template slot-scope="scope">
          {{ scope.row.customer_name }}
        </template>
      </el-table-column>
      <el-table-column prop="quantity" label="数量" width="100"></el-table-column>
      <el-table-column prop="unit_price" label="单价" width="100">
        <template slot-scope="scope">
          ¥{{ scope.row.unit_price }}
        </template>
      </el-table-column>
      <el-table-column prop="total_amount" label="总金额" width="120">
        <template slot-scope="scope">
          ¥{{ scope.row.total_amount }}
        </template>
      </el-table-column>
      <el-table-column prop="payment_method" label="支付方式" width="100"></el-table-column>
      <el-table-column prop="sale_date" label="销售日期" width="180">
        <template slot-scope="scope">
          {{ scope.row.sale_date | formatDateTime }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="150">
        <template slot-scope="scope">
          <el-button size="mini" @click="handleView(scope.row)">查看</el-button>
          <el-button size="mini" type="danger" @click="handleDelete(scope.row)">删除</el-button>
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

    <!-- 添加/查看对话框 -->
    <el-dialog :title="dialogTitle" :visible.sync="dialogVisible" width="50%">
      <el-form :model="form" :rules="rules" ref="form" label-width="100px">
        <el-form-item label="批次" prop="batch">
          <el-select v-model="form.batch" placeholder="请选择批次" filterable>
            <el-option
              v-for="item in batches"
              :key="item.id"
              :label="item.batch_number"
              :value="item.id">
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="客户名称" prop="customer_name">
          <el-input v-model="form.customer_name"></el-input>
        </el-form-item>
        <el-form-item label="联系电话" prop="customer_phone">
          <el-input v-model="form.customer_phone"></el-input>
        </el-form-item>
        <el-form-item label="客户地址" prop="customer_address">
          <el-input v-model="form.customer_address"></el-input>
        </el-form-item>
        <el-form-item label="数量" prop="quantity">
          <el-input-number v-model="form.quantity" :min="1"></el-input-number>
        </el-form-item>
        <el-form-item label="单价" prop="unit_price">
          <el-input-number v-model="form.unit_price" :min="0" :precision="2"></el-input-number>
        </el-form-item>
        <el-form-item label="总金额" prop="total_amount">
          <el-input-number v-model="form.total_amount" :min="0" :precision="2" :disabled="true"></el-input-number>
        </el-form-item>
        <el-form-item label="支付方式" prop="payment_method">
          <el-select v-model="form.payment_method" placeholder="请选择支付方式">
            <el-option label="现金" value="cash"></el-option>
            <el-option label="微信" value="wechat"></el-option>
            <el-option label="支付宝" value="alipay"></el-option>
            <el-option label="银行转账" value="bank"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="交易号" prop="transaction_id">
          <el-input v-model="form.transaction_id"></el-input>
        </el-form-item>
        <el-form-item label="销售日期" prop="sale_date">
          <el-date-picker
            v-model="form.sale_date"
            type="datetime"
            placeholder="选择日期时间">
          </el-date-picker>
        </el-form-item>
        <el-form-item label="备注" prop="remark">
          <el-input type="textarea" v-model="form.remark"></el-input>
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="dialogVisible = false">取 消</el-button>
        <el-button type="primary" @click="handleSubmit">确 定</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'SalesRecord',
  filters: {
    formatDateTime(value) {
      if (!value) return '-';
      try {
        const date = new Date(value);
        return date.toLocaleString();
      } catch (e) {
        console.error('Date parsing error:', e);
        return '-';
      }
    }
  },
  data() {
    return {
      searchForm: {
        batch: '',
        date_range: [],
        customer: ''
      },
      records: [],
      batches: [],
      page: 1,
      pageSize: 10,
      total: 0,
      loading: false,
      dialogVisible: false,
      dialogTitle: '添加销售记录',
      form: {
        batch: '',
        customer_name: '',
        customer_phone: '',
        customer_address: '',
        quantity: 1,
        unit_price: 0,
        total_amount: 0,
        payment_method: '',
        transaction_id: '',
        sale_date: new Date(),
        remark: ''
      },
      rules: {
        batch: [{ required: true, message: '请选择批次', trigger: 'change' }],
        customer_name: [{ required: true, message: '请输入客户名称', trigger: 'blur' }],
        customer_phone: [{ required: true, message: '请输入联系电话', trigger: 'blur' }],
        quantity: [{ required: true, message: '请输入数量', trigger: 'blur' }],
        unit_price: [{ required: true, message: '请输入单价', trigger: 'blur' }],
        payment_method: [{ required: true, message: '请选择支付方式', trigger: 'change' }],
        sale_date: [{ required: true, message: '请选择销售日期', trigger: 'change' }]
      }
    }
  },
  created() {
    this.fetchBatches()
    this.fetchRecords()
  },
  watch: {
    'form.quantity': {
      handler() {
        this.calculateTotal()
      }
    },
    'form.unit_price': {
      handler() {
        this.calculateTotal()
      }
    }
  },
  methods: {
    fetchBatches() {
      this.$axios.get(this.$httpUrl + '/api/products/batches/')
        .then(res => {
          console.log('Batches response:', res.data);
          if (Array.isArray(res.data)) {
            this.batches = res.data;
          } else if (res.data && Array.isArray(res.data.results)) {
            this.batches = res.data.results;
          } else {
            this.batches = [];
            console.warn('Invalid batches data format:', res.data);
          }
        })
        .catch(err => {
          console.error('Error fetching batches:', err);
          this.$message.error('获取批次列表失败');
        });
    },
    async fetchRecords() {
      try {
        this.loading = true
        // 确保请求头中包含认证 token
        const token = localStorage.getItem('token')
        const response = await axios.get('/api/tracing/sales/', {
          headers: {
            'Authorization': `Bearer ${token}`
          },
          params: {
            page: this.page,
            page_size: this.pageSize,
            batch: this.searchForm.batch,
            date_from: this.searchForm.date_range?.[0]?.toISOString(),
            date_to: this.searchForm.date_range?.[1]?.toISOString(),
            customer: this.searchForm.customer
          }
        })
        this.records = response.data.results
        console.log(1111111)
        console.log( this.records)
        console.log(2222)
        this.total = response.data.count
      } catch (error) {
        console.error('Error fetching sales records:', error)
        this.$message.error('获取销售记录失败')
      } finally {
        this.loading = false
      }
    },
    handleSearch() {
      this.page = 1
      this.fetchRecords()
    },
    resetSearch() {
      this.searchForm = {
        batch: '',
        date_range: [],
        customer: ''
      }
      this.handleSearch()
    },
    handleSizeChange(val) {
      this.pageSize = val
      this.fetchRecords()
    },
    handleCurrentChange(val) {
      this.page = val
      this.fetchRecords()
    },
    handleAdd() {
      this.dialogTitle = '添加销售记录'
      this.form = {
        batch: '',
        customer_name: '',
        customer_phone: '',
        customer_address: '',
        quantity: 1,
        unit_price: 0,
        total_amount: 0,
        payment_method: '',
        transaction_id: '',
        sale_date: new Date(),
        remark: ''
      }
      this.dialogVisible = true
    },
    handleView(row) {
      this.dialogTitle = '查看销售记录'
      this.form = { ...row }
      this.dialogVisible = true
    },
    handleDelete(row) {
      this.$confirm('确认删除该销售记录?', '提示', {
        type: 'warning'
      }).then(() => {
        this.$axios.delete(this.$httpUrl + `/api/tracing/sales/${row.id}/`)
          .then(() => {
            this.$message.success('删除成功')
            this.fetchRecords()
          })
          .catch(err => {
            this.$message.error('删除失败')
            console.error(err)
          })
      })
    },
    calculateTotal() {
      this.form.total_amount = this.form.quantity * this.form.unit_price
    },
    handleSubmit() {
      this.$refs.form.validate(valid => {
        if (valid) {
          // 确保日期格式正确
          const formData = {
            ...this.form,
            sale_date: this.form.sale_date.toISOString()
          }
          
          this.$axios.post('/api/tracing/sales/', formData)
            .then(() => {
              this.$message.success('添加成功')
              this.dialogVisible = false
              this.fetchRecords()
            })
            .catch(err => {
              console.error(err)
              this.$message.error('添加失败')
            })
        }
      })
    }
  }
}
</script>

<style scoped>
.sales-container {
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
</style> 