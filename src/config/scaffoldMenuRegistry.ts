type ScaffoldMenuItem = {
  id: string
  title: string
  path?: string
  icon?: string
  children?: ScaffoldMenuItem[]
  functionCode?: string
  hidden?: boolean
  roles?: string[]
}

export type ScaffoldMenuBucket = 'root' | 'system' | 'sales' | 'production'

export const scaffoldedMenuRegistry: Record<ScaffoldMenuBucket, ScaffoldMenuItem[]> = {
  root: [
    // __SCAFFOLD_ROOT_MENU_ENTRIES__
  ],
  system: [
    // __SCAFFOLD_SYSTEM_MENU_ENTRIES__
  ],
  sales: [
    // __SCAFFOLD_SALES_MENU_ENTRIES__
  ],
  production: [
    // __SCAFFOLD_PRODUCTION_MENU_ENTRIES__
  ],
}
