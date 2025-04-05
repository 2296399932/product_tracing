<template>
  <div class="batches-container">
    <div class="page-header">
      <h2>批次管理</h2>
      <el-button type="primary" @click="handleAdd" v-if="!isAdmin">新增批次</el-button>
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
      <el-table-column label="商品图片" width="100">
        <template slot-scope="scope">
          <el-image 
            style="width: 50px; height: 50px"
            :src="scope.row.product_details?.image_url || defaultImage"
            :preview-src-list="scope.row.product_details?.image_url ? [scope.row.product_details.image_url] : []"
            fit="cover">
            <div slot="error" class="image-slot">
              <i class="el-icon-picture-outline"></i>
            </div>
          </el-image>
        </template>
      </el-table-column>
      <el-table-column label="使用原材料" width="200">
        <template slot-scope="scope">
          <el-popover
            placement="right"
            width="400"
            trigger="click">
            <el-table :data="scope.row.materials || []" size="mini" border>
              <el-table-column prop="material_name" label="原材料名称"></el-table-column>
              <el-table-column prop="batch_number" label="批次号"></el-table-column>
              <el-table-column label="用量">
                <template slot-scope="props">
                  {{ props.row.quantity }} {{ props.row.unit }}
                </template>
              </el-table-column>
            </el-table>
            <el-button slot="reference" size="mini" type="info" plain>
              查看原材料 ({{ (scope.row.materials || []).length }})
            </el-button>
          </el-popover>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="250">
        <template slot-scope="scope">
          <el-button size="mini" @click="handleEdit(scope.row)" v-if="!isAdmin">编辑</el-button>
          <el-button size="mini" type="success" @click="handleViewQR(scope.row)">查看二维码</el-button>
          <el-button size="mini" type="danger" @click="handleDelete(scope.row)" v-if="!isAdmin">删除</el-button>
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
          <el-input v-model="form.batch_number" style="width: 30%"></el-input>
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
        
        <!-- 新增原材料部分 -->
        <div class="materials-section">
          <div class="materials-header">
            <h3>原材料列表</h3>
            <el-button type="primary" size="small" @click="addMaterial">添加原材料</el-button>
          </div>
          
          <div v-if="form.materials && form.materials.length > 0" class="materials-list">
            <el-card v-for="(material, index) in form.materials" :key="index" class="material-item">
              <div class="material-header">
                <span>原材料 #{{ index + 1 }}</span>
                <el-button type="danger" icon="el-icon-delete" size="mini" circle 
                  @click="removeMaterial(index)"></el-button>
              </div>
              
              <el-form-item :label="'原材料批次'" :prop="'materials.' + index + '.material_batch'">
                <el-select v-model="material.material_batch" filterable placeholder="选择原材料批次">
                  <el-option
                    v-for="item in materialBatches"
                    :key="item.id"
                    :label="item.material_name + ' - ' + item.batch_number"
                    :value="item.id">
                  </el-option>
                </el-select>
              </el-form-item>
              
              <el-form-item :label="'使用数量'" :prop="'materials.' + index + '.quantity'">
                <el-input-number v-model="material.quantity" :min="0.01" :precision="2"></el-input-number>
              </el-form-item>
              
              <el-form-item :label="'单位'" :prop="'materials.' + index + '.unit'">
                <el-input v-model="material.unit" placeholder="例如：克、千克、个"></el-input>
              </el-form-item>
            </el-card>
          </div>
          
          <div v-else class="no-materials">
            <el-empty description="暂无原材料，请添加"></el-empty>
          </div>
        </div>
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
        date_range: [],

      },
         isAdmin: JSON.parse(localStorage.getItem('userInfo') || '{}').role === 'admin',
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
        status: 'active',
        materials: []
      },
      rules: {
        product: [{ required: true, message: '请选择商品', trigger: 'change' }],
        batch_number: [{ required: true, message: '请输入批次号', trigger: 'blur' }],
        production_date: [{ required: true, message: '请选择生产日期', trigger: 'change' }],
        expiry_date: [{ required: true, message: '请选择有效期', trigger: 'change' }],
        quantity: [{ required: true, message: '请输入数量', trigger: 'blur' }],
        cost_price: [{ required: true, message: '请输入成本价', trigger: 'blur' }],
        'materials.*.material_batch': [{ required: true, message: '请选择原材料批次', trigger: 'change' }],
        'materials.*.quantity': [{ required: true, message: '请输入使用数量', trigger: 'blur' }],
        'materials.*.unit': [{ required: true, message: '请输入单位', trigger: 'blur' }]
      },
      statusOptions: [
        { value: 'active', label: '正常' },
        { value: 'sold_out', label: '售罄' },
        { value: 'expired', label: '过期' },
        { value: 'disabled', label: '停用' }
      ],
      defaultImage: require('@/assets/img/bo.jpg'),
      materialBatches: []
    }
  },
  created() {
    this.fetchProducts()
    this.fetchBatches()
    this.fetchMaterialBatches()
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
    fetchMaterialBatches() {
      this.$axios.get(this.$httpUrl + '/api/materials/batches/')
        .then(res => {
          // 确保我们正确处理API返回的数据结构
          if (res.data && res.data.results) {
            this.materialBatches = res.data.results || res.data;
          } else if (Array.isArray(res.data)) {
            this.materialBatches = res.data;
          } else {
            this.materialBatches = [];
            console.error('Unexpected API response format:', res.data);
          }
          console.log('Material batches loaded:', this.materialBatches);
        })
        .catch(err => {
          this.$message.error('获取原材料批次列表失败');
          console.error('获取原材料批次失败:', err);
          this.materialBatches = [];
        });
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
      
      // 生成建议的批次号
      const today = new Date();
      const dateStr = today.toISOString().slice(0, 10).replace(/-/g, '');
      const randomStr = Math.floor(Math.random() * 1000).toString().padStart(3, '0');
      const suggestedBatchNumber = `B${dateStr}${randomStr}`;
      
      this.form = {
        product: '',
        batch_number: suggestedBatchNumber, // 使用生成的批次号
        production_date: '',
        expiry_date: '',
        quantity: 0,
        cost_price: 0,
        status: 'active',
        materials: []
      }
      this.dialogVisible = true
    },
    handleEdit(row) {
      this.form = { ...row }
      if (!['active', 'sold_out', 'expired', 'disabled'].includes(this.form.status)) {
        this.form.status = 'active'
      }
      
      // 获取此批次已关联的原材料
      this.$axios.get(this.$httpUrl + `/api/products/batches/${row.id}/materials/`)
        .then(res => {
          this.form.materials = res.data.map(item => ({
            material_batch: item.material_batch,
            quantity: item.quantity,
            unit: item.unit
          }))
        })
        .catch(err => {
          console.error('加载原材料失败:', err)
          this.form.materials = []
          this.$message.warning('加载原材料失败，请重新添加')
        })
      
      this.dialogVisible = true
      this.dialogTitle = '编辑批次'
    },
    handleViewQR(row) {
      this.$axios.get(this.$httpUrl + `/api/tracing/qrcode/${row.batch_number}/`)
        .then(res => {
          console.log('QR code response:', res.data)
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
          
          // 打印请求数据便于调试
          console.log('提交的批次数据:', formData);
          
          // 移除表单中的materials，将在后续操作中单独提交
          const materials = [...formData.materials || []];
          delete formData.materials;
          
          const method = this.form.id ? 'put' : 'post';
          const url = this.form.id 
            ? `/api/products/batches/${this.form.id}/`
            : '/api/products/batches/';
          
          this.$axios[method](this.$httpUrl + url, formData)
            .then(response => {
              const batchId = this.form.id || response.data.id;
              
              // 如果有原材料，提交原材料关联
              if (materials && materials.length > 0) {
                return this.$axios.post(this.$httpUrl + `/api/products/batches/${batchId}/materials/`, {
                  materials: materials
                });
              }
              return Promise.resolve();
            })
            .then(() => {
              this.$message.success(this.form.id ? '更新成功' : '添加成功');
              this.dialogVisible = false;
              this.fetchBatches();
            })
            .catch(err => {
              // 详细记录错误信息
              console.error('错误详情:', {
                status: err.response?.status,
                data: err.response?.data,
                headers: err.response?.headers,
                requestData: formData
              });
              
              // 处理材料重复错误
              if (err.response?.data?.error && err.response.data.error.includes('Duplicate entry')) {
                this.$message.error('存在重复的原材料批次，请检查后重试');
                return;
              }
              
              if (err.response?.data?.batch_number) {
                this.$message.error(`批次号错误: ${err.response.data.batch_number[0]}`);
              } else if (err.response?.data?.production_date) {
                this.$message.error(`生产日期错误: ${err.response.data.production_date[0]}`);
              } else if (err.response?.data?.expiry_date) {
                this.$message.error(`有效期错误: ${err.response.data.expiry_date[0]}`);
              } else if (err.response?.data?.quantity) {
                this.$message.error(`数量错误: ${err.response.data.quantity[0]}`);
              } else if (err.response?.data?.cost_price) {
                this.$message.error(`成本价错误: ${err.response.data.cost_price[0]}`);
              } else if (err.response?.data?.status) {
                this.$message.error(`状态错误: ${err.response.data.status[0]}`);
              } else if (err.response?.data?.error) {
                this.$message.error(err.response.data.error);
              } else {
                this.$message.error(this.form.id ? '更新失败' : '添加失败');
              }
            });
        }
      });
    },
    formatDate(date) {
      if (!date) return null;
      if (typeof date === 'string') return date;
      return date.toISOString().split('T')[0];
    },
    addMaterial() {
      if (!this.form.materials) {
        this.form.materials = []
      }
      this.form.materials.push({
        material_batch: '',
        quantity: 1,
        unit: ''
      })
    },
    removeMaterial(index) {
      this.form.materials.splice(index, 1)
    },
    handleDelete(row) {
      this.$confirm('确认删除该批次吗？此操作不可逆', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        this.$axios.delete(this.$httpUrl + `/api/products/batches/${row.id}/`)
          .then(() => {
            this.$message.success('删除成功');
            this.fetchBatches();
          })
          .catch(err => {
            console.error('删除失败:', err.response?.data || err);
            this.$message.error(err.response?.data?.error || '删除失败');
          });
      }).catch(() => {
        // 用户取消删除操作
      });
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
.materials-section {
  margin-top: 20px;
  border-top: 1px solid #ebeef5;
  padding-top: 15px;
}
.materials-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}
.materials-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 500;
}
.materials-list {
  margin-bottom: 15px;
}
.material-item {
  margin-bottom: 15px;
  border: 1px solid #ebeef5;
}
.material-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 1px dashed #ebeef5;
}
.no-materials {
  margin: 20px 0;
}
</style> 