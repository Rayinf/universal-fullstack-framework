declare module '@vue/eslint-config-typescript' {
  export function defineConfigWithVueTs(...configs: any[]): any
  export const vueTsConfigs: {
    recommended: any
  }
}

declare module '@vue/eslint-config-prettier/skip-formatting' {
  const skipFormatting: any
  export default skipFormatting
}

declare module '@vitest/eslint-plugin' {
  const pluginVitest: {
    configs: {
      recommended: any
    }
  }
  export default pluginVitest
}
