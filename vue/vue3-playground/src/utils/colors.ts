/**
 * 计算两个颜色之间的渐变颜色
 * @param {string} color1 - 起始颜色（对应0，16进制格式，如"#FF0000"）
 * @param {string} color2 - 结束颜色（对应1，16进制格式，如"#0000FF"）
 * @param {number} ratio - 渐变比例（0到1之间的浮点数）
 * @returns {string} - 计算得到的渐变颜色（16进制格式）
 */
export function getGradientColor(color1: string, color2: string, ratio: number): string {
  // 确保ratio在0-1之间
  ratio = Math.max(0, Math.min(1, ratio))

  // 去除#号并解析颜色值
  const r1 = parseInt(color1.substring(1, 3), 16)
  const g1 = parseInt(color1.substring(3, 5), 16)
  const b1 = parseInt(color1.substring(5, 7), 16)

  const r2 = parseInt(color2.substring(1, 3), 16)
  const g2 = parseInt(color2.substring(3, 5), 16)
  const b2 = parseInt(color2.substring(5, 7), 16)

  // 计算渐变颜色
  const r = Math.round(r1 * (1 - ratio) + r2 * ratio)
  const g = Math.round(g1 * (1 - ratio) + g2 * ratio)
  const b = Math.round(b1 * (1 - ratio) + b2 * ratio)

  // 将RGB值转换为16进制字符串
  const toHex = (c: number) => {
    const hex = c.toString(16)
    return hex.length === 1 ? '0' + hex : hex
  }

  return `#${toHex(r)}${toHex(g)}${toHex(b)}`
}

/**
 * 计算两个颜色之间的渐变颜色，保持高明亮度
 * @param {string} color1 - 起始颜色（16进制格式）
 * @param {string} color2 - 结束颜色（16进制格式）
 * @param {number} ratio - 渐变比例（0到1之间的浮点数）
 * @param {number} [minLightness=0.7] - 最小亮度值（0-1）
 * @returns {string} - 计算得到的渐变颜色（16进制格式）
 */
export function getBrightGradientColor(
  color1: string,
  color2: string,
  ratio: number,
  minLightness: number = 0.7,
): string {
  // 确保ratio在0-1之间
  ratio = Math.max(0, Math.min(1, ratio))

  // 将16进制颜色转换为HSL
  const hsl1 = hexToHsl(color1)
  const hsl2 = hexToHsl(color2)

  // 确保起始和结束颜色都有足够亮度
  hsl1.l = Math.max(hsl1.l, minLightness)
  hsl2.l = Math.max(hsl2.l, minLightness)

  // 计算渐变HSL值
  const h = hsl1.h * (1 - ratio) + hsl2.h * ratio
  const s = hsl1.s * (1 - ratio) + hsl2.s * ratio
  const l = hsl1.l * (1 - ratio) + hsl2.l * ratio

  // 将HSL转换回16进制
  return hslToHex({ h, s, l })
}

// 辅助函数：16进制转HSL
function hexToHsl(hex: string) {
  // 去除#号并解析颜色值
  const r = parseInt(hex.substring(1, 3), 16) / 255
  const g = parseInt(hex.substring(3, 5), 16) / 255
  const b = parseInt(hex.substring(5, 7), 16) / 255

  const max = Math.max(r, g, b)
  const min = Math.min(r, g, b)
  let h, s
  const l = (max + min) / 2

  if (max === min) {
    h = s = 0 // 灰度
  } else {
    const d = max - min
    s = l > 0.5 ? d / (2 - max - min) : d / (max + min)

    switch (max) {
      case r:
        h = (g - b) / d + (g < b ? 6 : 0)
        break
      case g:
        h = (b - r) / d + 2
        break
      case b:
        h = (r - g) / d + 4
        break
    }

    h! /= 6
  }

  return { h: h! * 360, s, l }
}

// 辅助函数：HSL转16进制
function hslToHex(hsl: { h: number; s: number; l: number }) {
  const h = hsl.h / 360
  const s = hsl.s
  const l = hsl.l

  let r, g, b

  if (s === 0) {
    r = g = b = l // 灰度
  } else {
    const hue2rgb = (p: number, q: number, t: number) => {
      if (t < 0) t += 1
      if (t > 1) t -= 1
      if (t < 1 / 6) return p + (q - p) * 6 * t
      if (t < 1 / 2) return q
      if (t < 2 / 3) return p + (q - p) * (2 / 3 - t) * 6
      return p
    }

    const q = l < 0.5 ? l * (1 + s) : l + s - l * s
    const p = 2 * l - q

    r = hue2rgb(p, q, h + 1 / 3)
    g = hue2rgb(p, q, h)
    b = hue2rgb(p, q, h - 1 / 3)
  }

  const toHex = (x: number) => {
    const hex = Math.round(x * 255).toString(16)
    return hex.length === 1 ? '0' + hex : hex
  }

  return `#${toHex(r)}${toHex(g)}${toHex(b)}`
}

/**
 * 调整颜色亮度
 * @param {String} color 十六进制颜色
 * @param {Number} ratio 亮度比例 0-1，1为最亮
 * @returns {String} 调整后的颜色
 */
export function adjustColorBrightness(color: string, ratio: number): string {
  // 解析颜色
  let r = parseInt(color.slice(1, 3), 16)
  let g = parseInt(color.slice(3, 5), 16)
  let b = parseInt(color.slice(5, 7), 16)

  // 根据比例调整亮度 (HSV色彩空间更适合，但RGB简化版性能更好)
  const factor = 0.3 + ratio * 0.7 // 确保最低亮度
  r = Math.min(255, Math.round(r * factor))
  g = Math.min(255, Math.round(g * factor))
  b = Math.min(255, Math.round(b * factor))

  // 转换回十六进制
  return `#${((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1)}`
}
