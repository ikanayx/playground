export function base64ToBlob(base64: string) {
  if (!base64) {
    return undefined
  }
  // 分离base64数据中的元数据和实际内容
  const arr = base64.split(',')
  const mime = arr[0]!.match(/:(.*?);/)![1] // 获取MIME类型（如image/png）
  const bstr = atob(arr[1]!) // 解码base64内容为二进制字符串
  let n = bstr.length
  const u8arr = new Uint8Array(n) // 创建Uint8Array存储二进制数据
  while (n--) {
    u8arr[n] = bstr.charCodeAt(n)
  }
  return new Blob([u8arr], { type: mime }) // 生成Blob对象
}
