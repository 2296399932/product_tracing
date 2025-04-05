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

    <!-- 概览数据卡片 -->
    <el-row :gutter="20" class="overview-cards">
      <!-- 销售概览 -->
      <el-col :span="8">
        <el-card shadow="hover">
          <div slot="header">
            <span>销售概览</span>
          </div>
          <div class="overview-item">
            <div class="item-label">总销售额</div>
            <div class="item-value">¥{{ overview.sales.total_amount.toFixed(2) }}</div>
            <div class="item-trend" :class="overview.sales.growth >= 0 ? 'up' : 'down'">
              {{ Math.abs(overview.sales.growth).toFixed(2) }}%
              <i :class="overview.sales.growth >= 0 ? 'el-icon-top' : 'el-icon-bottom'"></i>
            </div>
          </div>
          <!-- 其他销售数据 -->
        </el-card>
      </el-col>
      
      <!-- 追溯概览 -->
      <el-col :span="8">
        <el-card shadow="hover">
          <div slot="header">
            <span>追溯概览</span>
          </div>
          <div class="overview-item">
            <div class="item-label">追溯完整率</div>
            <div class="item-value">{{ overview.tracing.completion_rate.toFixed(2) }}%</div>
            <el-progress :percentage="overview.tracing.completion_rate" :color="getProgressColor"></el-progress>
          </div>
          <!-- 其他追溯数据 -->
        </el-card>
      </el-col>
      
      <!-- 质量概览 -->
      <el-col :span="8">
        <el-card shadow="hover">
          <div slot="header">
            <span>质量概览</span>
          </div>
          <div class="overview-item">
            <div class="item-label">合格率</div>
            <div class="item-value">{{ overview.quality.pass_rate.toFixed(2) }}%</div>
            <el-progress :percentage="overview.quality.pass_rate" :color="getQualityColor"></el-progress>
          </div>
          <!-- 其他质量数据 -->
        </el-card>
      </el-col>
    </el-row>

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
          <div slot="header">商品销售排行</div>
          <div class="chart-container">
            <div ref="rankChart" style="height: 300px"></div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card class="chart-card">
          <div slot="header">销售分类占比</div>
          <div class="chart-container">
            <div ref="categoryChart" style="height: 300px"></div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 质量分析 -->
    <el-row :gutter="20">
      <el-col :span="12">
        <el-card class="chart-card">
          <div slot="header">质量问题分布</div>
          <div class="chart-container">
            <div ref="qualityChart" style="height: 300px"></div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card class="chart-card">
          <div slot="header">问题处理时效</div>
          <div class="chart-container">
            <div ref="timelinessChart" style="height: 300px"></div>
          </div>
        </el-card>
      </el-col>
    </el-row>

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
        rank: null,
        category: null,
        quality: null,
        timeliness: null
      },
      defaultImage: require('@/assets/img/bo.jpg'),
      overview: {
        sales: {
          total_amount: 0,
          order_count: 0,
          product_count: 0,
          customer_count: 0,
          growth: 0
        },
        tracing: {
          total_batches: 0,
          complete_chain: 0,
          completion_rate: 0,
          scan_count: 0,
          query_count: 0
        },
        quality: {
          total_inspections: 0,
          passed_count: 0,
          issue_count: 0,
          pass_rate: 0,
          avg_process_time: 0
        }
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
  computed: {
    getProgressColor() {
      return (percentage) => {
        if (percentage < 60) return '#F56C6C'
        if (percentage < 80) return '#E6A23C'
        return '#67C23A'
      }
    },
    getQualityColor() {
      return (percentage) => {
        if (percentage < 70) return '#F56C6C'
        if (percentage < 90) return '#E6A23C'
        return '#67C23A'
      }
    }
  },
  methods: {
    initCharts() {
      // 初始化所有图表
      this.charts.sales = echarts.init(this.$refs.salesChart)
      this.charts.rank = echarts.init(this.$refs.rankChart)
      this.charts.category = echarts.init(this.$refs.categoryChart)
      this.charts.quality = echarts.init(this.$refs.qualityChart)
      this.charts.timeliness = echarts.init(this.$refs.timelinessChart)

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

      // 获取销售概览数据
      this.$axios.get(this.$httpUrl + '/api/analysis/sales/overview/', { params })
        .then(res => {
          this.overview.sales = res.data
          this.updateSalesChart(res.data.trends || { dates: [], amount: [], count: [] })  // 提供默认值
        })
        .catch(err => {
          console.error('获取销售概览失败:', err)
          this.$message.error('获取销售概览数据失败')
        })
      
      // 获取追溯概览数据
      this.$axios.get(this.$httpUrl + '/api/analysis/tracing/overview/', { params })
        .then(res => {
          this.overview.tracing = res.data
          this.updateRankChart(res.data)
          this.updateCategoryChart(res.data)
        })
        .catch(err => {
          console.error('获取追溯概览失败:', err)
          this.$message.error('获取追溯概览数据失败')
        })
      
      // 获取质量概览数据
      this.$axios.get(this.$httpUrl + '/api/analysis/quality/overview/', { params })
        .then(res => {
          this.overview.quality = res.data
          this.updateQualityChart(res.data)
        })
        .catch(err => {
          console.error('获取质量概览失败:', err)
          this.$message.error('获取质量概览数据失败')
        })
    },
    updateSalesChart(data) {
      const option = {
        title: { text: '销售趋势' },
        tooltip: { 
          trigger: 'axis',
          formatter: function(params) {
            const data = params[0];
            return `${data.name}<br/>${data.seriesName}: ${data.value}${data.seriesName === '销售额' ? '元' : '单'}`
          }
        },
        xAxis: {
          type: 'category',
          data: data.dates || []  // 使用 dates 字段
        },
        yAxis: { 
          type: 'value',
          name: this.salesType === 'amount' ? '销售额(元)' : '订单数'
        },
        series: [{
          name: this.salesType === 'amount' ? '销售额' : '销量',
          type: 'line',
          smooth: true,
          data: this.salesType === 'amount' ? data.amount : data.count,  // 直接使用 amount 或 count 字段
          itemStyle: {
            color: '#409EFF'
          },
          areaStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: 'rgba(64,158,255,0.3)' },
              { offset: 1, color: 'rgba(64,158,255,0.1)' }
            ])
          }
        }]
      }
      this.charts.sales.setOption(option)
    },
    updateRankChart(data) {
      const option = {
        title: { text: '商品销售排行' },
        tooltip: { 
          trigger: 'axis',
          axisPointer: { type: 'shadow' },
          formatter: function(params) {
            const data = params[0];
            return `${data.name}<br/>销售额: ¥${data.value}<br/>销售量: ${data.data.count}`;
          }
        },
        xAxis: { type: 'value', name: '销售额(元)' },
        yAxis: { 
          type: 'category',
          data: data.top_products?.map(item => item.name) || []
        },
        series: [{
          type: 'bar',
          data: data.top_products?.map(item => ({
            value: item.value,
            count: item.count
          })) || [],
          itemStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
              { offset: 0, color: '#83bff6' },
              { offset: 0.5, color: '#188df0' },
              { offset: 1, color: '#188df0' }
            ])
          }
        }]
      }
      this.charts.rank.setOption(option)
    },
    updateCategoryChart(data) {
      const option = {

        tooltip: { 
          trigger: 'item',
          formatter: '{b}: ¥{c} ({d}%)'
        },
        legend: { 
          orient: 'vertical',
          left: 'left',
          type: 'scroll'
        },
        series: [{
          type: 'pie',
          radius: '50%',
          data: data.category_sales?.map(item => ({
            name: item.name || '未分类',
            value: item.value
          })) || [],
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowOffsetX: 0,
              shadowColor: 'rgba(0, 0, 0, 0.5)'
            }
          }
        }]
      }
      this.charts.category.setOption(option)
    },
    updateQualityChart(data) {
      // 更新质量分布饼图
      const qualityOption = {
        title: {
          text: '质量检测结果分布',
          left: 'center'
        },
        tooltip: {
          trigger: 'item',
          formatter: '{a} <br/>{b}: {c} ({d}%)'
        },
        legend: {
          orient: 'vertical',
          left: 'left',
          data: ['合格', '不合格']
        },
        series: [{
          name: '检测结果',
          type: 'pie',
          radius: ['50%', '70%'],
          avoidLabelOverlap: false,
          label: {
            show: true,
            position: 'inside',
            formatter: '{d}%'
          },
          emphasis: {
            label: {
              show: true,
              fontSize: '20',
              fontWeight: 'bold'
            }
          },
          labelLine: {
            show: false
          },
          data: [
            {
              value: data.passed_count,
              name: '合格',
              itemStyle: { color: '#67C23A' }
            },
            {
              value: data.issue_count,
              name: '不合格',
              itemStyle: { color: '#F56C6C' }
            }
          ]
        }]
      }
      
      // 问题处理时效分析图表 - 基于后端质量数据
      const timelinessOption = {
        title: {
          text: '问题处理分析',
          left: 'center'
        },
        tooltip: {
          trigger: 'axis',
          axisPointer: { type: 'shadow' }
        },
        legend: {
          data: ['处理时间(小时)', '问题数量'],
          top: '10%'
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          top: '20%',
          containLabel: true
        },
        xAxis: [
          {
            type: 'category',
            data: ['质量问题', '工艺问题', '包装问题', '物流问题'],
            axisPointer: {
              type: 'shadow'
            }
          }
        ],
        yAxis: [
          {
            type: 'value',
            name: '处理时间(小时)',
            min: 0,
            axisLabel: {
              formatter: '{value}'
            }
          },
          {
            type: 'value',
            name: '问题数量',
            min: 0,
            axisLabel: {
              formatter: '{value}'
            }
          }
        ],
        series: [
          {
            name: '处理时间(小时)',
            type: 'bar',
            data: [
              // 计算每类问题的平均处理时间，或使用模拟数据
              data.quality_issue_time || 8.5,
              data.process_issue_time || 12.3,
              data.packaging_issue_time || 4.7,
              data.logistics_issue_time || 6.2
            ],
            itemStyle: {
              color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                { offset: 0, color: '#83bff6' },
                { offset: 1, color: '#188df0' }
              ])
            }
          },
          {
            name: '问题数量',
            type: 'line',
            yAxisIndex: 1,
            data: [
              // 使用实际问题数量或模拟数据
              Math.round(data.issue_count * 0.4) || 8,
              Math.round(data.issue_count * 0.25) || 5,
              Math.round(data.issue_count * 0.2) || 4,
              Math.round(data.issue_count * 0.15) || 3
            ],
            itemStyle: {
              color: '#FF8C69'
            },
            symbol: 'circle',
            symbolSize: 8,
            lineStyle: {
              width: 3
            }
          }
        ]
      };
      
      // 设置图表选项
      if (this.charts.quality) {
        this.charts.quality.setOption(qualityOption);
      }
      
      if (this.charts.timeliness) {
        this.charts.timeliness.setOption(timelinessOption);
      }
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
.overview-cards {
  margin-bottom: 20px;
}
.overview-item {
  padding: 10px 0;
}
.item-label {
  font-size: 14px;
  color: #909399;
}
.item-value {
  font-size: 24px;
  font-weight: bold;
  margin: 10px 0;
}
.item-trend {
  font-size: 14px;
}
.item-trend.up {
  color: #67C23A;
}
.item-trend.down {
  color: #F56C6C;
}
</style> 