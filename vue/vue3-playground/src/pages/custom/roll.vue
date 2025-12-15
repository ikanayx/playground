<template>
  <div
    class="container"
    ref="containerRef"
    @touchstart="handleStart"
    @touchend="handleEnd"
    @touchmove="handleMove"
    @mousedown="handleStart"
    @mouseup="handleEnd"
    @mousemove="handleMove"
  >
    <!-- 中心位置标记（可选，用于可视化） -->
    <div class="center-point"></div>
    <!-- 图片容器 -->
    <div class="images-wrapper">
      <div
        class="image-item"
        v-for="(img, index) in imageList"
        :key="index"
        :style="getImageStyle(index)"
      >
        <img :src="img" alt="环绕图片" class="img" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'

// 核心配置参数
const D = 200 // 图片到中心的距离（px）
const alpha = 15 // 每张图片的夹角（度数），12张图片总夹角360°，这里按需求是11*alpha的旋转范围
const maxRotate = 11 * alpha // 最大旋转角度（临界条件）

// 响应式数据
const containerRef = ref(null)
const startX = ref<number | null>(null) // 滑动起始X坐标
const currentRotate = ref(0) // 当前总旋转角度（初始为0，第一张在正上方）
const imageList = ref<string[]>([]) // 图片列表（示例使用占位图，可替换为实际图片）

// 初始化图片列表（12张占位图）
onMounted(() => {
  // 生成12张占位图（可替换为实际图片路径）
  imageList.value = Array.from(
    { length: 12 },
    (_, i) => `https://picsum.photos/200/200?random=${i}`,
  )
})

// 计算每张图片的样式（位置+旋转）
const getImageStyle = (index: number) => {
  // 转换角度为弧度（Math.sin/cos需要弧度）
  // 初始角度：第一张在正上方（90°），之后每张增加alpha度，加上当前总旋转角度
  const angle = 90 + currentRotate.value - index * alpha
  const radian = (angle * Math.PI) / 180

  // 计算坐标（中心为容器中点）
  const left = `calc(50% + ${Math.cos(radian) * D}px)`
  const top = `calc(50% - ${Math.sin(radian) * D}px)` // 减号是因为CSS的y轴向下，而数学的y轴向上

  return {
    left,
    top,
    transform: 'translate(-50%, -50%)', // 让图片中心对准计算出的坐标
  }
}

// 滑动事件处理
const handleStart = (e: any) => {
  // 兼容触摸和鼠标事件
  startX.value = e.type.includes('mouse') ? e.clientX : e.touches[0].clientX
}

const handleMove = (e: any) => {
  if (startX.value === null) return
  const currentX = e.type.includes('mouse') ? e.clientX : e.touches[0].clientX
  const diffX = currentX - startX.value // 右滑为正，左滑为负

  // 计算旋转角度（每滑动1px，旋转0.5度，可调整灵敏度）
  const rotateDiff = -diffX * 0.5 // 负号：右滑顺时针（角度增加），左滑逆时针（角度减少）
  const newRotate = currentRotate.value + rotateDiff

  // 限制旋转范围：0 ~ maxRotate（临界条件）
  currentRotate.value = Math.max(0, Math.min(maxRotate, newRotate))

  // 重置起始位置，让滑动更流畅
  startX.value = currentX
}

const handleEnd = () => {
  startX.value = null // 重置起始位置
}
</script>

<style scoped>
.container {
  width: 100vw;
  height: 100vh;
  position: relative;
  overflow: hidden;
  background-color: #f5f5f5;
  cursor: grab;
}

.container:active {
  cursor: grabbing;
}

.center-point {
  width: 10px;
  height: 10px;
  background-color: red;
  border-radius: 50%;
  position: absolute;
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%);
  z-index: 1;
}

.images-wrapper {
  width: 100%;
  height: 100%;
  position: relative;
}

.image-item {
  position: absolute;
  /* transition:
    left 0.1s ease,
    top 0.1s ease; 平滑过渡 */
  z-index: 2;

  /* 禁止文本选中 */
  -webkit-user-select: none;
  -moz-user-select: none;
  -ms-user-select: none;
  user-select: none;

  /* 禁止移动端长按弹出菜单（Safari/Chrome移动端核心属性） */
  -webkit-touch-callout: none;

  /* 禁止拖拽 */
  -webkit-user-drag: none; /* Safari专属：禁止元素被拖拽 */
  user-drag: none; /* 标准写法（部分浏览器支持） */
}

.img {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  object-fit: cover;
}
</style>
