<template>
  <div class="logistics-container">
    <div class="page-header">
      <h2>物流记录管理</h2>
      <el-button type="primary" @click="handleAdd" v-if="!isAdmin">添加物流记录</el-button>
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
      <el-form-item label="记录类型">
        <el-select v-model="searchForm.record_type" placeholder="请选择类型">
          <el-option label="入库" value="storage"></el-option>
          <el-option label="出库" value="delivery"></el-option>
          <el-option label="运输" value="transport"></el-option>
        </el-select>
      </el-form-item>
      <el-form-item label="状态">
        <el-select v-model="searchForm.status" placeholder="请选择状态">
          <el-option label="待处理" value="pending"></el-option>
          <el-option label="进行中" value="in_progress"></el-option>
          <el-option label="已完成" value="completed"></el-option>
          <el-option label="异常" value="exception"></el-option>
        </el-select>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="handleSearch">查询</el-button>
        <el-button @click="resetSearch">重置</el-button>
      </el-form-item>
    </el-form>

    <!-- 物流记录列表 -->
    <el-table 
      :data="records" 
      border 
      style="width: 100%"
      v-loading="loading"
      :empty-text="loading ? '加载中...' : '暂无数据'">
      <!-- 批次号 -->
      <el-table-column label="批次号" width="180">
        <template slot-scope="scope">
          {{ scope.row.batch_number }}
        </template>
      </el-table-column>

      <!-- 商品名称 -->
      <el-table-column label="商品名称" width="180">
        <template slot-scope="scope">
          {{ scope.row.batch_details?.product_name }}
        </template>
      </el-table-column>

      <!-- 规格 -->
      <el-table-column label="规格" width="120">
        <template slot-scope="scope">
          {{ scope.row.batch_details?.specifications. description}}
        </template>
      </el-table-column>

      <!-- 记录类型 -->
      <el-table-column label="记录类型" width="100">
        <template slot-scope="scope">
          {{ getRecordTypeText(scope.row.record_type) }}
        </template>
      </el-table-column>

      <!-- 起始位置 -->
      <el-table-column label="起始位置">
        <template slot-scope="scope">
          {{ scope.row.from_location }}
        </template>
      </el-table-column>

      <!-- 目标位置 -->
      <el-table-column label="目标位置">
        <template slot-scope="scope">
          {{ scope.row.to_location }}
        </template>
      </el-table-column>

      <!-- 操作员 -->
      <el-table-column label="操作员" width="120">
        <template slot-scope="scope">
          {{ scope.row.operator_name }}
        </template>
      </el-table-column>

      <!-- 状态 -->
      <el-table-column label="状态" width="100">
        <template slot-scope="scope">
          <el-tag :type="getStatusType(scope.row.status)">
            {{ getStatusText(scope.row.status) }}
          </el-tag>
        </template>
      </el-table-column>

      <!-- 创建时间 -->
      <el-table-column label="创建时间" width="180">
        <template slot-scope="scope">
          {{ formatDateTime(scope.row.created_at) }}
        </template>
      </el-table-column>

      <!-- 操作 -->
      <el-table-column label="操作" width="200" fixed="right">
        <template slot-scope="scope">
          <el-button 
            size="mini" 
            @click.stop="handleEdit(scope.row)" v-if="!isAdmin">
            编辑
          </el-button>
          <el-button 
            size="mini" 
            type="danger" 
            @click.stop="handleDelete(scope.row)" v-if="!isAdmin">
            删除
          </el-button>
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
        <el-form-item label="批次" prop="batch">
          <el-select v-model="form.batch" placeholder="请选择批次" filterable :disabled="!!form.id">
            <el-option
              v-for="item in batches"
              :key="item.id"
              :label="item.batch_number"
              :value="item.id">
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="记录类型" prop="record_type">
          <el-select v-model="form.record_type" placeholder="请选择类型">
            <el-option label="入库" value="storage"></el-option>
            <el-option label="出库" value="delivery"></el-option>
            <el-option label="运输" value="transport"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="起始位置" prop="from_location">
          <el-input v-model="form.from_location"></el-input>
        </el-form-item>
        <el-form-item label="目标位置" prop="to_location">
          <el-input v-model="form.to_location"></el-input>
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-select v-model="form.status" placeholder="请选择状态">
            <el-option label="待处理" value="pending"></el-option>
            <el-option label="处理中" value="processing"></el-option>
            <el-option label="已完成" value="completed"></el-option>
          </el-select>
        </el-form-item>
      </el-form>
      <div slot="footer">
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </div>
    </el-dialog>

    <!-- 状态更新对话框 -->
    <el-dialog title="更新状态" :visible.sync="statusDialogVisible" width="30%">
      <el-form :model="statusForm" label-width="100px">
        <el-form-item label="状态">
          <el-select v-model="statusForm.status" placeholder="请选择状态">
            <el-option label="待处理" value="pending"></el-option>
            <el-option label="进行中" value="in_progress"></el-option>
            <el-option label="已完成" value="completed"></el-option>
            <el-option label="异常" value="exception"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="实际到达">
          <el-date-picker
            v-model="statusForm.actual_arrival"
            type="datetime"
            placeholder="选择日期时间">
          </el-date-picker>
        </el-form-item>
        <el-form-item label="备注">
          <el-input type="textarea" v-model="statusForm.remark"></el-input>
        </el-form-item>
      </el-form>
      <div slot="footer">
        <el-button @click="statusDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitStatusUpdate">确定</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
export default {
  name: 'LogisticsRecord',
  filters: {
    formatDateTime(value) {
      if (!value) return '-';
      if (value instanceof Date) {
        return value.toLocaleString();
      }
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
         isAdmin: JSON.parse(localStorage.getItem('userInfo') || '{}').role === 'admin',

      searchForm: {
        batch: '',
        record_type: '',
        status: ''
      },
      records: [],
      batches: [],
      page: 1,
      pageSize: 10,
      total: 0,
      dialogVisible: false,
      statusDialogVisible: false,
      dialogTitle: '添加物流记录',
      form: {
        batch: '',
        record_type: '',
        from_location: '',
        to_location: '',
        status: 'pending',
        estimated_arrival: '',
        remark: ''
      },
      statusForm: {
        id: '',
        status: '',
        actual_arrival: '',
        remark: ''
      },
      rules: {
        batch: [{ required: true, message: '请选择批次', trigger: 'change' }],
        record_type: [{ required: true, message: '请选择记录类型', trigger: 'change' }],
        from_location: [{ required: true, message: '请输入起始位置', trigger: 'blur' }],
        to_location: [{ required: true, message: '请输入目标位置', trigger: 'blur' }],
        status: [{ required: true, message: '请选择状态', trigger: 'change' }]
      },
      loading: false
    }
  },
  created() {
    this.fetchBatches()
    this.fetchRecords()
  },
  methods: {
    getRecordTypeText(type) {
      const types = {
        storage: '入库',
        delivery: '出库',
        transport: '运输'
      }
      return types[type] || type
    },
    getStatusType(status) {
      const types = {
        pending: 'info',
        in_progress: 'warning',
        completed: 'success',
        exception: 'danger'
      }
      return types[status] || ''
    },
    getStatusText(status) {
      const texts = {
        pending: '待处理',
        in_progress: '进行中',
        completed: '已完成',
        exception: '异常'
      }
      return texts[status] || status
    },
    fetchBatches() {
      this.$axios.get(this.$httpUrl + '/api/products/batches/')
        .then(res => {
          this.batches = res.data.results || []
        })
        .catch(err => {
          this.$message.error('获取批次列表失败')
          console.error(err)
        })
    },
    fetchRecords() {
      this.loading = true;
      const params = {
        page: this.page,
        page_size: this.pageSize,
        batch: this.searchForm.batch,
        record_type: this.searchForm.record_type,
        status: this.searchForm.status
      }
      
      this.$axios.get(this.$httpUrl + '/api/tracing/logistics/', { params })
        .then(res => {
          console.log('Raw API response:', res);
          if (Array.isArray(res.data)) {
            // 直接使用数组数据
            this.records = res.data;
            console.log('Final records array:', this.records);
            // 使用数组长度作为总数
            this.total = res.data.length;
          } else if (res.data && Array.isArray(res.data.results)) {
            // 兼容分页格式
            this.records = res.data.results;
            this.total = res.data.count || 0;
          } else {
            console.warn('Invalid response format:', res.data);
            this.records = [];
            this.total = 0;
          }
        })
        .catch(err => {
          console.error('Error fetching records:', err);
          this.$message.error('获取物流记录失败');
        })
        .finally(() => {
          this.loading = false;
        });
    },
    handleSizeChange(val) {
      this.pageSize = val;
      this.fetchRecords();
    },
    handleCurrentChange(val) {
      this.page = val;
      this.fetchRecords();
    },
    handleAdd() {
      this.dialogTitle = '添加物流记录';
      this.form = {
        batch: '',
        record_type: '',
        from_location: '',
        to_location: '',
        status: 'pending',
        estimated_arrival: '',
        remark: ''
      };
      this.dialogVisible = true;
    },
    handleEdit(row) {
      this.dialogTitle = '编辑物流记录';
      // 创建表单数据的副本，避免直接修改列表数据
      this.form = {
        ...row,
        estimated_arrival: row.estimated_arrival ? new Date(row.estimated_arrival) : null,
        actual_arrival: row.actual_arrival ? new Date(row.actual_arrival) : null
      };
      this.dialogVisible = true;
    },
    handleSubmit() {
      this.$refs.form.validate(valid => {
        if (valid) {
          const method = this.form.id ? 'put' : 'post';
          const url = this.form.id 
            ? `/api/tracing/logistics/${this.form.id}/`
            : '/api/tracing/logistics/';
          
          // 处理日期格式
          const formData = {
            ...this.form,
            estimated_arrival: this.form.estimated_arrival instanceof Date 
              ? this.form.estimated_arrival.toISOString()
              : this.form.estimated_arrival,
            actual_arrival: this.form.actual_arrival instanceof Date
              ? this.form.actual_arrival.toISOString()
              : this.form.actual_arrival
          };
          
          this.$axios[method](this.$httpUrl + url, formData)
            .then(() => {
              this.$message.success(this.form.id ? '更新成功' : '添加成功');
              this.dialogVisible = false;
              this.fetchRecords();
            })
            .catch(err => {
              console.error('Error:', err.response?.data || err);
              this.$message.error(err.response?.data?.error || (this.form.id ? '更新失败' : '添加失败'));
            });
        }
      });
    },
    handleDelete(row) {
      this.$confirm('确认删除该物流记录?', '提示', {
        type: 'warning'
      }).then(() => {
        this.$axios.delete(this.$httpUrl + `/api/tracing/logistics/${row.id}/`)
          .then(() => {
            this.$message.success('删除成功');
            this.fetchRecords();
          })
          .catch(err => {
            this.$message.error('删除失败');
            console.error(err);
          });
      });
    },
    handleSearch() {
      this.page = 1;
      this.fetchRecords();
    },
    resetSearch() {
      this.searchForm = {
        batch: '',
        record_type: '',
        status: ''
      };
      this.handleSearch();
    },
    handleUpdateStatus(row) {
      this.statusForm = {
        id: row.id,
        status: row.status,
        actual_arrival: row.actual_arrival ? new Date(row.actual_arrival) : new Date(),
        remark: row.remark
      };
      this.statusDialogVisible = true;
    },
    submitStatusUpdate() {
      this.$axios.patch(this.$httpUrl + `/api/tracing/logistics/${this.statusForm.id}/`, {
        status: this.statusForm.status,
        actual_arrival: this.statusForm.actual_arrival,
        remark: this.statusForm.remark
      })
        .then(() => {
          this.$message.success('状态更新成功')
          this.statusDialogVisible = false
          this.fetchRecords()
        })
        .catch(err => {
          this.$message.error('状态更新失败')
          console.error(err)
        })
    },
    // 添加一个辅助方法来安全地获取嵌套属性
    getNestedValue(obj, path, defaultValue = '-') {
      try {
        return path.split('.').reduce((current, key) => 
          current && current[key] !== undefined ? current[key] : defaultValue, obj);
      } catch (e) {
        return defaultValue;
      }
    },
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
  }
}
</script>

<style scoped>
.logistics-container {
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