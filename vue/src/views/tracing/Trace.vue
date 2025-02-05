<template>
  <div class="trace-container">
    <div class="search-section">
      <h2>产品追溯查询</h2>
      <el-form :inline="true" class="search-form">
        <el-form-item label="批次号">
          <el-autocomplete
            v-model="batchNumber"
            :fetch-suggestions="queryBatchNumbers"
            placeholder="请输入批次号"
            :trigger-on-focus="true"
            @select="handleSelect">
            <template slot-scope="{ item }">
              <div>
                <span>{{ item.batch_number }}</span>
                <span class="suggestion-detail">
                  {{ item.product_name }} | {{ item.production_date | formatDate }}
                </span>
              </div>
            </template>
          </el-autocomplete>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch" :loading="loading">查询</el-button>
          <el-button @click="handleScan">扫码查询</el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- 加载状态 -->
    <el-card v-if="loading" class="trace-card">
      <div class="loading-container">
        <el-spinner></el-spinner>
        <p>正在加载追溯信息...</p>
      </div>
    </el-card>

    <!-- 无数据提示 -->
    <el-card v-else-if="!traceData" class="trace-card">
      <div class="empty-container">
        <i class="el-icon-search"></i>
        <p>请输入批次号进行查询</p>
      </div>
    </el-card>

    <div v-else class="trace-content">
      <!-- 产品基本信息 -->
      <el-card class="trace-card">
        <div slot="header">
          <span>产品信息</span>
        </div>
        <el-descriptions :column="2" border>
          <el-descriptions-item label="产品名称">
            {{ traceData.product?.name || '暂无数据' }}
          </el-descriptions-item>
          <el-descriptions-item label="批次号">
            {{ traceData.batch_number || '暂无数据' }}
          </el-descriptions-item>
          <el-descriptions-item label="生产日期">
            {{ traceData.production_date | formatDate }}
          </el-descriptions-item>
          <el-descriptions-item label="有效期">
            {{ traceData.expiry_date | formatDate }}
          </el-descriptions-item>
          <el-descriptions-item label="规格">
            {{ traceData.product?.specifications || '暂无数据' }}
          </el-descriptions-item>
          <el-descriptions-item label="生产企业">
            {{ traceData.manufacturer || '暂无数据' }}
          </el-descriptions-item>
        </el-descriptions>
      </el-card>

      <!-- 生产记录 -->
      <el-card class="trace-card" v-if="traceData.production_records?.length">
        <div slot="header">
          <span>生产记录</span>
        </div>
        <el-timeline>
          <el-timeline-item
            v-for="(record, index) in traceData.production_records"
            :key="index"
            :timestamp="record.production_date | formatDateTime"
            placement="top">
            <el-card>
              <h4>生产线: {{ record.production_line }}</h4>
              <p>操作员: {{ record.operator_name }}</p>
              <p>环境温度: {{ record.temperature }}°C</p>
              <p>环境湿度: {{ record.humidity }}%</p>
              <div v-if="record.quality_check?.length">
                <h4>质检记录:</h4>
                <el-table :data="record.quality_check" border size="small">
                  <el-table-column prop="item" label="检查项"></el-table-column>
                  <el-table-column prop="standard" label="标准"></el-table-column>
                  <el-table-column prop="result" label="结果">
                    <template slot-scope="scope">
                      <el-tag :type="scope.row.result === 'pass' ? 'success' : 'danger'">
                        {{ scope.row.result === 'pass' ? '合格' : '不合格' }}
                      </el-tag>
                    </template>
                  </el-table-column>
                </el-table>
              </div>
            </el-card>
          </el-timeline-item>
        </el-timeline>
      </el-card>

      <!-- 物流记录 -->
      <el-card class="trace-card" v-if="traceData.logistics_records?.length">
        <div slot="header">
          <span>物流记录</span>
        </div>
        <el-steps :active="traceData.logistics_records.length" direction="vertical">
          <el-step 
            v-for="(record, index) in traceData.logistics_records" 
            :key="index"
            :title="record.record_type | logisticsType"
            :description="getLogisticsDescription(record)">
            <template slot="icon">
              <i :class="getLogisticsIcon(record.record_type)"></i>
            </template>
          </el-step>
        </el-steps>
      </el-card>

      <!-- 销售记录 -->
      <el-card class="trace-card" v-if="traceData.sales_record">
        <div slot="header">
          <span>销售信息</span>
        </div>
        <el-descriptions :column="2" border>
          <el-descriptions-item label="销售日期">
            {{ traceData.sales_record.sale_date | formatDateTime }}
          </el-descriptions-item>
          <el-descriptions-item label="销售数量">
            {{ traceData.sales_record.quantity }}
          </el-descriptions-item>
          <el-descriptions-item label="销售单价">
            ¥{{ traceData.sales_record.unit_price }}
          </el-descriptions-item>
          <el-descriptions-item label="销售金额">
            ¥{{ traceData.sales_record.total_amount }}
          </el-descriptions-item>
          <el-descriptions-item label="支付方式">
            {{ traceData.sales_record.payment_method | paymentMethod }}
          </el-descriptions-item>
          <el-descriptions-item label="交易编号">
            {{ traceData.sales_record.transaction_id }}
          </el-descriptions-item>
        </el-descriptions>
      </el-card>
    </div>

    <!-- 扫码对话框 -->
    <el-dialog title="扫描二维码" :visible.sync="scanDialogVisible" width="300px">
      <div class="qr-scanner">
        <div v-if="loading" class="loading">
          <el-spinner></el-spinner>
          <p>正在初始化扫描...</p>
        </div>
        <div v-else>
          <video ref="video" class="scanner-video"></video>
          <canvas ref="canvas" style="display: none;"></canvas>
          <p>请将二维码对准扫描框</p>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import jsQR from 'jsqr'  // 需要安装 jsqr 包

export default {
  name: 'TraceQuery',
  filters: {
    formatDate(value) {
      if (!value) return ''
      return new Date(value).toLocaleDateString()
    },
    formatDateTime(value) {
      if (!value) return ''
      const date = new Date(value)
      return `${date.toLocaleDateString()} ${date.toLocaleTimeString()}`
    },
    logisticsType(type) {
      const types = {
        storage: '入库',
        delivery: '出库',
        transport: '运输中'
      }
      return types[type] || type
    },
    paymentMethod(method) {
      const methods = {
        cash: '现金',
        wechat: '微信',
        alipay: '支付宝',
        bank: '银行转账'
      }
      return methods[method] || method
    }
  },
  data() {
    return {
      batchNumber: '',
      traceData: null,
      scanDialogVisible: false,
      loading: false,
      batchSuggestions: [],
      error: null
    }
  },
  methods: {
    queryBatchNumbers(queryString, cb) {
      if (queryString.length === 0) {
        this.$axios.get(this.$httpUrl + '/api/tracing/recent-batches/')
          .then(res => {
            this.batchSuggestions = res.data
            cb(this.batchSuggestions)
          })
          .catch(err => {
            console.error('获取最近批次失败:', err)
            cb([])
          })
      } else {
        this.$axios.get(this.$httpUrl + '/api/tracing/search-batches/', {
          params: { query: queryString }
        })
          .then(res => {
            this.batchSuggestions = res.data
            cb(this.batchSuggestions)
          })
          .catch(err => {
            console.error('搜索批次失败:', err)
            cb([])
          })
      }
    },
    handleSelect(item) {
      this.batchNumber = item.batch_number
      this.handleSearch()
    },
    handleSearch() {
      if (!this.batchNumber) {
        this.$message.warning('请输入批次号')
        return
      }
      
      this.loading = true
      this.traceData = null
      
      this.$axios.get(this.$httpUrl + `/api/tracing/trace/${this.batchNumber}/`)
        .then(res => {
          if (res.data) {
            this.traceData = res.data
            console.log('Trace data:', this.traceData)
          } else {
            this.$message.warning('未找到相关追溯信息')
          }
        })
        .catch(err => {
          console.error('获取追溯信息失败:', err)
          this.$message.error(err.response?.data?.error || '获取追溯信息失败')
        })
        .finally(() => {
          this.loading = false
        })
    },
    handleScan() {
      this.scanDialogVisible = true
      this.$nextTick(() => {
        this.startScanner()
      })
    },
    
    async startScanner() {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' } })
        const video = this.$refs.video
        video.srcObject = stream
        video.play()
        
        requestAnimationFrame(this.scan)
      } catch (error) {
        console.error('Error starting scanner:', error)
        this.$message.error('无法启动摄像头')
      }
    },
    
    scan() {
      if (!this.scanDialogVisible) {
        const video = this.$refs.video
        if (video && video.srcObject) {
          const tracks = video.srcObject.getTracks()
          tracks.forEach(track => track.stop())
        }
        return
      }
      
      const video = this.$refs.video
      const canvas = this.$refs.canvas
      const context = canvas.getContext('2d')
      
      if (video.readyState === video.HAVE_ENOUGH_DATA) {
        canvas.height = video.videoHeight
        canvas.width = video.videoWidth
        
        context.drawImage(video, 0, 0, canvas.width, canvas.height)
        const imageData = context.getImageData(0, 0, canvas.width, canvas.height)
        
        const code = jsQR(imageData.data, imageData.width, imageData.height)
        
        if (code) {
          // 假设二维码内容是批次号
          const batchNumber = code.data
          this.scanDialogVisible = false
          this.batchNumber = batchNumber
          this.handleSearch()
        }
      }
      
      requestAnimationFrame(this.scan)
    },
    getLogisticsIcon(type) {
      const icons = {
        storage: 'el-icon-box',
        delivery: 'el-icon-truck',
        transport: 'el-icon-location'
      }
      return icons[type] || 'el-icon-more'
    },
    getLogisticsDescription(record) {
      return `${record.from_location || '起点'} → ${record.to_location || '终点'}\n` +
        `时间: ${this.$options.filters.formatDateTime(record.created_at)}\n` +
        `操作员: ${record.operator_name}\n` +
        `状态: ${this.$options.filters.logisticsType(record.status)}`
    },
    formatRecordType(type) {
      const types = {
        'storage': '入库',
        'delivery': '出库',
        'transport': '运输中'
      }
      return types[type] || type
    },
    formatStatus(status) {
      const statuses = {
        'pending': '待处理',
        'processing': '处理中',
        'completed': '已完成'
      }
      return statuses[status] || status
    },
    getStatusType(status) {
      const types = {
        'pending': 'warning',
        'processing': 'primary',
        'completed': 'success'
      }
      return types[status] || 'info'
    },
    formatPaymentMethod(method) {
      const methods = {
        'cash': '现金',
        'wechat': '微信',
        'alipay': '支付宝',
        'card': '银行卡'
      }
      return methods[method] || method
    }
  }
}
</script>

<style scoped>
.trace-container {
  padding: 20px;
}
.search-section {
  margin-bottom: 30px;
}
.trace-card {
  margin-bottom: 20px;
}
.loading-container,
.empty-container {
  text-align: center;
  padding: 40px;
}
.empty-container i {
  font-size: 48px;
  color: #909399;
  margin-bottom: 20px;
}
.qr-scanner {
  text-align: center;
  padding: 20px;
}
.scanner-video {
  width: 100%;
  max-width: 300px;
  margin-bottom: 10px;
}
.loading {
  padding: 20px;
  text-align: center;
}
.el-timeline {
  margin-top: 20px;
}
.el-step__description {
  white-space: pre-line;
}
.suggestion-detail {
  font-size: 12px;
  color: #909399;
  margin-left: 10px;
}
.el-autocomplete {
  width: 300px;
}
</style> 