<template>
  <div class="trace-detail">
    <div v-if="error" class="error-message">
      {{ error }}
      <div class="retry-button" @click="retry">
        <button class="btn">重试</button>
      </div>
    </div>
    
    <div v-else-if="loading" class="loading">
      <p>加载中...</p>
    </div>
    
    <div v-else-if="traceData" class="trace-content">
      <h2>产品追溯信息</h2>
      
      <!-- 批次信息 -->
      <div class="section">
        <h3>批次信息</h3>
        <p>批次号：{{ $route.params.batchNumber }}</p>
        <p v-if="traceData.production_date">生产日期：{{ traceData.production_date }}</p>
        <p v-if="traceData.expiry_date">过期日期：{{ traceData.expiry_date }}</p>
      </div>

      <!-- 产品信息 -->
      <div class="section" v-if="traceData.product">
        <h3>产品信息</h3>
        <p>产品名称：{{ traceData.product.name }}</p>
        <p>规格：{{ traceData.product.specifications }}</p>
        <p>生产商：{{ traceData.product.manufacturer_name }}</p>
      </div>

      <!-- 生产记录 -->
      <div class="section" v-if="traceData.production_records && traceData.production_records.length">
        <h3>生产记录</h3>
        <div v-for="record in traceData.production_records" :key="record.production_date">
          <p>生产日期：{{ record.production_date }}</p>
          <p>生产线：{{ record.production_line }}</p>
          <p>操作员：{{ record.operator_name }}</p>
        </div>
      </div>

      <!-- 物流记录 -->
      <div class="section" v-if="traceData.logistics_records && traceData.logistics_records.length">
        <h3>物流记录</h3>
        <div v-for="record in traceData.logistics_records" :key="record.operation_time">
          <p>操作类型：{{ record.record_type }}</p>
          <p>从：{{ record.from_location }}</p>
          <p>到：{{ record.to_location }}</p>
          <p>状态：{{ record.status }}</p>
        </div>
      </div>

      <!-- 销售记录 -->
      <div class="section" v-if="traceData.sales_record">
        <h3>销售信息</h3>
        <p>销售日期：{{ traceData.sales_record.sale_date }}</p>
        <p>销售数量：{{ traceData.sales_record.quantity }}</p>
        <p>销售员：{{ traceData.sales_record.seller_name }}</p>
      </div>

      <!-- 原材料信息 -->
      <div class="section" v-if="traceData.materials && traceData.materials.length">
        <h3>原材料信息</h3>
        <p>原材料数量: {{ traceData.materials.length }}</p>
        
        <div v-for="material in traceData.materials" :key="material.batch_number" class="material-item">
          <p>名称：{{ material.name }}</p>
          <p>批次号：{{ material.batch_number }}</p>
          <p>用量：{{ material.quantity }} {{ material.unit }}</p>
          <p>供应商：{{ material.supplier || '未知' }}</p>
          <p>生产日期：{{ material.production_date }}</p>
          <p>有效期至：{{ material.expiry_date }}</p>
        </div>
      </div>
    </div>
    
    <div v-else class="no-data">
      <p>未找到相关追溯信息</p>
    </div>
  </div>
</template>

<script>
export default {
  name: 'TraceDetail',
  data() {
    return {
      loading: true,
      traceData: null,
      error: null,
      retryCount: 0,
      maxRetries: 3
    }
  },
  created() {
    this.fetchTraceData()
  },
  methods: {
    fetchTraceData() {
      const batchNumber = this.$route.params.batchNumber
      this.loading = true
      this.error = null
      
      console.log('Fetching trace data for batch:', batchNumber)
      console.log('API URL:', `${this.$httpUrl}/api/tracing/trace/${batchNumber}/`)
      
      this.$axios.get(`${this.$httpUrl}/api/tracing/trace/${batchNumber}/`)
        .then(response => {
          console.log('Trace data received:', response.data)
          this.traceData = response.data
          this.loading = false
        })
        .catch(error => {
          console.error('Error fetching trace data:', error)
          console.error('Error details:', error.response ? error.response.data : 'No response')
          console.error('Status:', error.response ? error.response.status : 'Unknown')
          
          // 增加重试逻辑
          if (this.retryCount < this.maxRetries) {
            this.retryCount++
            console.log(`Retry attempt ${this.retryCount} of ${this.maxRetries}...`)
            setTimeout(() => {
              this.fetchTraceData()
            }, 1000) // 1秒后重试
            return
          }
          
          this.error = `获取追溯数据失败：${error.response && error.response.data ? error.response.data.error : '请检查网络连接'}`
          this.loading = false
        })
    },
    
    retry() {
      this.retryCount = 0
      this.fetchTraceData()
    }
  }
}
</script>

<style scoped>
.trace-detail {
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
}

.error-message {
  color: #f56c6c;
  text-align: center;
  padding: 20px;
  background-color: #fef0f0;
  border-radius: 4px;
  margin-bottom: 20px;
}

.loading {
  text-align: center;
  padding: 20px;
}

.section {
  margin-bottom: 20px;
  padding: 15px;
  border: 1px solid #eee;
  border-radius: 5px;
  background-color: #fff;
}

.section h3 {
  margin-top: 0;
  color: #333;
  border-bottom: 1px solid #eee;
  padding-bottom: 10px;
}

.no-data {
  text-align: center;
  color: #909399;
  padding: 20px;
}

.material-item {
  border-bottom: 1px solid #eee;
  padding: 10px 0;
}

.material-item:last-child {
  border-bottom: none;
}

.retry-button {
  margin-top: 15px;
  text-align: center;
}

.btn {
  padding: 8px 16px;
  background-color: #409EFF;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}
</style> 