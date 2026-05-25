<script setup lang="ts">
import { ref, onMounted, watch, nextTick } from 'vue'
import type { Candidate } from './CandidateCards.vue'

const props = defineProps<{ candidates: Candidate[] }>()

const canvasRef = ref<HTMLCanvasElement | null>(null)

const dimensions = [
  { key: 'scalability', label: '可扩展性' },
  { key: 'performance', label: '性能' },
  { key: 'coupling', label: '松耦合' },
  { key: 'complexity', label: '低复杂度' },
  { key: 'deployability', label: '部署灵活' },
  { key: 'testability', label: '可测试性' },
]

// KB scores
const kbMap: Record<string, Record<string, string>> = {
  '分层架构 (Layered Architecture)': { scalability: '低', performance: '中', coupling: '高（层间紧耦合）', complexity: '低', deployability: '单体部署', testability: '中' },
  '微服务架构 (Microservices Architecture)': { scalability: '高', performance: '中（需考虑网络开销）', coupling: '低', complexity: '高', deployability: '独立部署', testability: '高（单服务）' },
  '事件驱动架构 (Event-Driven Architecture)': { scalability: '高', performance: '高（异步处理）', coupling: '低（通过事件解耦）', complexity: '高', deployability: '独立部署', testability: '中（事件流测试复杂）' },
  'CQRS (命令查询职责分离)': { scalability: '高（读写独立扩展）', performance: '高', coupling: '低', complexity: '高', deployability: '独立部署', testability: '高' },
  '管道-过滤器架构 (Pipe-Filter Architecture)': { scalability: '中', performance: '高（并行处理）', coupling: '低（过滤器独立）', complexity: '中', deployability: '单体/独立', testability: '高（每个过滤器独立测试）' },
  'SOA (面向服务架构)': { scalability: '中', performance: '低（ESB是瓶颈）', coupling: '中', complexity: '高', deployability: '集中管理', testability: '中' },
  '六边形架构/端口适配器 (Hexagonal/Ports & Adapters)': { scalability: '中', performance: '中', coupling: '低（核心与外部解耦）', complexity: '中', deployability: '灵活', testability: '高（核心可独立测试）' },
  'MVC架构 (Model-View-Controller)': { scalability: '低', performance: '中', coupling: '中', complexity: '低', deployability: '单体', testability: '中' },
  'Space-Based架构 (基于空间的架构)': { scalability: '极高', performance: '极高（内存级访问）', coupling: '低', complexity: '极高', deployability: '分布式', testability: '低' },
  '对等架构 (Peer-to-Peer Architecture)': { scalability: '高（自组织扩展）', performance: '中', coupling: '极低', complexity: '高', deployability: '去中心化部署', testability: '低' },
  'Serverless架构': { scalability: '极高（自动扩缩）', performance: '中（冷启动延迟）', coupling: '低（事件触发）', complexity: '中', deployability: '函数级部署', testability: '中' },
  '插件架构/微内核 (Plugin/Microkernel Architecture)': { scalability: '中', performance: '中', coupling: '低（核心与插件解耦）', complexity: '中', deployability: '核心+插件独立', testability: '高' },
}

function getScore(candidateName: string, dim: string): number {
  const kb = kbMap[candidateName]
  if (!kb) return 3
  const val = kb[dim] || '中'
  // Extract core value before parentheses
  const core = val.split('（')[0]
  const scoreMap: Record<string, number> = { '极高': 5, '高': 4, '中': 3, '低': 2, '极低': 1 }
  const raw = scoreMap[core] ?? 3
  // Invert coupling and complexity (lower is better for the radar)
  if (dim === 'coupling' || dim === 'complexity') {
    return 6 - raw
  }
  return raw
}

const lineColors = [
  'rgba(245, 158, 11, 0.8)',
  'rgba(148, 163, 184, 0.7)',
  'rgba(217, 119, 6, 0.7)',
]
const fillColors = [
  'rgba(245, 158, 11, 0.15)',
  'rgba(148, 163, 184, 0.1)',
  'rgba(217, 119, 6, 0.1)',
]

function draw() {
  const canvas = canvasRef.value
  if (!canvas || !props.candidates.length) return

  const dpr = window.devicePixelRatio || 1
  const rect = canvas.getBoundingClientRect()
  canvas.width = rect.width * dpr
  canvas.height = rect.height * dpr
  const ctx = canvas.getContext('2d')!
  ctx.scale(dpr, dpr)

  const W = rect.width
  const H = rect.height
  const cx = W / 2
  const cy = H / 2
  const levels = 5
  const radius = Math.min(W, H) * 0.38
  const n = dimensions.length

  ctx.clearRect(0, 0, W, H)

  // Grid
  for (let l = 1; l <= levels; l++) {
    ctx.beginPath()
    for (let i = 0; i < n; i++) {
      const angle = (Math.PI * 2 * i) / n - Math.PI / 2
      const r = (radius * l) / levels
      const x = cx + r * Math.cos(angle)
      const y = cy + r * Math.sin(angle)
      i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y)
    }
    ctx.closePath()
    ctx.strokeStyle = 'rgba(71, 85, 105, 0.4)'
    ctx.lineWidth = 1
    ctx.stroke()
  }

  // Axes
  for (let i = 0; i < n; i++) {
    const angle = (Math.PI * 2 * i) / n - Math.PI / 2
    ctx.beginPath()
    ctx.moveTo(cx, cy)
    ctx.lineTo(cx + radius * Math.cos(angle), cy + radius * Math.sin(angle))
    ctx.strokeStyle = 'rgba(71, 85, 105, 0.3)'
    ctx.stroke()
  }

  // Labels
  ctx.fillStyle = '#94a3b8'
  ctx.font = '12px system-ui, sans-serif'
  ctx.textAlign = 'center'
  for (let i = 0; i < n; i++) {
    const angle = (Math.PI * 2 * i) / n - Math.PI / 2
    const lr = radius + 20
    const x = cx + lr * Math.cos(angle)
    const y = cy + lr * Math.sin(angle)
    ctx.fillText(dimensions[i].label, x, y + 4)
  }

  // Data polygons
  const count = Math.min(props.candidates.length, 3)
  for (let c = count - 1; c >= 0; c--) {
    const cand = props.candidates[c]
    ctx.beginPath()
    for (let i = 0; i < n; i++) {
      const score = getScore(cand.name, dimensions[i].key)
      const angle = (Math.PI * 2 * i) / n - Math.PI / 2
      const r = (radius * score) / levels
      const x = cx + r * Math.cos(angle)
      const y = cy + r * Math.sin(angle)
      i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y)
    }
    ctx.closePath()
    ctx.fillStyle = fillColors[c]
    ctx.fill()
    ctx.strokeStyle = lineColors[c]
    ctx.lineWidth = 2
    ctx.stroke()
  }

  // Legend
  const legendY = H - 24
  ctx.font = '11px system-ui, sans-serif'
  for (let c = 0; c < count; c++) {
    const lx = cx - (count * 60) / 2 + c * 60 + 20
    ctx.fillStyle = lineColors[c]
    ctx.fillRect(lx, legendY - 5, 10, 10)
    ctx.fillStyle = '#94a3b8'
    ctx.textAlign = 'left'
    const name = props.candidates[c].name.split('(')[0].trim()
    ctx.fillText(name.slice(0, 6), lx + 14, legendY + 4)
  }
}

onMounted(() => {
  nextTick(() => draw())
  window.addEventListener('resize', draw)
})

watch(() => props.candidates, () => nextTick(() => draw()), { deep: true })
</script>

<template>
  <div class="glass p-5 animate-in">
    <h3 class="text-lg font-bold text-slate-100 mb-4">📊 多维度雷达对比</h3>
    <canvas ref="canvasRef" class="w-full aspect-square max-h-[360px] mx-auto" />
  </div>
</template>
