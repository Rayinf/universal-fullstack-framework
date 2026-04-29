<template>
  <div class="page-view">
    <div class="page-header">
      <div class="title-container">
        <div class="title-accent"></div>
        <div class="title-row">
          <h2>生产工单看板</h2>
          <div class="page-description">工单执行状态、日报工趋势、入库趋势与产品工单量排行。</div>
        </div>
      </div>
    </div>

    <div class="content-card dashboard-content" v-loading="loading">
      <div class="toolbar-row">
        <div class="filter-group">
          <el-radio-group v-model="days" size="default">
            <el-radio-button :label="7">近7天</el-radio-button>
            <el-radio-button :label="30">近30天</el-radio-button>
          </el-radio-group>
        </div>
        <div class="toolbar-actions">
          <div class="refresh-control">
            <span class="auto-refresh-label">自动刷新</span>
            <el-switch v-model="autoRefresh" inline-prompt active-text="开" inactive-text="关" />
          </div>
          <el-divider direction="vertical" />
          <el-button type="primary" plain :icon="Refresh" @click="loadData">立即刷新</el-button>
        </div>
      </div>

      <div class="card-grid">
        <div class="metric-card-wrapper">
          <div class="metric-card primary">
            <div class="metric-icon">
              <el-icon><Document /></el-icon>
            </div>
            <div class="metric-info">
              <div class="metric-label">工单总数</div>
              <div class="metric-value">{{ cards.totalCount }}</div>
            </div>
          </div>
        </div>
        <div class="metric-card-wrapper">
          <div class="metric-card warning">
            <div class="metric-icon">
              <el-icon><Timer /></el-icon>
            </div>
            <div class="metric-info">
              <div class="metric-label">待审批</div>
              <div class="metric-value">{{ cards.pendingApprovalCount }}</div>
            </div>
          </div>
        </div>
        <div class="metric-card-wrapper">
          <div class="metric-card info">
            <div class="metric-icon">
              <el-icon><Loading /></el-icon>
            </div>
            <div class="metric-info">
              <div class="metric-label">生产中</div>
              <div class="metric-value">{{ cards.producingCount }}</div>
            </div>
          </div>
        </div>
        <div class="metric-card-wrapper">
          <div class="metric-card success">
            <div class="metric-icon">
              <el-icon><CircleCheck /></el-icon>
            </div>
            <div class="metric-info">
              <div class="metric-label">待入库</div>
              <div class="metric-value">{{ cards.pendingInboundCount }}</div>
            </div>
          </div>
        </div>
        <div class="metric-card-wrapper">
          <div class="metric-card completion">
            <div class="metric-icon">
              <el-icon><PieChart /></el-icon>
            </div>
            <div class="metric-info">
              <div class="metric-label">完结率</div>
              <div class="metric-value">{{ cards.completionRate.toFixed(1) }}%</div>
            </div>
          </div>
        </div>
      </div>

      <div class="chart-grid">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <div class="chart-header">
              <span class="header-title">日报工合格趋势</span>
              <span class="header-subtitle">近{{ days }}天</span>
            </div>
          </template>
          <div ref="reportTrendRef" class="chart"></div>
        </el-card>
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <div class="chart-header">
              <span class="header-title">完工入库趋势</span>
              <span class="header-subtitle">近{{ days }}天</span>
            </div>
          </template>
          <div ref="inboundTrendRef" class="chart"></div>
        </el-card>
      </div>

      <div class="table-grid">
        <el-card shadow="hover" class="data-card">
          <template #header>
            <div class="chart-header">
              <span class="header-title">工单状态分布</span>
            </div>
          </template>
          <el-table :data="statusDistribution" stripe height="300px">
            <el-table-column prop="statusName" label="状态" />
            <el-table-column prop="count" label="数量" align="right" width="100">
              <template #default="{ row }">
                <span class="fw-bold">{{ row.count }}</span>
              </template>
            </el-table-column>
            <el-table-column label="占比" align="right" width="100">
              <template #default="{ row }">
                {{ cards.totalCount ? ((row.count / cards.totalCount) * 100).toFixed(1) : 0 }}%
              </template>
            </el-table-column>
          </el-table>
        </el-card>
        <el-card shadow="hover" class="data-card">
          <template #header>
            <div class="chart-header">
              <span class="header-title">产品工单量 TOP10</span>
            </div>
          </template>
          <el-table :data="productTop" stripe height="300px">
            <el-table-column type="index" label="排名" width="60" align="center" />
            <el-table-column prop="productName" label="产品" show-overflow-tooltip />
            <el-table-column prop="quantity" label="计划数量" align="right" width="120">
              <template #default="{ row }">
                <span class="text-primary fw-bold">{{ row.quantity }}</span>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref, watch } from 'vue'
import * as echarts from 'echarts/core'
import type { EChartsCoreOption, EChartsType } from 'echarts/core'
import { BarChart, LineChart } from 'echarts/charts'
import { GridComponent, LegendComponent, TooltipComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import { ElMessage } from 'element-plus'
import {
  Document,
  Timer,
  Loading,
  CircleCheck,
  PieChart,
  Refresh,
} from '@element-plus/icons-vue'
import { getWorkOrderDashboardApi, type WorkOrderDashboardData } from '@/api/system/workOrder'

echarts.use([BarChart, LineChart, GridComponent, LegendComponent, TooltipComponent, CanvasRenderer])

// 项目统一配色方案
const colors = {
  primary: ['#6366f1', '#818cf8', '#a5b4fc'],
  success: ['#14b8a6', '#5eead4', '#99f6e4'],
  info: ['#60a5fa', '#93c5fd', '#bfdbfe'],
  warning: ['#f59e0b', '#fbbf24', '#fcd34d'],
  gray: ['#64748b', '#94a3b8', '#cbd5e1'],
}

// ECharts 统一主题配置
const theme = {
  backgroundColor: 'transparent',
  textStyle: {
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
    color: '#334155',
  },
  tooltip: {
    backgroundColor: 'rgba(255, 255, 255, 0.9)',
    borderColor: 'rgba(0, 0, 0, 0.05)',
    borderWidth: 1,
    textStyle: {
      color: '#334155',
    },
  },
  legend: {
    textStyle: {
      color: '#64748b',
    },
    icon: 'circle',
    itemGap: 16,
  },
  grid: {
    left: '3%',
    right: '4%',
    bottom: '3%',
    containLabel: true,
  },
}

const loading = ref(false)
const days = ref<number>(7)
const autoRefresh = ref<boolean>(true)
const cards = ref<WorkOrderDashboardData['cards']>({
  totalCount: 0,
  pendingApprovalCount: 0,
  producingCount: 0,
  pendingInboundCount: 0,
  completedCount: 0,
  completionRate: 0,
})
const reportTrend = ref<WorkOrderDashboardData['reportTrend']>([])
const inboundTrend = ref<WorkOrderDashboardData['inboundTrend']>([])
const statusDistribution = ref<WorkOrderDashboardData['statusDistribution']>([])
const productTop = ref<WorkOrderDashboardData['productTop']>([])

const reportTrendRef = ref<HTMLDivElement | null>(null)
const inboundTrendRef = ref<HTMLDivElement | null>(null)

let reportChart: EChartsType | null = null
let inboundChart: EChartsType | null = null
let refreshTimer: number | null = null

const REFRESH_INTERVAL_MS = 60 * 1000

const renderCharts = () => {
  if (reportTrendRef.value) {
    reportChart?.dispose()
    reportChart = echarts.init(reportTrendRef.value)
    const option: EChartsCoreOption = {
      ...theme,
      color: colors.primary,
      tooltip: {
        ...theme.tooltip,
        trigger: 'axis',
      },
      xAxis: {
        type: 'category',
        data: reportTrend.value.map((item) => item.date),
        axisLine: { show: true, lineStyle: { color: '#e2e8f0' } },
        axisTick: { show: false },
      },
      yAxis: {
        type: 'value',
        splitLine: {
          show: true,
          lineStyle: { color: '#f1f5f9', type: 'dashed' },
        },
      },
      series: [
        {
          name: '报工数量',
          data: reportTrend.value.map((item) => item.quantity),
          type: 'line',
          smooth: true,
          symbol: 'circle',
          symbolSize: 8,
          lineStyle: { width: 3 },
          areaStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: 'rgba(99, 102, 241, 0.2)' },
              { offset: 1, color: 'rgba(99, 102, 241, 0)' },
            ]),
          },
        },
      ],
    }
    reportChart.setOption(option)
  }

  if (inboundTrendRef.value) {
    inboundChart?.dispose()
    inboundChart = echarts.init(inboundTrendRef.value)
    const option: EChartsCoreOption = {
      ...theme,
      color: colors.success,
      tooltip: {
        ...theme.tooltip,
        trigger: 'axis',
      },
      xAxis: {
        type: 'category',
        data: inboundTrend.value.map((item) => item.date),
        axisLine: { show: true, lineStyle: { color: '#e2e8f0' } },
        axisTick: { show: false },
      },
      yAxis: {
        type: 'value',
        splitLine: {
          show: true,
          lineStyle: { color: '#f1f5f9', type: 'dashed' },
        },
      },
      series: [
        {
          name: '入库数量',
          type: 'bar',
          barWidth: '40%',
          itemStyle: {
            borderRadius: [4, 4, 0, 0],
          },
          data: inboundTrend.value.map((item) => item.quantity),
        },
      ],
    }
    inboundChart.setOption(option)
  }
}

const handleResize = () => {
  reportChart?.resize()
  inboundChart?.resize()
}

const loadData = async () => {
  if (loading.value) {
    return
  }
  loading.value = true
  try {
    const res = await getWorkOrderDashboardApi({ days: days.value })
    if ((res.code === 0 || res.code === 200) && res.data) {
      cards.value = res.data.cards
      reportTrend.value = res.data.reportTrend || []
      inboundTrend.value = res.data.inboundTrend || []
      statusDistribution.value = res.data.statusDistribution || []
      productTop.value = res.data.productTop || []
      renderCharts()
    } else {
      ElMessage.error(res.msg || '获取看板数据失败')
    }
  } catch (error) {
    console.error('获取生产看板失败:', error)
    ElMessage.error('获取看板失败')
  } finally {
    loading.value = false
  }
}

const stopAutoRefresh = () => {
  if (refreshTimer !== null) {
    window.clearInterval(refreshTimer)
    refreshTimer = null
  }
}

const startAutoRefresh = () => {
  stopAutoRefresh()
  if (!autoRefresh.value) {
    return
  }
  refreshTimer = window.setInterval(() => {
    loadData()
  }, REFRESH_INTERVAL_MS)
}

watch(days, () => {
  loadData()
})

watch(autoRefresh, () => {
  startAutoRefresh()
})

onMounted(() => {
  loadData()
  startAutoRefresh()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  stopAutoRefresh()
  reportChart?.dispose()
  inboundChart?.dispose()
})
</script>

<style scoped>
@import '@/styles/common.css';

.dashboard-content {
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 24px;
  overflow-y: auto;
}

.toolbar-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 16px;
}

.toolbar-actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

.refresh-control {
  display: flex;
  align-items: center;
  gap: 8px;
}

.auto-refresh-label {
  color: var(--el-text-color-secondary);
  font-size: 13px;
}

/* 指标卡片样式 */
.card-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 16px;
}

.metric-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  background: var(--el-bg-color);
  border-radius: 12px;
  border: 1px solid var(--el-border-color-lighter);
  transition: all 0.3s ease;
}

.metric-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.metric-icon {
  width: 48px;
  height: 48px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.metric-card.primary .metric-icon { background: rgba(99, 102, 241, 0.1); color: #6366f1; }
.metric-card.warning .metric-icon { background: rgba(245, 158, 11, 0.1); color: #f59e0b; }
.metric-card.info .metric-icon { background: rgba(96, 165, 250, 0.1); color: #60a5fa; }
.metric-card.success .metric-icon { background: rgba(20, 184, 166, 0.1); color: #14b8a6; }
.metric-card.completion .metric-icon { background: rgba(139, 92, 246, 0.1); color: #8b5cf6; }

.metric-info {
  flex: 1;
}

.metric-label {
  color: var(--el-text-color-secondary);
  font-size: 13px;
  margin-bottom: 4px;
}

.metric-value {
  font-size: 24px;
  font-weight: 700;
  color: var(--el-text-color-primary);
}

/* 图表卡片样式 */
.chart-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.chart-card {
  border-radius: 12px;
  overflow: hidden;
}

.chart-header {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.header-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.header-subtitle {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.chart {
  height: 320px;
}

/* 表格卡片样式 */
.table-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.data-card {
  border-radius: 12px;
}

.fw-bold { font-weight: 600; }
.text-primary { color: var(--el-color-primary); }

@media (max-width: 1400px) {
  .card-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 1200px) {
  .chart-grid,
  .table-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .card-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  .toolbar-row {
    flex-direction: column;
    align-items: stretch;
  }
}
</style>
