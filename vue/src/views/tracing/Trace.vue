<template>
  <div class="trace-container">
    <!-- 搜索区域 -->
    <div class="search-section">
      <div class="title-area">
        <h1>产品溯源查询</h1>
        <p class="subtitle">透明、可信、全程可追溯</p>
      </div>
      
      <el-form :inline="true" class="search-form">
        <el-form-item>
          <el-input
            v-model="batchNumber"
            placeholder="请输入批次号"
            prefix-icon="el-icon-search"
            clearable
            class="search-input">
            <el-button slot="append" type="primary" @click="handleSearch" :loading="loading">查询</el-button>
          </el-input>
        </el-form-item>
        <el-form-item>
          <el-button type="info" icon="el-icon-camera" @click="handleScan">扫码查询</el-button>
        </el-form-item>
      </el-form>
      
      <div class="help-text">
        <p>输入产品包装上的批次号或扫描二维码,即可查询产品全链路信息</p>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-container">
      <el-card shadow="hover">
        <div class="loading-animation">
          <i class="el-icon-loading"></i>
          <p>正在加载追溯信息...</p>
        </div>
      </el-card>
    </div>

    <!-- 无数据提示 -->
    <div v-else-if="!traceData && !loading" class="empty-container">
      <el-card shadow="hover">
        <div class="empty-content">
          <i class="el-icon-search empty-icon"></i>
          <h3>暂无追溯数据</h3>
          <p>请输入有效的批次号或扫描产品二维码</p>
        </div>
      </el-card>
    </div>

    <!-- 追溯信息显示 -->
    <div v-else-if="traceData" class="trace-content">
      <!-- 产品基本信息卡片 -->
      <el-card class="trace-card product-card" shadow="hover">
        <div slot="header" class="card-header">
          <i class="el-icon-goods"></i>
          <span>产品基本信息</span>
        </div>
        
        <div class="product-info">
          <div class="product-image">
            <el-image 
              :src="traceData.product_details?.image_url || defaultImage"
              :preview-src-list="traceData.product_details?.image_url ? [traceData.product_details.image_url] : []"
              fit="cover">
              <div slot="error" class="image-slot">
                <i class="el-icon-picture-outline"></i>
              </div>
            </el-image>
          </div>
          
          <div class="product-details">
            <h2>{{ traceData.product?.name || '暂无产品名称' }}</h2>
            <div class="detail-grid">
              <div class="detail-item">
                <label>批次号</label>
                <span>{{ traceData.batch || traceData.batch_number }}</span>
              </div>
              <div class="detail-item">
                <label>生产日期</label>
                <span>{{ (traceData.production_date || getFirstProductionDate()) | formatDate }}</span>
              </div>
              <div class="detail-item">
                <label>有效期至</label>
                <span>{{ traceData.expiry_date | formatDate }}</span>
              </div>
              <div class="detail-item">
                <label>产品规格</label>
                <div v-if="formattedSpecifications.length > 0" class="specifications-list">
                  <div v-for="(spec, index) in formattedSpecifications" :key="index" class="spec-item">
                    <span class="spec-key">{{ spec.key }}:</span> {{ spec.value }}
                  </div>
                </div>
                <span v-else>{{ traceData.product?.specifications || '暂无数据' }}</span>
              </div>
              <div class="detail-item">
                <label>生产员</label>
                <span>{{ traceData.product?.manufacturer_name || traceData.manufacturer || '暂无数据' }}</span>
              </div>
              <div class="detail-item">
                <label>状态</label>
                <el-tag :type="getStatusType(traceData.status)">{{ getStatusText(traceData.status) }}</el-tag>
              </div>
            </div>
          </div>
        </div>
      </el-card>

      <!-- 生产记录卡片 -->
      <el-card v-if="traceData.production_records?.length" class="trace-card" shadow="hover">
        <div slot="header" class="card-header">
          <i class="el-icon-s-operation"></i>
          <span>生产记录</span>
        </div>
        
        <el-timeline>
          <el-timeline-item
            v-for="(record, index) in traceData.production_records"
            :key="index"
            :timestamp="record.production_date | formatDateTime"
            :icon="getProductionIcon(record)"
            :type="getProductionType(record)">
            <el-card class="timeline-card">
              <h4>生产线: {{ record.production_line }}</h4>
              <div class="timeline-detail">
                <span><i class="el-icon-user"></i> 操作员: {{ record.operator_name || '未记录' }}</span>
                <span><i class="el-icon-temperature"></i> 环境温度: {{ record.temperature || 0 }}°C</span>
                <span><i class="el-icon-umbrella"></i> 环境湿度: {{ record.humidity || 0 }}%</span>
              </div>
              
              <div v-if="record.quality_check?.length" class="quality-check">
                <h4><i class="el-icon-check"></i> 质检记录:</h4>
                <el-table :data="record.quality_check" border stripe size="small">
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

      <!-- 物流记录卡片 -->
      <el-card v-if="traceData.logistics_records?.length" class="trace-card" shadow="hover">
        <div slot="header" class="card-header">
          <i class="el-icon-truck"></i>
          <span>物流记录</span>
        </div>
        
        <el-steps :active="traceData.logistics_records.length" direction="vertical" align-center>
          <el-step 
            v-for="(record, index) in traceData.logistics_records" 
            :key="index"
            :icon="getLogisticsIcon(record.record_type)"
            :title="formatRecordType(record.record_type)"
            :description="getLogisticsDescription(record)">
          </el-step>
        </el-steps>
      </el-card>

      <!-- 销售信息卡片 -->
      <el-card v-if="traceData.sales_record" class="trace-card" shadow="hover">
        <div slot="header" class="card-header">
          <i class="el-icon-shopping-cart-full"></i>
          <span>销售信息</span>
        </div>
        
        <div class="sales-info">
          <div class="sales-grid">
            <div class="sales-item">
              <label>销售日期</label>
              <span>{{ traceData.sales_record.sale_date | formatDateTime }}</span>
            </div>
            <div class="sales-item">
              <label>销售数量</label>
              <span>{{ traceData.sales_record.quantity }}</span>
            </div>
            <div class="sales-item">
              <label>销售单价</label>
              <span>¥{{ traceData.sales_record.unit_price }}</span>
            </div>
            <div class="sales-item">
              <label>销售金额</label>
              <span>¥{{ traceData.sales_record.total_amount }}</span>
            </div>
            <div class="sales-item">
              <label>支付方式</label>
              <span>{{ formatPaymentMethod(traceData.sales_record.payment_method) }}</span>
            </div>
            <div class="sales-item">
              <label>交易编号</label>
              <span class="transaction-id">{{ traceData.sales_record.transaction_id }}</span>
            </div>
          </div>
        </div>
      </el-card>
      
      <!-- 分享按钮 -->
      <div class="share-container">
        <el-button type="primary" icon="el-icon-share" @click="shareTrace">分享溯源信息</el-button>
        <el-button type="success" icon="el-icon-download" @click="downloadQRCode">下载溯源码</el-button>
      </div>
    </div>

    <!-- 扫码对话框 -->
    <el-dialog title="扫描二维码" :visible.sync="scanDialogVisible" width="350px" center>
      <div class="qr-scanner">
        <div v-if="scannerLoading" class="scanner-loading">
          <i class="el-icon-loading"></i>
          <p>正在启动相机...</p>
        </div>
        <div v-else class="scanner-content">
          <video ref="video" class="scanner-video"></video>
          <canvas ref="canvas" style="display: none;"></canvas>
          <div class="scanner-guide">
            <div class="scanner-frame"></div>
          </div>
          <p class="scanner-tip">请将二维码对准框内</p>
        </div>
      </div>
    </el-dialog>
    
    <!-- 分享对话框 -->
    <el-dialog title="分享溯源信息" :visible.sync="shareDialogVisible" width="300px" center>
      <div class="share-content">
        <div v-if="qrcodeUrl" class="qrcode-container">
          <img :src="qrcodeUrl" alt="溯源二维码" class="qrcode-image">
          <p>扫描上方二维码查看溯源信息</p>
        </div>
        <div v-else class="qrcode-loading">
          <i class="el-icon-loading"></i>
          <p>正在生成二维码...</p>
        </div>
        
        <div class="share-actions">
          <el-button type="primary" icon="el-icon-copy-document" @click="copyTraceUrl">复制链接</el-button>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import jsQR from 'jsqr'

export default {
  name: 'Trace',
  filters: {
    formatDate(value) {
      if (!value) return '未设置'
      return new Date(value).toLocaleDateString()
    },
    formatDateTime(value) {
      if (!value) return '未设置'
      const date = new Date(value)
      return `${date.toLocaleDateString()} ${date.toLocaleTimeString()}`
    }
  },
  data() {
    return {
      batchNumber: '',
      traceData: null,
      loading: false,
      scanDialogVisible: false,
      scannerLoading: false,
      shareDialogVisible: false,
      qrcodeUrl: null,
      defaultImage: require('@/assets/img/bo.jpg')
    }
  },
  created() {
    // 从URL参数获取批次号
    const batchNumber = this.$route.params.batchNumber || this.$route.query.batch
    if (batchNumber) {
      this.batchNumber = batchNumber
      this.handleSearch()
    }
  },
  computed: {
    formattedSpecifications() {
      const specs = this.traceData?.product?.specifications;
      if (!specs) return [];
      
      try {
        // 尝试解析字符串形式的JSON
        let specsObj = specs;
        if (typeof specs === 'string') {
          specsObj = JSON.parse(specs);
        }
        
        // 如果不是对象，返回空数组
        if (typeof specsObj !== 'object' || specsObj === null) {
          return [];
        }
        
        // 转换为键值对数组并格式化键名
        return Object.entries(specsObj).map(([key, value]) => ({
          key: this.formatSpecKey(key),
          value: value
        }));
      } catch (error) {
        console.error('解析产品规格失败:', error);
        return [];
      }
    }
  },
  methods: {
    handleSearch() {
      if (!this.batchNumber) {
        this.$message.warning('请输入批次号')
        return
      }
      
      this.loading = true
      this.traceData = null
      
      // 使用与TraceDetail相同的接口
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
      this.scannerLoading = true
      
      this.$nextTick(() => {
        this.startScanner()
      })
    },
    async startScanner() {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ 
          video: { facingMode: 'environment' }
        })
        const video = this.$refs.video
        video.srcObject = stream
        video.play()
        
        this.scannerLoading = false
        
        requestAnimationFrame(this.scan)
      } catch (error) {
        console.error('Error starting scanner:', error)
        this.$message.error('无法启动摄像头，请确保已授予相机权限')
        this.scannerLoading = false
        this.scanDialogVisible = false
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
      if (!video || !canvas) return

      if (video.readyState === video.HAVE_ENOUGH_DATA) {
        canvas.height = video.videoHeight
        canvas.width = video.videoWidth
        
        const context = canvas.getContext('2d')
        context.drawImage(video, 0, 0, canvas.width, canvas.height)
        const imageData = context.getImageData(0, 0, canvas.width, canvas.height)
        
        const code = jsQR(imageData.data, imageData.width, imageData.height)
        
        if (code) {
          // 尝试从二维码内容提取批次号 - 不同格式处理
          const directBatchNumber = code.data.match(/^[A-Z][0-9]{10,}$/); // 直接是批次号
          const batchNumberMatch = code.data.match(/https?:\/\/.*\/trace\/([A-Z0-9]+)/i); // 链接格式
          
          if (directBatchNumber) {
            this.batchNumber = code.data;
          } else if (batchNumberMatch && batchNumberMatch[1]) {
            this.batchNumber = batchNumberMatch[1];
          } else {
            this.batchNumber = code.data; // 默认使用完整内容
          }
          
          this.scanDialogVisible = false;
          this.handleSearch();
        }
      }
      
      requestAnimationFrame(this.scan)
    },
    getLogisticsIcon(type) {
      const icons = {
        'storage': 'el-icon-box',
        'inbound': 'el-icon-box',
        'delivery': 'el-icon-truck',
        'outbound': 'el-icon-truck',
        'transport': 'el-icon-location',
        'delayed': 'el-icon-time'
      }
      return icons[type] || 'el-icon-more'
    },
    getProductionIcon() {
      return 'el-icon-s-operation'
    },
    getProductionType() {
      return 'primary'
    },
    getLogisticsDescription(record) {
      const status = this.formatRecordType(record.status || 'pending');
      const time = this.$options.filters.formatDateTime(record.operation_time || record.created_at);
      
      return `${record.from_location || '起点'} → ${record.to_location || '终点'}\n` +
        `时间: ${time}\n` +
        `操作员: ${record.operator_name || '未记录'}\n` +
        `状态: ${status}`;
    },
    formatRecordType(type) {
      const types = {
        'storage': '入库',
        'inbound': '入库',
        'delivery': '出库',
        'outbound': '出库',
        'transport': '运输中',
        'delayed': '延迟',
        'completed': '已完成'
      };
      return types[type] || type;
    },
    formatStatus(status) {
      const statuses = {
        'pending': '待处理',
        'processing': '处理中',
        'completed': '已完成',
        'active': '活跃',
        'inactive': '停用',
        'in_storage': '在库',
        'sold': '已售出',
        'produced': '已生产',
        'out_storage': '已出库'
      };
      return statuses[status] || status;
    },
    getStatusText(status) {
      if (!status) return '未知';
      
      const statuses = {
        'pending': '待处理',
        'processing': '处理中',
        'completed': '已完成',
        'active': '活跃',
        'inactive': '停用',
        'in_storage': '在库',
        'sold': '已售出',
        'produced': '已生产',
        'out_storage': '已出库',
        'outbound': '已出库',
        'delayed': '延迟',
        'delivered': '已送达'
      };
      return statuses[status] || status;
    },
    getStatusType(status) {
      const types = {
        'pending': 'warning',
        'processing': 'primary',
        'completed': 'success',
        'active': 'success',
        'inactive': 'info',
        'in_storage': 'primary',
        'sold': 'success'
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
    },
    shareTrace() {
      this.shareDialogVisible = true
      this.qrcodeUrl = null
      
      // 获取溯源二维码
      this.$axios.get(this.$httpUrl + `/api/tracing/qrcode/${this.batchNumber}/`)
        .then(res => {
          this.qrcodeUrl = res.data.qrcode_url
        })
        .catch(err => {
          console.error('获取二维码失败:', err)
          this.$message.error('获取二维码失败')
        })
    },
    copyTraceUrl() {
      // 构建完整的追溯链接，但不更新当前页面URL
      const baseUrl = `${window.location.origin}${window.location.pathname}`
      const traceUrl = `${baseUrl}#/trace/${this.batchNumber}`
      
      navigator.clipboard.writeText(traceUrl)
        .then(() => {
          this.$message.success('链接已复制到剪贴板')
        })
        .catch(err => {
          console.error('复制失败:', err)
          this.$message.error('复制失败，请手动复制')
        })
    },
    downloadQRCode() {
      if (!this.qrcodeUrl) {
        this.shareTrace()
        setTimeout(this.downloadQRCodeImage, 1000)
      } else {
        this.downloadQRCodeImage()
      }
    },
    downloadQRCodeImage() {
      if (!this.qrcodeUrl) {
        this.$message.error('二维码尚未生成，请稍后再试')
        return
      }

      const link = document.createElement('a')
      link.href = this.qrcodeUrl
      link.download = `追溯码_${this.batchNumber}.png`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
    },
    // 格式化产品规格的键名
    formatSpecKey(key) {
      // 将下划线和驼峰命名转换为空格分隔的词组，并首字母大写
      return key
        .replace(/_/g, ' ')                           // 将下划线替换为空格
        .replace(/([A-Z])/g, ' $1')                   // 在大写字母前添加空格
        .replace(/^./, str => str.toUpperCase())      // 首字母大写
        .trim()                                        // 去除多余空格
    },
    // 获取第一条生产记录的日期作为生产日期
    getFirstProductionDate() {
      if (this.traceData?.production_records?.length > 0) {
        return this.traceData.production_records[0].production_date;
      }
      return null;
    }
  }
}
</script>

<style scoped>
.trace-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  background-color: #f5f7fa;
  min-height: 100vh;
}

.search-section {
  margin-bottom: 30px;
  text-align: center;
  padding: 30px 20px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.title-area {
  margin-bottom: 20px;
}

.title-area h1 {
  font-size: 32px;
  color: #409EFF;
  margin-bottom: 10px;
}

.subtitle {
  font-size: 16px;
  color: #606266;
  margin-bottom: 20px;
}

.search-form {
  display: flex;
  justify-content: center;
  margin-bottom: 15px;
}

.search-input {
  width: 400px;
}

.help-text {
  color: #909399;
  font-size: 14px;
}

.trace-card {
  margin-bottom: 30px;
  border-radius: 8px;
  overflow: hidden;
}

.card-header {
  display: flex;
  align-items: center;
}

.card-header i {
  margin-right: 8px;
  font-size: 18px;
}

.loading-container, .empty-container {
  text-align: center;
  padding: 40px;
}

.loading-animation, .empty-content {
  padding: 40px;
}

.loading-animation i, .empty-icon {
  font-size: 48px;
  color: #409EFF;
  margin-bottom: 20px;
}

.empty-icon {
  color: #909399;
}

.product-card {
  background-color: #fff;
}

.product-info {
  display: flex;
  flex-wrap: wrap;
}

.product-image {
  width: 200px;
  margin-right: 30px;
  margin-bottom: 20px;
}

.product-image .el-image {
  width: 100%;
  height: 200px;
  border-radius: 4px;
  overflow: hidden;
}

.product-details {
  flex: 1;
  min-width: 300px;
}

.product-details h2 {
  margin-top: 0;
  margin-bottom: 20px;
  color: #303133;
}

.detail-grid, .sales-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 20px;
}

.detail-item, .sales-item {
  display: flex;
  flex-direction: column;
}

.detail-item label, .sales-item label {
  font-size: 14px;
  color: #909399;
  margin-bottom: 5px;
}

.detail-item span, .sales-item span {
  font-size: 16px;
  color: #303133;
}

.timeline-card {
  margin-bottom: 10px;
}

.timeline-detail {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  margin: 10px 0;
}

.timeline-detail span {
  display: flex;
  align-items: center;
}

.timeline-detail i {
  margin-right: 5px;
}

.quality-check {
  margin-top: 15px;
}

.quality-check h4 {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
}

.quality-check i {
  margin-right: 5px;
}

.share-container {
  display: flex;
  justify-content: center;
  margin-top: 30px;
  gap: 20px;
}

.qr-scanner {
  text-align: center;
}

.scanner-video {
  width: 100%;
  max-width: 300px;
  margin-bottom: 10px;
  border-radius: 4px;
}

.scanner-guide {
  position: relative;
  width: 100%;
  max-width: 300px;
  height: 200px;
  margin: 0 auto;
}

.scanner-frame {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 200px;
  height: 200px;
  border: 2px solid #409EFF;
  border-radius: 10px;
}

.scanner-tip {
  margin-top: 15px;
  color: #606266;
}

.scanner-loading, .qrcode-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 30px;
}

.scanner-loading i, .qrcode-loading i {
  font-size: 24px;
  color: #409EFF;
  margin-bottom: 10px;
}

.qrcode-container {
  text-align: center;
  padding: 20px;
}

.qrcode-image {
  width: 200px;
  height: 200px;
  margin-bottom: 15px;
}

.share-actions {
  margin-top: 20px;
  text-align: center;
}

.transaction-id {
  word-break: break-all;
}

@media (max-width: 768px) {
  .search-input {
    width: 250px;
  }
  
  .product-image {
    width: 100%;
    margin-right: 0;
  }
  
  .detail-grid, .sales-grid {
    grid-template-columns: 1fr;
  }
}

/* 添加产品规格样式 */
.spec-item {
  margin-bottom: 5px;
  font-size: 14px;
}

.spec-key {
  font-weight: 500;
  color: #606266;
}

.specifications-list {
  display: flex;
  flex-direction: column;
  gap: 5px;
}
</style> 