import type { TableCell, FormLayoutConfig } from '@/types/formConfig'

/**
 * 创建一个基础的 2x2 表格
 */
export const createDefaultLayout = (): FormLayoutConfig => {
  return {
    layoutType: 'table',
    border: true,
    rows: [
      {
        cells: [
          {
            id: Math.random().toString(36).substr(2, 9),
            content: { type: 'static', value: '表头1' },
            style: { align: 'center', fontWeight: 'bold' },
          },
          {
            id: Math.random().toString(36).substr(2, 9),
            content: { type: 'static', value: '表头2' },
            style: { align: 'center', fontWeight: 'bold' },
          },
        ],
      },
      {
        cells: [
          {
            id: Math.random().toString(36).substr(2, 9),
            content: { type: 'static', value: '' },
            style: { align: 'left' },
          },
          {
            id: Math.random().toString(36).substr(2, 9),
            content: { type: 'static', value: '' },
            style: { align: 'left' },
          },
        ],
      },
    ],
  }
}

/**
 * 获取单元格在平铺网格中的坐标
 */
export const getTableGrid = (layout: FormLayoutConfig) => {
  const grid: (string | null)[][] = []

  layout.rows.forEach((row, rowIndex) => {
    if (!grid[rowIndex]) grid[rowIndex] = []

    let colIndex = 0
    row.cells.forEach((cell) => {
      // 找到当前行第一个为空的位置
      while (grid[rowIndex][colIndex] !== undefined) {
        colIndex++
      }

      const rs = cell.rowspan || 1
      const cs = cell.colspan || 1

      for (let r = 0; r < rs; r++) {
        for (let c = 0; c < cs; c++) {
          if (!grid[rowIndex + r]) grid[rowIndex + r] = []
          grid[rowIndex + r][colIndex + c] = cell.id
        }
      }
      colIndex += cs
    })
  })

  return grid
}

/**
 * 获取逻辑列数
 */
export const getLogicalColumnCount = (layout: FormLayoutConfig) => {
  if (!layout || !layout.rows || !layout.rows.length) return 0
  const grid = getTableGrid(layout)
  return Math.max(...grid.map((row) => row.length), 0)
}

/**
 * 获取单元格所在的逻辑列起始位置
 */
export const getCellLogicalCol = (grid: (string | null)[][], cellId: string, rowIndex: number) => {
  const row = grid[rowIndex]
  if (!row) return -1
  return row.indexOf(cellId)
}

/**
 * 根据逻辑坐标寻找单元格ID
 */
export const getCellIdAt = (grid: (string | null)[][], rowIndex: number, colIndex: number) => {
  if (!grid[rowIndex]) return null
  return grid[rowIndex][colIndex]
}
