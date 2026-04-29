export const isMessageBoxCancel = (action: unknown): boolean =>
  action === 'cancel' || action === 'close'
