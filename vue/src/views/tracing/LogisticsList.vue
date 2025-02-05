<template>
  <div class="logistics-list">
    <el-table :data="records" v-loading="loading">
      <el-table-column prop="batch_number" label="批次号"/>
      <el-table-column prop="record_type" label="记录类型">
        <template #default="scope">
          {{ formatRecordType(scope.row.record_type) }}
        </template>
      </el-table-column>
      <el-table-column prop="from_location" label="起始位置"/>
      <el-table-column prop="to_location" label="目标位置"/>
      <el-table-column prop="operator_name" label="操作员"/>
      <el-table-column prop="status" label="状态">
        <template #default="scope">
          {{ formatStatus(scope.row.status) }}
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="创建时间">
        <template #default="scope">
          {{ formatDateTime(scope.row.created_at) }}
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script>
export default {
  methods: {
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
    }
  }
}
</script> 