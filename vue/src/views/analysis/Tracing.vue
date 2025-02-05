<template>
  <div class="tracing-analysis-container">
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

    <!-- 追溯数据概览 -->
    <el-row :gutter="20" class="data-overview">
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="data-item">
            <div class="data-title">生产批次数</div>
            <div class="data-value">{{ overview.batchCount }}</div>
            <div class="data-compare">
              <el-progress :percentage="overview.batchCompletion" :format="format"></el-progress>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="data-item">
            <div class="data-title">物流记录数</div>
            <div class="data-value">{{ overview.logisticsCount }}</div>
            <div class="data-compare">
              平均运输时间: {{ overview.averageTransportTime }}天
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="data-item">
            <div class="data-title">追溯查询次数</div>
            <div class="data-value">{{ overview.queryCount }}</div>
            <div class="data-compare">
              环比增长 {{ overview.queryGrowth }}%
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="data-item">
            <div class="data-title">问题批次数</div>
            <div class="data-value">{{ overview.issueCount }}</div>
            <div class="data-compare">
              批次合格率: {{ overview.qualifiedRate }}%
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 追溯链完整性分析 -->
    <el-card class="chart-card">
      <div slot="header">追溯链完整性分析</div>
      <div class="chart-container">
        <div ref="chainChart" style="height: 400px"></div>
      </div>
    </el-card>

    <!-- 追溯热点分析 -->
    <el-row :gutter="20">
      <el-col :span="12">
        <el-card class="chart-card">
          <div slot="header">追溯查询热点商品</div>
          <div class="chart-container">
            <div ref="hotProductChart" style="height: 400px"></div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card class="chart-card">
          <div slot="header">追溯查询地域分布</div>
          <div class="chart-container">
            <div ref="regionChart" style="height: 400px"></div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 追溯问题分析表格 -->
    <el-card class="table-card">
      <div slot="header">追溯问题分析</div>
      <el-table :data="issueList" border style="width: 100%">
        <el-table-column prop="batch_number" label="批次号" width="180"></el-table-column>
        <el-table-column prop="product_name" label="商品名称"></el-table-column>
        <el-table-column prop="issue_type" label="问题类型" width="120">
          <template slot-scope="scope">
            <el-tag :type="getIssueTypeTag(scope.row.issue_type)">
              {{ getIssueTypeText(scope.row.issue_type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="issue_date" label="发现时间" width="180"></el-table-column>
        <el-table-column prop="status" label="处理状态" width="100">
          <template slot-scope="scope">
            <el-tag :type="scope.row.status === 'resolved' ? 'success' : 'danger'">
              {{ scope.row.status === 'resolved' ? '已解决' : '未解决' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="问题描述"></el-table-column>
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
import { getMap } from '@jiaminghi/data-view'

export default {
  name: 'TracingAnalysis',
  data() {
    return {
      filterForm: {
        dateRange: [],
        category: ''
      },
      categories: [],
      overview: {
        batchCount: 0,
        batchCompletion: 0,
        logisticsCount: 0,
        averageTransportTime: 0,
        queryCount: 0,
        queryGrowth: 0,
        issueCount: 0,
        qualifiedRate: 0
      },
      issueList: [],
      page: 1,
      pageSize: 10,
      total: 0,
      charts: {
        chain: null,
        hotProduct: null,
        region: null
      }
    }
  },
  mounted() {
    // 注册中国地图
    getMap('china').then(map => {
      this.$echarts.registerMap('china', map)
      this.initCharts()
    })
    this.fetchCategories()
    this.fetchData()
  },
  methods: {
    format(percentage) {
      return `完整率 ${percentage}%`
    },
    initCharts() {
      this.charts.chain = echarts.init(this.$refs.chainChart)
      this.charts.hotProduct = echarts.init(this.$refs.hotProductChart)
      this.charts.region = echarts.init(this.$refs.regionChart)
      
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
      this.$axios.get(this.$httpUrl + '/api/analysis/tracing/overview/', { params })
        .then(res => {
          this.overview = res.data
          this.updateCharts(res.data)
        })
        .catch(err => {
          this.$message.error('获取追溯概览失败')
          console.error(err)
        })

      // 获取问题列表
      this.$axios.get(this.$httpUrl + '/api/analysis/tracing/issues/', {
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
      // 更新追溯链完整性分析图
      const chainOption = {
        title: { text: '追溯链完整性分析' },
        tooltip: { trigger: 'axis' },
        legend: { data: ['生产记录', '物流记录', '销售记录'] },
        xAxis: { type: 'category', data: data.chain.dates },
        yAxis: { type: 'value', name: '完整率(%)' },
        series: [
          {
            name: '生产记录',
            type: 'line',
            data: data.chain.production
          },
          {
            name: '物流记录',
            type: 'line',
            data: data.chain.logistics
          },
          {
            name: '销售记录',
            type: 'line',
            data: data.chain.sales
          }
        ]
      }
      this.charts.chain.setOption(chainOption)

      // 更新热点商品图
      const hotProductOption = {
        title: { text: '追溯查询热点商品' },
        tooltip: { trigger: 'axis' },
        xAxis: { type: 'value' },
        yAxis: { type: 'category', data: data.hotProducts.names },
        series: [{
          type: 'bar',
          data: data.hotProducts.counts
        }]
      }
      this.charts.hotProduct.setOption(hotProductOption)

      // 更新地域分布图
      const regionOption = {
        title: { text: '追溯查询地域分布' },
        tooltip: { trigger: 'item' },
        visualMap: {
          min: 0,
          max: data.regions.max,
          text: ['高', '低'],
          calculable: true
        },
        series: [{
          type: 'map',
          map: 'china',
          data: data.regions.data
        }]
      }
      this.charts.region.setOption(regionOption)
    },
    getIssueTypeTag(type) {
      const types = {
        production: 'warning',
        logistics: 'info',
        quality: 'danger'
      }
      return types[type] || ''
    },
    getIssueTypeText(type) {
      const types = {
        production: '生产问题',
        logistics: '物流问题',
        quality: '质量问题'
      }
      return types[type] || type
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
      
      this.$axios.get(this.$httpUrl + '/api/analysis/tracing/export/', {
        params,
        responseType: 'blob'
      })
        .then(res => {
          const url = window.URL.createObjectURL(new Blob([res.data]))
          const link = document.createElement('a')
          link.href = url
          link.setAttribute('download', '追溯分析报告.xlsx')
          document.body.appendChild(link)
          link.click()
          document.body.removeChild(link)
        })
        .catch(err => {
          this.$message.error('导出失败')
          console.error(err)
        })
    }
  }
}
</script>

<style scoped>
.tracing-analysis-container {
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