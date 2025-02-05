<template>
  <div class="production-container">
    <div class="page-header">
      <h2>生产记录管理</h2>
      <el-button type="primary" @click="handleAdd">添加生产记录</el-button>
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



    <!-- 生产记录列表 -->
    <el-table 
      :data="records" 
      border 
      style="width: 100%"
      v-loading="loading"
      :empty-text="loading ? '加载中...' : '暂无数据'"
      @row-click="handleRowClick">
      <el-table-column prop="batch_number" label="批次号" width="180">
        <template slot-scope="scope">
          <span :title="JSON.stringify(scope.row)">
            {{ scope.row.batch_number || '-' }}
          </span>
        </template>
      </el-table-column>
      <el-table-column prop="batch_details.product.name" label="商品名称">
        <template slot-scope="scope">
          {{ scope.row.batch_details?.product?.name || '-' }}
        </template>
      </el-table-column>
      <el-table-column prop="production_date" label="生产日期" width="180">
        <template slot-scope="scope">
          {{ scope.row.production_date | formatDateTime }}
        </template>
      </el-table-column>
      <el-table-column prop="production_line" label="生产线" width="120"></el-table-column>
      <el-table-column prop="operator_name" label="操作员" width="120">
        <template slot-scope="scope">
          {{ scope.row.operator_name || '-' }}
        </template>
      </el-table-column>
      <el-table-column prop="temperature" label="温度" width="100">
        <template slot-scope="scope">
          {{ scope.row.temperature ? `${scope.row.temperature}°C` : '-' }}
        </template>
      </el-table-column>
      <el-table-column prop="humidity" label="湿度" width="100">
        <template slot-scope="scope">
          {{ scope.row.humidity ? `${scope.row.humidity}%` : '-' }}
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
    <el-dialog :title="dialogTitle" :visible.sync="dialogVisible" width="60%">
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
        <el-form-item label="生产日期" prop="production_date">
          <el-date-picker
            v-model="form.production_date"
            type="datetime"
            placeholder="选择日期时间">
          </el-date-picker>
        </el-form-item>
        <el-form-item label="生产线" prop="production_line">
          <el-input v-model="form.production_line"></el-input>
        </el-form-item>
        <el-form-item label="温度" prop="temperature">
          <el-input-number v-model="form.temperature" :precision="1" :step="0.1"></el-input-number>
        </el-form-item>
        <el-form-item label="湿度" prop="humidity">
          <el-input-number v-model="form.humidity" :precision="1" :step="0.1"></el-input-number>
        </el-form-item>
        <el-form-item label="原材料信息" prop="raw_materials">
          <el-table :data="form.raw_materials" border>
            <el-table-column prop="name" label="材料名称">
              <template slot-scope="scope">
                <el-input v-model="scope.row.name"></el-input>
              </template>
            </el-table-column>
            <el-table-column prop="quantity" label="数量">
              <template slot-scope="scope">
                <el-input-number v-model="scope.row.quantity" :min="0"></el-input-number>
              </template>
            </el-table-column>
            <el-table-column prop="unit" label="单位">
              <template slot-scope="scope">
                <el-input v-model="scope.row.unit"></el-input>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="100">
              <template slot-scope="scope">
                <el-button type="text" @click="removeMaterial(scope.$index)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
          <div style="margin-top: 10px">
            <el-button type="text" @click="addMaterial">添加原材料</el-button>
          </div>
        </el-form-item>
        <el-form-item label="质检信息" prop="quality_check">
          <el-table :data="form.quality_check" border>
            <el-table-column prop="item" label="检查项">
              <template slot-scope="scope">
                <el-input v-model="scope.row.item"></el-input>
              </template>
            </el-table-column>
            <el-table-column prop="standard" label="标准">
              <template slot-scope="scope">
                <el-input v-model="scope.row.standard"></el-input>
              </template>
            </el-table-column>
            <el-table-column prop="result" label="结果">
              <template slot-scope="scope">
                <el-select v-model="scope.row.result">
                  <el-option label="合格" value="pass"></el-option>
                  <el-option label="不合格" value="fail"></el-option>
                </el-select>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="100">
              <template slot-scope="scope">
                <el-button type="text" @click="removeQualityCheck(scope.$index)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
          <div style="margin-top: 10px">
            <el-button type="text" @click="addQualityCheck">添加质检项</el-button>
          </div>
        </el-form-item>
        <el-form-item label="备注">
          <el-input type="textarea" v-model="form.remark"></el-input>
        </el-form-item>
      </el-form>
      <div slot="footer">
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" v-if="!form.id">确定</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
export default {
  name: 'ProductionRecord',
  filters: {
    formatDateTime(value) {
      if (!value) return ''
      const date = new Date(value)
      return `${date.toLocaleDateString()} ${date.toLocaleTimeString()}`
    }
  },
  data() {
    return {
      searchForm: {
        batch: '',
        date_range: []
      },
      records: [],
      batches: [],
      page: 1,
      pageSize: 10,
      total: 0,
      dialogVisible: false,
      dialogTitle: '添加生产记录',
      form: {
        batch: '',
        production_date: '',
        production_line: '',
        temperature: 25,
        humidity: 50,
        raw_materials: [],
        quality_check: [],
        remark: ''
      },
      rules: {
        batch: [{ required: true, message: '请选择批次', trigger: 'change' }],
        production_date: [{ required: true, message: '请选择生产日期', trigger: 'change' }],
        production_line: [{ required: true, message: '请输入生产线', trigger: 'blur' }]
      },
      loading: false
    }
  },
  created() {
    this.fetchBatches()
    this.fetchRecords()
  },
  methods: {
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
        date_from: this.searchForm.date_range?.[0],
        date_to: this.searchForm.date_range?.[1]
      }
      console.log('Fetching records with params:', params);
      
      this.$axios.get(this.$httpUrl + '/api/tracing/production/', { params })
        .then(res => {
          console.log('Raw API response:', res);
          console.log('Records data:', res.data);
          this.records = [...(res.data.results || [])];
          console.log('Processed records:', this.records);
          if (this.records.length > 0) {
            console.log('First record details:', {
              batch_number: this.records[0].batch_number,
              product_name: this.records[0].batch_details?.product?.name,
              operator_name: this.records[0].operator_name,
              temperature: this.records[0].temperature,
              humidity: this.records[0].humidity
            });
          }
          this.total = res.data.count || 0;
        })
        .catch(err => {
          this.$message.error('获取生产记录失败');
          console.error('Error fetching records:', err);
        })
        .finally(() => {
          this.loading = false;
        });
    },
    handleSearch() {
      this.page = 1
      this.fetchRecords()
    },
    resetSearch() {
      this.searchForm = {
        batch: '',
        date_range: []
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
      this.dialogTitle = '添加生产记录'
      this.form = {
        batch: '',
        production_date: new Date(),
        production_line: '',
        temperature: 25,
        humidity: 50,
        raw_materials: [],
        quality_check: [],
        remark: ''
      }
      this.dialogVisible = true
    },
    handleView(row) {
      this.dialogTitle = '查看生产记录'
      this.form = { ...row }
      this.dialogVisible = true
    },
    handleDelete(row) {
      this.$confirm('确认删除该生产记录?', '提示', {
        type: 'warning'
      }).then(() => {
        this.$axios.delete(this.$httpUrl + `/api/tracing/production/${row.id}/`)
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
    addMaterial() {
      this.form.raw_materials.push({
        name: '',
        quantity: 0,
        unit: ''
      })
    },
    removeMaterial(index) {
      this.form.raw_materials.splice(index, 1)
    },
    addQualityCheck() {
      this.form.quality_check.push({
        item: '',
        standard: '',
        result: 'pass'
      })
    },
    removeQualityCheck(index) {
      this.form.quality_check.splice(index, 1)
    },
    handleSubmit() {
      this.$refs.form.validate(valid => {
        if (valid) {
          this.$axios.post(this.$httpUrl + '/api/tracing/production/', this.form)
            .then(() => {
              this.$message.success('添加成功')
              this.dialogVisible = false
              this.fetchRecords()
            })
            .catch(err => {
              this.$message.error('添加失败')
              console.error(err)
            })
        }
      })
    },
    handleRowClick(row) {
      console.log('Row clicked:', row);
      console.log('Row batch number:', row.batch_number);
      console.log('Row product name:', row.batch_details?.product?.name);
    }
  }
}
</script>

<style scoped>
.production-container {
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