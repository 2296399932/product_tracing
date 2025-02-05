<template>
  <div class="sales-analysis-container">
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
          <el-button @click="exportData">导出数据</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 销售概览 -->
    <el-row :gutter="20" class="data-overview">
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="data-item">
            <div class="data-title">总销售额</div>
            <div class="data-value">¥{{ overview.totalAmount }}</div>
            <div class="data-compare" :class="overview.amountTrend > 0 ? 'up' : 'down'">
              {{ Math.abs(overview.amountTrend) }}% 较上期
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="data-item">
            <div class="data-title">订单数</div>
            <div class="data-value">{{ overview.orderCount }}</div>
            <div class="data-compare" :class="overview.orderTrend > 0 ? 'up' : 'down'">
              {{ Math.abs(overview.orderTrend) }}% 较上期
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="data-item">
            <div class="data-title">客单价</div>
            <div class="data-value">¥{{ overview.averageOrder }}</div>
            <div class="data-compare" :class="overview.averageTrend > 0 ? 'up' : 'down'">
              {{ Math.abs(overview.averageTrend) }}% 较上期
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="data-item">
            <div class="data-title">销售商品数</div>
            <div class="data-value">{{ overview.productCount }}</div>
            <div class="data-compare" :class="overview.productTrend > 0 ? 'up' : 'down'">
              {{ Math.abs(overview.productTrend) }}% 较上期
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 销售趋势图 -->
    <el-card class="chart-card">
      <div slot="header">
        <span>销售趋势</span>
        <el-radio-group v-model="trendType" size="small" style="margin-left: 20px">
          <el-radio-button label="amount">销售额</el-radio-button>
          <el-radio-button label="count">订单量</el-radio-button>
        </el-radio-group>
      </div>
      <div class="chart-container">
        <div ref="trendChart" style="height: 400px"></div>
      </div>
    </el-card>

    <!-- 商品销售排行 -->
    <el-row :gutter="20">
      <el-col :span="12">
        <el-card class="chart-card">
          <div slot="header">商品销售排行</div>
          <div class="chart-container">
            <div ref="rankChart" style="height: 400px"></div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card class="chart-card">
          <div slot="header">销售分类占比</div>
          <div class="chart-container">
            <div ref="pieChart" style="height: 400px"></div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 销售明细表格 -->
    <el-card class="table-card">
      <div slot="header">销售明细</div>
      <el-table :data="salesDetails" border style="width: 100%">
        <el-table-column prop="date" label="日期" width="180"></el-table-column>
        <el-table-column prop="product_name" label="商品名称"></el-table-column>
        <el-table-column prop="category_name" label="商品分类"></el-table-column>
        <el-table-column prop="quantity" label="数量" width="100"></el-table-column>
        <el-table-column prop="unit_price" label="单价" width="120">
          <template slot-scope="scope">
            ¥{{ scope.row.unit_price }}
          </template>
        </el-table-column>
        <el-table-column prop="total_amount" label="金额" width="120">
          <template slot-scope="scope">
            ¥{{ scope.row.total_amount }}
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
  name: 'SalesAnalysis',
  data() {
    return {
      filterForm: {
        dateRange: [],
        category: ''
      },
      categories: [],
      overview: {
        totalAmount: 0,
        orderCount: 0,
        averageOrder: 0,
        productCount: 0,
        amountTrend: 0,
        orderTrend: 0,
        averageTrend: 0,
        productTrend: 0
      },
      trendType: 'amount',
      salesDetails: [],
      page: 1,
      pageSize: 10,
      total: 0,
      charts: {
        trend: null,
        rank: null,
        pie: null
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
      this.charts.rank = echarts.init(this.$refs.rankChart)
      this.charts.pie = echarts.init(this.$refs.pieChart)
      
      window.addEventListener('resize', () => {
        this.charts.trend.resize()
        this.charts.rank.resize()
        this.charts.pie.resize()
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
      // 获取概览数据
      const params = {
        date_from: this.filterForm.dateRange?.[0],
        date_to: this.filterForm.dateRange?.[1],
        category: this.filterForm.category
      }
      
      this.$axios.get(this.$httpUrl + '/api/analysis/sales/overview/', { params })
        .then(res => {
          this.overview = res.data
          this.updateCharts(res.data)
        })
        .catch(err => {
          this.$message.error('获取销售概览失败')
          console.error(err)
        })

      // 获取明细数据
      this.$axios.get(this.$httpUrl + '/api/analysis/sales/details/', {
        params: {
          ...params,
          page: this.page,
          page_size: this.pageSize
        }
      })
        .then(res => {
          this.salesDetails = res.data.results
          this.total = res.data.count
        })
        .catch(err => {
          this.$message.error('获取销售明细失败')
          console.error(err)
        })
    },
    updateCharts(data) {
      // 更新趋势图
      const trendOption = {
        title: { text: '销售趋势' },
        tooltip: { trigger: 'axis' },
        xAxis: { type: 'category', data: data.trend.dates },
        yAxis: { type: 'value' },
        series: [{
          data: this.trendType === 'amount' ? data.trend.amounts : data.trend.counts,
          type: 'line',
          smooth: true
        }]
      }
      this.charts.trend.setOption(trendOption)

      // 更新排行图
      const rankOption = {
        title: { text: '商品销售排行' },
        tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
        xAxis: { type: 'value' },
        yAxis: { type: 'category', data: data.rank.products },
        series: [{
          type: 'bar',
          data: data.rank.amounts
        }]
      }
      this.charts.rank.setOption(rankOption)

      // 更新饼图
      const pieOption = {
        title: { text: '销售分类占比' },
        tooltip: { trigger: 'item' },
        series: [{
          type: 'pie',
          radius: '50%',
          data: data.category_distribution
        }]
      }
      this.charts.pie.setOption(pieOption)
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
      
      this.$axios.get(this.$httpUrl + '/api/analysis/sales/export/', { 
        params,
        responseType: 'blob'
      })
        .then(res => {
          const url = window.URL.createObjectURL(new Blob([res.data]))
          const link = document.createElement('a')
          link.href = url
          link.setAttribute('download', '销售分析报告.xlsx')
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
.sales-analysis-container {
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
}
.data-compare.up {
  color: #67C23A;
}
.data-compare.down {
  color: #F56C6C;
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