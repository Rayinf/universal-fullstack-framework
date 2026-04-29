<template>
  <div class="page-view">
    <div class="page-header">
      <div class="title-container">
        <div class="title-accent"></div>
        <div class="title-row">
          <h2>合同业务看板</h2>
          <div class="page-description">报价转化、回款趋势、客户贡献与佣金排行。</div>
        </div>
      </div>
    </div>

    <div class="content-card dashboard-content" v-loading="loading">
      <div class="card-grid">
        <div class="metric-card-wrapper">
          <div class="metric-card warning">
            <div class="metric-icon">
              <el-icon><Timer /></el-icon>
            </div>
            <div class="metric-info">
              <div class="metric-label">待审批报价</div>
              <div class="metric-value">{{ cards.pendingApprovalCount }}</div>
            </div>
          </div>
        </div>
        <div class="metric-card-wrapper">
          <div class="metric-card primary">
            <div class="metric-icon">
              <el-icon><Money /></el-icon>
            </div>
            <div class="metric-info">
              <div class="metric-label">合同总金额</div>
              <div class="metric-value">{{ cards.contractTotalAmount.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }}</div>
            </div>
          </div>
        </div>
        <div class="metric-card-wrapper">
          <div class="metric-card success">
            <div class="metric-icon">
              <el-icon><CircleCheck /></el-icon>
            </div>
            <div class="metric-info">
              <div class="metric-label">整体回款率</div>
              <div class="metric-value">{{ cards.overallPaidRate.toFixed(1) }}%</div>
            </div>
          </div>
        </div>
        <div class="metric-card-wrapper">
          <div class="metric-card danger">
            <div class="metric-icon">
              <el-icon><Warning /></el-icon>
            </div>
            <div class="metric-info">
              <div class="metric-label">30天内到期合同</div>
              <div class="metric-value">{{ cards.expiringContractCount }}</div>
            </div>
          </div>
        </div>
        <div class="metric-card-wrapper">
          <div class="metric-card info">
            <div class="metric-icon">
              <el-icon><PieChart /></el-icon>
            </div>
            <div class="metric-info">
              <div class="metric-label">报价转化率</div>
              <div class="metric-value">{{ cards.quotationConversionRate.toFixed(1) }}%</div>
            </div>
          </div>
        </div>
      </div>

      <div class="chart-grid">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <div class="chart-header">
              <span class="header-title">月度回款趋势</span>
            </div>
          </template>
          <div ref="paymentTrendRef" class="chart"></div>
        </el-card>
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <div class="chart-header">
              <span class="header-title">客户贡献 TOP10</span>
            </div>
          </template>
          <div ref="customerTopRef" class="chart"></div>
        </el-card>
      </div>

      <div class="table-grid">
        <el-card shadow="hover" class="data-card">
          <template #header>
            <div class="chart-header">
              <span class="header-title">佣金排行 TOP5</span>
            </div>
          </template>
          <el-table :data="commissionTop" stripe height="300px">
            <el-table-column type="index" label="排名" width="60" align="center" />
            <el-table-column prop="salespersonName" label="销售员" />
            <el-table-column prop="amount" label="佣金总额" align="right" width="150">
              <template #default="{ row }">
                <span class="text-primary fw-bold">{{ row.amount.toLocaleString(undefined, { minimumFractionDigits: 2 }) }}</span>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts/core'
import type { EChartsCoreOption, EChartsType } from 'echarts/core'
import { BarChart, LineChart } from 'echarts/charts'
import { GridComponent, LegendComponent, TooltipComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import { ElMessage } from 'element-plus'
import {
  Timer,
  Money,
  CircleCheck,
  Warning,
  PieChart,
} from '@element-plus/icons-vue'
import {
  getContractDashboardApi,
  checkExpiringContractsApi,
  type ContractDashboardData,
} from '@/api/system/contract'

echarts.use([BarChart, LineChart, GridComponent, LegendComponent, TooltipComponent, CanvasRenderer])

// 项目统一配色方案
const colors = {
  primary: ['#6366f1', '#818cf8', '#a5b4fc'],
  success: ['#14b8a6', '#5eead4', '#99f6e4'],
  info: ['#60a5fa', '#93c5fd', '#bfdbfe'],
  warning: ['#f59e0b', '#fbbf24', '#fcd34d'],
  danger: ['#ef4444', '#f87171', '#fca5a5'],
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
const cards = ref<ContractDashboardData['cards']>({
  pendingApprovalCount: 0,
  contractTotalAmount: 0,
  overallPaidRate: 0,
  expiringContractCount: 0,
  quotationConversionRate: 0,
})
const paymentTrend = ref<ContractDashboardData['paymentTrend']>([])
const customerContributionTop = ref<ContractDashboardData['customerContributionTop']>([])
const commissionTop = ref<ContractDashboardData['commissionTop']>([])

const paymentTrendRef = ref<HTMLDivElement | null>(null)
const customerTopRef = ref<HTMLDivElement | null>(null)

let paymentChart: EChartsType | null = null
let customerChart: EChartsType | null = null

const renderCharts = () => {
  if (paymentTrendRef.value) {
    paymentChart?.dispose()
    paymentChart = echarts.init(paymentTrendRef.value)
    const option: EChartsCoreOption = {
      ...theme,
      color: colors.primary,
      tooltip: {
        ...theme.tooltip,
        trigger: 'axis',
      },
      xAxis: {
        type: 'category',
        data: paymentTrend.value.map((item) => item.month),
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
          name: '回款金额',
          data: paymentTrend.value.map((item) => item.amount),
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
    paymentChart.setOption(option)
  }

  if (customerTopRef.value) {
    customerChart?.dispose()
    customerChart = echarts.init(customerTopRef.value)
    const option: EChartsCoreOption = {
      ...theme,
      color: colors.info,
      tooltip: {
        ...theme.tooltip,
        trigger: 'axis',
      },
      xAxis: {
        type: 'value',
        splitLine: {
          show: true,
          lineStyle: { color: '#f1f5f9', type: 'dashed' },
        },
      },
      yAxis: {
        type: 'category',
        data: customerContributionTop.value.map((item) => item.customerName),
        axisLine: { show: true, lineStyle: { color: '#e2e8f0' } },
        axisTick: { show: false },
      },
      series: [
        {
          name: '贡献金额',
          type: 'bar',
          barWidth: '60%',
          itemStyle: {
            borderRadius: [0, 4, 4, 0],
          },
          data: customerContributionTop.value.map((item) => item.amount),
        },
      ],
    }
    customerChart.setOption(option)
  }
}

const handleResize = () => {
  paymentChart?.resize()
  customerChart?.resize()
}

const loadData = async () => {
  loading.value = true
  try {
    await checkExpiringContractsApi(30)
    const res = await getContractDashboardApi()
    if ((res.code === 0 || res.code === 200) && res.data) {
      cards.value = res.data.cards
      paymentTrend.value = res.data.paymentTrend || []
      customerContributionTop.value = res.data.customerContributionTop || []
      commissionTop.value = res.data.commissionTop || []
      renderCharts()
    } else {
      ElMessage.error(res.msg || '获取看板数据失败')
    }
  } catch (error) {
    console.error('获取看板失败:', error)
    ElMessage.error('获取看板失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadData()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  paymentChart?.dispose()
  customerChart?.dispose()
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
.metric-card.danger .metric-icon { background: rgba(239, 68, 68, 0.1); color: #ef4444; }

.metric-info {
  flex: 1;
}

.metric-label {
  color: var(--el-text-color-secondary);
  font-size: 13px;
  margin-bottom: 4px;
}

.metric-value {
  font-size: 22px;
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

.chart {
  height: 320px;
}

/* 表格卡片样式 */
.table-grid {
  display: grid;
  grid-template-columns: 1fr;
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
  .chart-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .card-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
