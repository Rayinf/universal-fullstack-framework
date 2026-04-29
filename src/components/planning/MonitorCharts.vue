<template>
  <div class="monitor-charts">
    <el-row :gutter="20">
      <!-- 计划达成率图表 -->
      <el-col :span="24">
        <el-card shadow="hover" header="计划达成率">
          <div ref="achievementChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
import * as echarts from 'echarts/core'
import type { EChartsCoreOption, EChartsType } from 'echarts/core'
import { BarChart, LineChart } from 'echarts/charts'
import { GridComponent, LegendComponent, TooltipComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'

echarts.use([BarChart, LineChart, GridComponent, LegendComponent, TooltipComponent, CanvasRenderer])

interface ChartData {
  dates: string[]
  planned: number[]
  completed: number[]
  achievementRates: number[]
  productionLines: string[]
  lineLoads: Array<{ line: string; planned: number; actual: number }>
}

const props = defineProps<{
  data: ChartData
}>()

const achievementChartRef = ref<HTMLElement>()
const loadChartRef = ref<HTMLElement>()
let achievementChart: EChartsType | null = null
let loadChart: EChartsType | null = null

// 初始化计划达成率图表
const initAchievementChart = () => {
  if (!achievementChartRef.value) return

  achievementChart = echarts.init(achievementChartRef.value)

  // 动态计算达成率Y轴的最大值
  const maxAchievementRate = Math.max(...props.data.achievementRates)
  const yAxisMax = maxAchievementRate > 100 ? Math.ceil(maxAchievementRate / 20) * 20 : 100

  const option: EChartsCoreOption = {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'cross' },
    },
    legend: {
      data: ['计划数量', '完成数量', '达成率(%)'],
      top: 5,
      textStyle: { fontSize: 12 },
    },
    grid: {
      left: '50px',
      right: '60px',
      bottom: '40px',
      top: '60px',
      containLabel: false,
    },
    xAxis: {
      type: 'category',
      data: props.data.dates,
      boundaryGap: true,
      axisLabel: {
        fontSize: 11,
        rotate: 30,
      },
    },
    yAxis: [
      {
        type: 'value',
        name: '数量',
        position: 'left',
        nameTextStyle: { fontSize: 12 },
        axisLabel: {
          fontSize: 11,
          formatter: '{value}',
        },
      },
      {
        type: 'value',
        name: '达成率(%)',
        position: 'right',
        max: yAxisMax,
        nameTextStyle: { fontSize: 12 },
        axisLabel: {
          fontSize: 11,
          formatter: '{value}%',
        },
      },
    ],
    series: [
      {
        name: '计划数量',
        type: 'bar',
        data: props.data.planned,
        itemStyle: { color: '#409EFF' },
      },
      {
        name: '完成数量',
        type: 'bar',
        data: props.data.completed,
        itemStyle: { color: '#67C23A' },
      },
      {
        name: '达成率(%)',
        type: 'line',
        yAxisIndex: 1,
        data: props.data.achievementRates,
        itemStyle: { color: '#E6A23C' },
        lineStyle: { width: 2 },
        symbol: 'circle',
        symbolSize: 6,
      },
    ],
  }

  achievementChart.setOption(option)
}

// 初始化生产线负荷图表
const initLoadChart = () => {
  if (!loadChartRef.value) return

  loadChart = echarts.init(loadChartRef.value)

  const option: EChartsCoreOption = {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
    },
    legend: {
      data: ['计划负荷', '实际负荷'],
      top: 10,
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true,
    },
    xAxis: {
      type: 'category',
      data: props.data.productionLines,
    },
    yAxis: {
      type: 'value',
      name: '负荷(小时)',
    },
    series: [
      {
        name: '计划负荷',
        type: 'bar',
        data: props.data.lineLoads.map((l) => l.planned),
        itemStyle: { color: '#409EFF' },
      },
      {
        name: '实际负荷',
        type: 'bar',
        data: props.data.lineLoads.map((l) => l.actual),
        itemStyle: { color: '#67C23A' },
      },
    ],
  }

  loadChart.setOption(option)
}

// 更新图表
const updateCharts = () => {
  if (achievementChart) {
    // 动态计算达成率Y轴的最大值
    const maxAchievementRate = Math.max(...props.data.achievementRates)
    const yAxisMax = maxAchievementRate > 100 ? Math.ceil(maxAchievementRate / 20) * 20 : 100

    achievementChart.setOption({
      yAxis: [{}, { max: yAxisMax }],
      xAxis: { data: props.data.dates },
      series: [
        { data: props.data.planned },
        { data: props.data.completed },
        { data: props.data.achievementRates },
      ],
    })
  }

  if (loadChart) {
    loadChart.setOption({
      xAxis: { data: props.data.productionLines },
      series: [
        { data: props.data.lineLoads.map((l) => l.planned) },
        { data: props.data.lineLoads.map((l) => l.actual) },
      ],
    })
  }
}

// 监听数据变化
watch(
  () => props.data,
  () => {
    updateCharts()
  },
  { deep: true },
)

// 窗口大小变化时重绘
const handleResize = () => {
  achievementChart?.resize()
  loadChart?.resize()
}

onMounted(async () => {
  await nextTick()
  initAchievementChart()
  initLoadChart()
  // 等待一帧后重新调整大小，确保图表正确渲染
  requestAnimationFrame(() => {
    achievementChart?.resize()
    loadChart?.resize()
  })
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  achievementChart?.dispose()
  loadChart?.dispose()
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
.monitor-charts {
  width: 100%;
  min-width: 0;
}

.chart-container {
  height: 280px;
  width: 100%;
  min-width: 0;
}
</style>
