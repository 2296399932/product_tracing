<template>
  <div class="analysis-container">
    <!-- 筛选条件 -->
    <el-card class="filter-card">
      <el-form :inline="true" :model="filterForm">
        <el-form-item label="时间范围">
          <el-date-picker
            v-model="filterForm.dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            @change="handleFilter">
          </el-date-picker>
        </el-form-item>
        <el-form-item label="商品分类">
          <el-select v-model="filterForm.category" placeholder="请选择分类" @change="handleFilter">
            <el-option label="全部" value=""></el-option>
            <el-option
              v-for="item in categories"
              :key="item.id"
              :label="item.name"
              :value="item.id">
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleFilter">查询</el-button>
          <el-button @click="exportData">导出报告</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 销售分析 -->
    <el-card class="chart-card">
      <div slot="header">
        <span>销售分析</span>
        <el-radio-group v-model="salesType" size="small" style="margin-left: 20px">
          <el-radio-button label="amount">销售额</el-radio-button>
          <el-radio-button label="count">销量</el-radio-button>
        </el-radio-group>
      </div>
      <div class="chart-container">
        <div ref="salesChart" style="height: 400px"></div>
      </div>
    </el-card>

    <!-- 追溯分析 -->
    <el-row :gutter="20">
      <el-col :span="12">
        <el-card class="chart-card">
          <div slot="header">追溯链完整性分析</div>
          <div class="chart-container">
            <div ref="chainChart" style="height: 300px"></div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card class="chart-card">
          <div slot="header">追溯查询热点</div>
          <div class="chart-container">
            <div ref="hotspotChart" style="height: 300px"></div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 质量分析 -->
<!--    <el-row :gutter="20">-->
<!--      <el-col :span="12">-->
<!--        <el-card class="chart-card">-->
<!--          <div slot="header">质量问题分布</div>-->
<!--          <div class="chart-container">-->
<!--            <div ref="qualityChart" style="height: 300px"></div>-->
<!--          </div>-->
<!--        </el-card>-->
<!--      </el-col>-->
<!--      <el-col :span="12">-->
<!--        <el-card class="chart-card">-->
<!--          <div slot="header">问题处理时效</div>-->
<!--          <div class="chart-container">-->
<!--            <div ref="timelinessChart" style="height: 300px"></div>-->
<!--          </div>-->
<!--        </el-card>-->
<!--      </el-col>-->
<!--    </el-row>-->


  </div>
</template>

<script>
import * as echarts from 'echarts'

export default {
  name: 'Analysis',
  data() {
    return {
      filterForm: {
        dateRange: [],
        category: ''
      },
      salesType: 'amount',
      categories: [],
      charts: {
        sales: null,
        chain: null,
        hotspot: null
      }
    }
  },
  mounted() {
    this.initCharts()
    this.fetchCategories()
    this.fetchData()
  },
  beforeDestroy() {
    // 销毁图表实例
    Object.values(this.charts).forEach(chart => {
      if (chart) {
        chart.dispose()
      }
    })
  },
  methods: {
    initCharts() {
      // 初始化所有图表
      this.charts.sales = echarts.init(this.$refs.salesChart)
      this.charts.chain = echarts.init(this.$refs.chainChart)
      this.charts.hotspot = echarts.init(this.$refs.hotspotChart)



      // 监听窗口大小变化
      window.addEventListener('resize', this.handleResize)
    },
    handleResize() {
      // 重置所有图表大小
      Object.values(this.charts).forEach(chart => {
        if (chart) {
          chart.resize()
        }
      })
    },
    fetchCategories() {
      this.$axios.get(this.$httpUrl + '/api/products/categories/')
        .then(res => {
          this.categories = res.data
        })
        .catch(err => {
          console.error('获取分类列表失败:', err)
          this.$message.error('获取分类列表失败')
        })
    },
    handleFilter() {
      this.fetchData()
    },
    exportData() {
      const params = {
        date_from: this.filterForm.dateRange?.[0],
        date_to: this.filterForm.dateRange?.[1],
        category: this.filterForm.category,
        type: this.salesType
      }
      
      this.$axios.get(this.$httpUrl + '/api/analysis/export/', { 
        params,
        responseType: 'blob'
      })
        .then(res => {
          const url = window.URL.createObjectURL(new Blob([res.data]))
          const link = document.createElement('a')
          link.href = url
          link.setAttribute('download', '数据分析报告.xlsx')
          document.body.appendChild(link)
          link.click()
          document.body.removeChild(link)
        })
        .catch(err => {
          console.error('导出报告失败:', err)
          this.$message.error('导出报告失败')
        })
    },
    fetchData() {
      const params = {
        date_from: this.filterForm.dateRange?.[0],
        date_to: this.filterForm.dateRange?.[1],
        category: this.filterForm.category
      }
      
      // 获取销售分析数据
      this.$axios.get(this.$httpUrl + '/api/analysis/sales/', { 
        params: { ...params, type: this.salesType }
      })
        .then(res => {
          this.updateSalesChart(res.data)
        })
        .catch(err => {
          console.error('获取销售分析失败:', err)
          this.$message.error('获取销售分析数据失败')
        })

      // 获取追溯分析数据
      this.$axios.get(this.$httpUrl + '/api/analysis/tracing/', { params })
        .then(res => {
          this.updateChainChart(res.data.chain)
          this.updateHotspotChart(res.data.hotspot)
        })
        .catch(err => {
          console.error('获取追溯分析失败:', err)
          this.$message.error('获取追溯分析数据失败')
        })
    },
    updateSalesChart(data) {
      const option = {
        title: { text: '销售趋势' },
        tooltip: { trigger: 'axis' },
        xAxis: {
          type: 'category',
          data: data.trend.map(item => item.sale_date__date)
        },
        yAxis: { type: 'value' },
        series: [{
          name: this.salesType === 'amount' ? '销售额' : '销量',
          type: 'line',
          data: data.trend.map(item => this.salesType === 'amount' ? item.amount : item.count)
        }]
      }
      this.charts.sales.setOption(option)
    },
    updateChainChart(data) {
      const option = {
        title: { text: '追溯链完整性' },
        tooltip: { trigger: 'item' },
        series: [{
          type: 'pie',
          radius: '60%',
          data: [
            { value: data.complete_chain, name: '完整链' },
            { value: data.total - data.complete_chain, name: '不完整链' }
          ]
        }]
      }
      this.charts.chain.setOption(option)
    },
    updateHotspotChart(data) {
      const option = {
        title: { text: '追溯查询热点' },
        tooltip: { trigger: 'axis' },
        xAxis: {
          type: 'category',
          data: data.map(item => item.product__name)
        },
        yAxis: { type: 'value' },
        series: [{
          type: 'bar',
          data: data.map(item => item.count)
        }]
      }
      this.charts.hotspot.setOption(option)
    },

  },
  watch: {
    salesType() {
      this.fetchData()
    }
  }
}
</script>

<style scoped>
.analysis-container {
  padding: 20px;
}
.filter-card {
  margin-bottom: 20px;
}
.chart-card {
  margin-bottom: 20px;
}
.chart-container {
  padding: 10px;
  height: 100%;
  min-height: 300px;
}
.table-card {
  margin-bottom: 20px;
}
.pagination-container {
  margin-top: 20px;
  text-align: right;
}
</style> 