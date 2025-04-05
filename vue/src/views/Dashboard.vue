<template>
  <div class="dashboard-container">
    <!-- 数据概览 -->
    <el-row :gutter="20" class="data-overview">
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="data-item">
            <div class="data-icon">
              <i class="el-icon-goods"></i>
            </div>
            <div class="data-info">
              <div class="data-title">商品总数</div>
              <div class="data-value">{{ overview.total_products }}</div>
              <div class="data-compare" :class="overview.productGrowth > 0 ? 'up' : 'down'">
                {{ Math.abs(overview.productGrowth) }}% 较上月
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="data-item">
            <div class="data-icon blue">
              <i class="el-icon-box"></i>
            </div>
            <div class="data-info">
              <div class="data-title">在库批次</div>
              <div class="data-value">{{ overview.total_batches }}</div>
              <div class="data-compare">
                库存总值: ¥{{ overview.total_revenue }}
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="data-item">
            <div class="data-icon green">
              <i class="el-icon-sell"></i>
            </div>
            <div class="data-info">
              <div class="data-title">本月销售额</div>
              <div class="data-value">{{ overview.total_sales }}单</div>
              <div class="data-compare" :class="overview.salesGrowth > 0 ? 'up' : 'down'">
                {{ Math.abs(overview.salesGrowth) }}% 较上月
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="data-item">
            <div class="data-icon orange">
              <i class="el-icon-warning"></i>
            </div>
            <div class="data-info">
              <div class="data-title">预警信息</div>
              <div class="data-value">{{ overview.warningCount }}</div>
              <div class="data-compare">
                其中 {{ overview.expiringCount }} 个批次即将过期
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 图表区域 -->
    <el-row :gutter="20" class="chart-row">
      <el-col :span="16">
        <el-card class="chart-card">
          <div slot="header">
            <span>销售趋势</span>
            <el-radio-group v-model="salesType" size="small" style="margin-left: 20px">
              <el-radio-button label="week">本周</el-radio-button>
              <el-radio-button label="month">本月</el-radio-button>
              <el-radio-button label="year">全年</el-radio-button>
            </el-radio-group>
          </div>
          <div class="chart-container">
            <div ref="salesChart" style="height: 350px"></div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card class="chart-card">
          <div slot="header">商品分类占比</div>
          <div class="chart-container">
            <div ref="categoryChart" style="height: 350px"></div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 最新动态 -->
    <el-row :gutter="20" class="list-row">
      <el-col :span="12">
        <el-card class="list-card">
          <div slot="header">
            <span>最新订单</span>
            <el-button style="float: right; padding: 3px 0" type="text">
              查看更多
            </el-button>
          </div>
          <el-table :data="latestOrders" style="width: 100%" size="small">
            <el-table-column prop="order_number" label="订单号" width="180"></el-table-column>
            <el-table-column prop="customer" label="客户"></el-table-column>
            <el-table-column prop="amount" label="金额" width="120">
              <template slot-scope="scope">
                ¥{{ scope.row.amount }}
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="100">
              <template slot-scope="scope">
                <el-tag :type="getOrderStatusType(scope.row.status)">
                  {{ scope.row.status }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="date" label="时间" width="180"></el-table-column>
          </el-table>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card class="list-card">
          <div slot="header">
            <span>系统预警</span>
            <el-button style="float: right; padding: 3px 0" type="text">
              查看更多
            </el-button>
          </div>
          <el-table :data="warnings" style="width: 100%" size="small">
            <el-table-column prop="type" label="类型" width="120">
              <template slot-scope="scope">
                <el-tag :type="getWarningType(scope.row.type)">
                  {{ scope.row.type }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="content" label="内容"></el-table-column>
            <el-table-column prop="created_at" label="时间" width="180"></el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import * as echarts from 'echarts'

export default {
  name: 'Dashboard',
  data() {
    return {
      overview: {
        total_products: 0,
        total_batches: 0,
        total_sales: 0,
        total_revenue: 0,
        productGrowth: 0,
        warningCount: 0,
        expiringCount: 0
      },
      salesType: 'month',
      latestOrders: [],
      warnings: [],
      charts: {
        sales: null,
        category: null
      }
    }
  },
  mounted() {
    this.initCharts()
    this.fetchData()
    const userInfo = JSON.parse(localStorage.getItem('userInfo') || '{}')
    console.log('User Info:', {
      username: userInfo.username || '未知用户',
      role: userInfo.role || '未知角色',
      email: userInfo.email || '未知邮箱',
      id: userInfo.id || '未知ID',
      is_active: userInfo.is_active ? '启用' : '禁用',
      phone: userInfo.phone || '未知手机号',
      last_login: userInfo.last_login || '从未登录'
    })
  },
  methods: {
    initCharts() {
      this.charts.sales = echarts.init(this.$refs.salesChart)
      this.charts.category = echarts.init(this.$refs.categoryChart)
      
      window.addEventListener('resize', () => {
        Object.values(this.charts).forEach(chart => chart.resize())
      })
    },
    fetchData() {
      // 添加认证头
      const headers = {
        'Authorization': 'Bearer ' + localStorage.getItem('token')
      }

      // 获取概览数据
      this.$axios.get(this.$httpUrl + '/api/dashboard/overview/', { headers })
        .then(response => {
          this.overview = response.data
        })
        .catch(err => {
          console.error('获取概览数据失败:', err)
        })

      // 获取销售趋势
      this.$axios.get(this.$httpUrl + '/api/dashboard/sales-trend/', {
        params: { type: this.salesType },
        headers
      })
        .then(response => {
          this.updateSalesChart(response.data)
        })
        .catch(err => {
          console.error('获取销售趋势失败:', err)
        })

      // 获取分类统计
      this.$axios.get(this.$httpUrl + '/api/dashboard/category-stats/', { headers })
        .then(response => {
          this.updateCategoryChart(response.data)
        })
        .catch(err => {
          console.error('获取分类统计失败:', err)
        })

      // 获取最新订单
      this.$axios.get(this.$httpUrl + '/api/dashboard/latest-orders/', { headers })
        .then(response => {
          this.latestOrders = response.data
        })
        .catch(err => {
          console.error('获取最新订单失败:', err)
        })

      // 获取系统预警
      this.$axios.get(this.$httpUrl + '/api/dashboard/warnings/', { headers })
        .then(response => {
          this.warnings = response.data
        })
        .catch(err => {
          console.error('获取系统预警失败:', err)
        })
    },
    updateSalesChart(data) {
      const option = {
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'cross',
            crossStyle: {
              color: '#999'
            }
          }
        },
        legend: {
          data: ['销售额', '订单量']
        },
        xAxis: {
          type: 'category',
          data: data.dates,
          axisPointer: {
            type: 'shadow'
          }
        },
        yAxis: [
          {
            type: 'value',
            name: '销售额',
            min: 0,
            axisLabel: {
              formatter: '¥{value}'
            }
          },
          {
            type: 'value',
            name: '订单量',
            min: 0,
            position: 'right'
          }
        ],
        series: [
          {
            name: '销售额',
            type: 'line',
            smooth: true,
            data: data.values,
            itemStyle: {
              color: '#409EFF'
            }
          },
          {
            name: '订单量',
            type: 'bar',
            yAxisIndex: 1,
            data: data.orders,
            itemStyle: {
              color: '#67C23A'
            }
          }
        ]
      }
      this.charts.sales.setOption(option)
    },
    updateCategoryChart(data) {
      const option = {
        tooltip: {
          trigger: 'item',
          formatter: '{a} <br/>{b}: {c} ({d}%)'
        },
        legend: {
          orient: 'vertical',
          right: '5%',
          top: 'center',
          data: data.map(item => item.name)
        },
        series: [
          {
            name: '商品分类',
            type: 'pie',
            radius: ['40%', '60%'],
            center: ['40%', '50%'],
            avoidLabelOverlap: false,
            label: {
              show: true,
              position: 'outside',
              formatter: '{b}: {c}',
              textStyle: {
                fontSize: 12
              }
            },
            emphasis: {
              label: {
                show: true,
                fontSize: '16',
                fontWeight: 'bold'
              }
            },
            labelLine: {
              show: true,
              length: 10,
              length2: 10
            },
            data: data.map(item => ({
              name: item.name,
              value: item.value
            }))
          }
        ]
      }
      this.charts.category.setOption(option)
    },
    getOrderStatusType(status) {
      const types = {
        '待付款': 'warning',
        '已付款': 'primary',
        '已发货': 'success',
        '已完成': 'info'
      }
      return types[status] || ''
    },
    getWarningType(type) {
      const types = {
        '库存不足': 'danger',
        '即将过期': 'warning',
        '质量问题': 'danger',
        '系统异常': 'info'
      }
      return types[type] || ''
    }
  },
  watch: {
    salesType() {
      this.fetchData()
    }
  },
  created() {
    this.fetchData()
  }
}
</script>

<style scoped>
.dashboard-container {
  padding: 20px;
}
.data-overview {
  margin-bottom: 20px;
}
.data-item {
  display: flex;
  align-items: center;
}
.data-icon {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background-color: #409EFF;
  display: flex;
  justify-content: center;
  align-items: center;
  margin-right: 20px;
}
.data-icon i {
  font-size: 40px;
  color: #fff;
}
.data-icon.blue {
  background-color: #67C23A;
}
.data-icon.green {
  background-color: #E6A23C;
}
.data-icon.orange {
  background-color: #F56C6C;
}
.data-info {
  flex: 1;
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
  color: #999;
}
.data-compare.up {
  color: #67C23A;
}
.data-compare.down {
  color: #F56C6C;
}
.chart-row {
  margin-bottom: 20px;
}
.chart-card {
  margin-bottom: 20px;
}
.chart-container {
  padding: 10px;
}
.list-row {
  margin-bottom: 20px;
}
.list-card {
  margin-bottom: 20px;
}
</style> 