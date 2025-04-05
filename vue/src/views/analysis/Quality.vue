<template>
  <div class="quality-analysis-container">
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

    <!-- 质量数据概览 -->
    <el-row :gutter="20" class="data-overview">
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="data-item">
            <div class="data-title">总检测批次</div>
            <div class="data-value">{{ overview.totalBatches }}</div>
            <div class="data-compare">
              较上期 {{ overview.batchGrowth > 0 ? '+' : '' }}{{ overview.batchGrowth }}%
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="data-item">
            <div class="data-title">合格率</div>
            <div class="data-value">{{ overview.passRate }}%</div>
            <div class="data-compare">
              <el-progress :percentage="overview.passRate" :color="getProgressColor"></el-progress>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="data-item">
            <div class="data-title">问题批次</div>
            <div class="data-value">{{ overview.issueBatches }}</div>
            <div class="data-compare">
              问题率: {{ overview.issueRate }}%
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="data-item">
            <div class="data-title">平均处理时间</div>
            <div class="data-value">{{ overview.avgHandleTime }}h</div>
            <div class="data-compare">
              较上期 {{ overview.timeImprovement > 0 ? '+' : '' }}{{ overview.timeImprovement }}%
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 质量趋势分析 -->
    <el-card class="chart-card">
      <div slot="header">
        <span>质量趋势分析</span>
        <el-radio-group v-model="trendType" size="small" style="margin-left: 20px">
          <el-radio-button label="pass">合格率</el-radio-button>
          <el-radio-button label="issue">问题数</el-radio-button>
        </el-radio-group>
      </div>
      <div class="chart-container">
        <div ref="trendChart" style="height: 400px"></div>
      </div>
    </el-card>

    <!-- 质量分布分析 -->
    <el-row :gutter="20">
      <el-col :span="12">
        <el-card class="chart-card">
          <div slot="header">问题类型分布</div>
          <div class="chart-container">
            <div ref="issueTypeChart" style="height: 400px"></div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card class="chart-card">
          <div slot="header">问题原因分析</div>
          <div class="chart-container">
            <div ref="causeChart" style="height: 400px"></div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 质量问题明细 -->
    <el-card class="table-card">
      <div slot="header">质量问题明细</div>
      <el-table :data="issueList" border style="width: 100%">
        <el-table-column prop="batch_number" label="批次号" width="180"></el-table-column>
        <el-table-column prop="product_name" label="商品名称"></el-table-column>
        <el-table-column prop="check_time" label="检测时间" width="180"></el-table-column>
        <el-table-column prop="issue_type" label="问题类型" width="120">
          <template slot-scope="scope">
            <el-tag :type="getIssueTypeTag(scope.row.issue_type)">
              {{ scope.row.issue_type }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="severity" label="严重程度" width="100">
          <template slot-scope="scope">
            <el-tag :type="getSeverityTag(scope.row.severity)">
              {{ scope.row.severity }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="cause" label="原因分析"></el-table-column>
        <el-table-column prop="solution" label="解决方案"></el-table-column>
        <el-table-column prop="status" label="处理状态" width="100">
          <template slot-scope="scope">
            <el-tag :type="scope.row.status === 'resolved' ? 'success' : 'danger'">
              {{ scope.row.status === 'resolved' ? '已解决' : '未解决' }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
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
    </el-card>
  </div>
</template>

<script>
import * as echarts from 'echarts'

export default {
  name: 'QualityAnalysis',
  data() {
    return {
      filterForm: {
        dateRange: [],
        category: ''
      },
      categories: [],
      overview: {
        totalBatches: 0,
        batchGrowth: 0,
        passRate: 0,
        issueBatches: 0,
        issueRate: 0,
        avgHandleTime: 0,
        timeImprovement: 0
      },
      trendType: 'pass',
      issueList: [],
      page: 1,
      pageSize: 10,
      total: 0,
      charts: {
        trend: null,
        issueType: null,
        cause: null
      }
    }
  },
  computed: {
    getProgressColor() {
      return (percentage) => {
        if (percentage < 85) return '#F56C6C'
        if (percentage < 95) return '#E6A23C'
        return '#67C23A'
      }
    }
  },
  mounted() {
    this.initCharts()
    this.fetchCategories()
    this.fetchData()
  },
  methods: {
    initCharts() {
      this.charts.trend = echarts.init(this.$refs.trendChart)
      this.charts.issueType = echarts.init(this.$refs.issueTypeChart)
      this.charts.cause = echarts.init(this.$refs.causeChart)
      
      window.addEventListener('resize', () => {
        Object.values(this.charts).forEach(chart => chart.resize())
      })
    },
    fetchCategories() {
      this.$axios.get(this.$httpUrl + '/api/products/categories/')
        .then(res => {
          this.categories = res.data
        })
        .catch(err => {
          this.$message.error('获取分类列表失败')
          console.error(err)
        })
    },
    fetchData() {
      const params = {
        date_from: this.filterForm.dateRange?.[0],
        date_to: this.filterForm.dateRange?.[1],
        category: this.filterForm.category
      }
      
      // 获取概览数据
      this.$axios.get(this.$httpUrl + '/api/analysis/quality/overview/', { params })
        .then(res => {
          console.log('Quality overview response:', res.data)
          this.overview = res.data
          this.updateCharts(res.data)
        })
        .catch(err => {
          console.error('获取质量概览失败:', err)
          console.error('Error response:', err.response?.data)
          this.$message.error('获取质量概览数据失败: ' + (err.response?.data?.error || err.message))
        })

      // 获取问题列表
      this.$axios.get(this.$httpUrl + '/api/analysis/quality/issues/', {
        params: {
          ...params,
          page: this.page,
          page_size: this.pageSize
        }
      })
        .then(res => {
          this.issueList = res.data.results
          this.total = res.data.count
        })
        .catch(err => {
          this.$message.error('获取问题列表失败')
          console.error(err)
        })
    },
    updateCharts(data) {
      try {
        // 更新趋势图
        const trendOption = {
          title: { text: this.trendType === 'pass' ? '合格率趋势' : '问题数趋势' },
          tooltip: { trigger: 'axis' },
          xAxis: { 
            type: 'category',
            // 使用最近30天的日期作为X轴
            data: Array.from({ length: 30 }, (_, i) => {
              const date = new Date()
              date.setDate(date.getDate() - (29 - i))
              return date.toLocaleDateString()
            })
          },
          yAxis: { 
            type: 'value',
            name: this.trendType === 'pass' ? '合格率(%)' : '问题数',
            min: this.trendType === 'pass' ? 0 : undefined,
            max: this.trendType === 'pass' ? 100 : undefined
          },
          series: [{
            name: this.trendType === 'pass' ? '合格率' : '问题数',
            type: 'line',
            smooth: true,
            data: this.trendType === 'pass' ? 
              (data.trend?.pass_rates || []) : 
              (data.trend?.issue_counts || [])
          }]
        }
        
        if (this.charts.trend) {
          this.charts.trend.setOption(trendOption)
        }

        // 更新问题类型分布图
        const issueTypeOption = {
          title: { text: '问题类型分布' },
          tooltip: { trigger: 'item' },
          legend: { orient: 'vertical', left: 'left' },
          series: [{
            type: 'pie',
            radius: '50%',
            data: data.issueTypes?.map(item => ({
              name: item.name,
              value: item.count
            })) || []
          }]
        }
        this.charts.issueType.setOption(issueTypeOption)

        // 更新原因分析图
        const causeOption = {
          title: { text: '问题原因分析' },
          tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
          xAxis: { type: 'value' },
          yAxis: { 
            type: 'category',
            data: data.causes?.map(item => item.name) || []
          },
          series: [{
            type: 'bar',
            data: data.causes?.map(item => item.value) || []
          }]
        }
        this.charts.cause.setOption(causeOption)
      } catch (err) {
        console.error('Error updating charts:', err)
        this.$message.error('更新图表失败: ' + err.message)
      }
    },
    getIssueTypeTag(type) {
      const types = {
        '原材料': 'warning',
        '生产工艺': 'danger',
        '包装': 'info',
        '储存': 'warning'
      }
      return types[type] || ''
    },
    getSeverityTag(severity) {
      const types = {
        '严重': 'danger',
        '中等': 'warning',
        '轻微': 'info'
      }
      return types[severity] || ''
    },
    handleFilter() {
      this.page = 1
      this.fetchData()
    },
    handleSizeChange(val) {
      this.pageSize = val
      this.fetchData()
    },
    handleCurrentChange(val) {
      this.page = val
      this.fetchData()
    },
    exportData() {
      const params = {
        date_from: this.filterForm.dateRange?.[0],
        date_to: this.filterForm.dateRange?.[1],
        category: this.filterForm.category
      }
      
      this.$axios.get(this.$httpUrl + '/api/analysis/quality/export/', {
        params,
        responseType: 'blob'
      })
        .then(res => {
          const url = window.URL.createObjectURL(new Blob([res.data]))
          const link = document.createElement('a')
          link.href = url
          link.setAttribute('download', '质量分析报告.xlsx')
          document.body.appendChild(link)
          link.click()
          document.body.removeChild(link)
        })
        .catch(err => {
          this.$message.error('导出失败')
          console.error(err)
        })
    }
  },
  beforeDestroy() {
    // 销毁图表实例
    Object.values(this.charts).forEach(chart => {
      if (chart) {
        try {
          chart.dispose()
        } catch (err) {
          console.warn('Error disposing chart:', err)
        }
      }
    })
    
    // 移除事件监听
    window.removeEventListener('resize', this.handleResize)
  }
}
</script>

<style scoped>
.quality-analysis-container {
  padding: 20px;
}
.filter-card {
  margin-bottom: 20px;
}
.data-overview {
  margin-bottom: 20px;
}
.data-item {
  text-align: center;
}
.data-title {
  font-size: 14px;
  color: #666;
}
.data-value {
  font-size: 24px;
  font-weight: bold;
  margin: 10px 0;
}
.data-compare {
  font-size: 12px;
  padding: 0 20px;
}
.chart-card {
  margin-bottom: 20px;
}
.chart-container {
  padding: 10px;
}
.table-card {
  margin-bottom: 20px;
}
.pagination-container {
  margin-top: 20px;
  text-align: right;
}
</style> 