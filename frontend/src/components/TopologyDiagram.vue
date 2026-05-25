<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{ archName: string }>()

const svgs: Record<string, string> = {
  microservices: `
    <rect x="135" y="16" width="110" height="32" rx="6" fill="#0891b2"/><text x="190" y="37" text-anchor="middle" fill="#ecfeff" font-size="12">API Gateway</text>
    <rect x="18" y="88" width="78" height="42" rx="6" fill="#0e7490"/><text x="57" y="113" text-anchor="middle" fill="#fff" font-size="11">商品服务</text>
    <rect x="112" y="88" width="78" height="42" rx="6" fill="#0e7490"/><text x="151" y="113" text-anchor="middle" fill="#fff" font-size="11">订单服务</text>
    <rect x="206" y="88" width="78" height="42" rx="6" fill="#0e7490"/><text x="245" y="113" text-anchor="middle" fill="#fff" font-size="11">支付服务</text>
    <rect x="300" y="88" width="62" height="42" rx="6" fill="#0e7490"/><text x="331" y="113" text-anchor="middle" fill="#fff" font-size="11">用户</text>
    <line x1="190" y1="48" x2="57" y2="88" stroke="#67e8f9" stroke-width="1.5"/><line x1="190" y1="48" x2="151" y2="88" stroke="#67e8f9" stroke-width="1.5"/><line x1="190" y1="48" x2="245" y2="88" stroke="#67e8f9" stroke-width="1.5"/><line x1="190" y1="48" x2="331" y2="88" stroke="#67e8f9" stroke-width="1.5"/>
    <rect x="42" y="172" width="296" height="36" rx="6" fill="#0f172a" stroke="#334155"/><text x="190" y="195" text-anchor="middle" fill="#cbd5e1" font-size="11">服务发现 · 容器编排 · 分布式追踪</text>
  `,
  event: `
    <rect x="120" y="24" width="140" height="34" rx="8" fill="#7c3aed"/><text x="190" y="46" text-anchor="middle" fill="#fff" font-size="12">事件总线 / MQ</text>
    <rect x="28" y="98" width="86" height="38" rx="6" fill="#8b5cf6"/><text x="71" y="121" text-anchor="middle" fill="#fff" font-size="11">生产者</text>
    <rect x="145" y="98" width="86" height="38" rx="6" fill="#8b5cf6"/><text x="188" y="121" text-anchor="middle" fill="#fff" font-size="11">事件处理</text>
    <rect x="264" y="98" width="86" height="38" rx="6" fill="#6d28d9"/><text x="307" y="121" text-anchor="middle" fill="#fff" font-size="11">消费者</text>
    <line x1="71" y1="98" x2="160" y2="58" stroke="#c4b5fd" stroke-width="1.5"/><line x1="188" y1="98" x2="190" y2="58" stroke="#c4b5fd" stroke-width="1.5"/><line x1="307" y1="98" x2="220" y2="58" stroke="#c4b5fd" stroke-width="1.5"/>
  `,
  pipe: `
    <rect x="20" y="105" width="56" height="38" rx="6" fill="#0891b2"/><text x="48" y="129" text-anchor="middle" fill="#fff" font-size="11">输入</text>
    <rect x="94" y="105" width="64" height="38" rx="6" fill="#0e7490"/><text x="126" y="129" text-anchor="middle" fill="#fff" font-size="11">过滤器</text>
    <rect x="176" y="105" width="64" height="38" rx="6" fill="#0e7490"/><text x="208" y="129" text-anchor="middle" fill="#fff" font-size="11">转换</text>
    <rect x="258" y="105" width="64" height="38" rx="6" fill="#0e7490"/><text x="290" y="129" text-anchor="middle" fill="#fff" font-size="11">审核</text>
    <rect x="340" y="105" width="40" height="38" rx="6" fill="#0891b2"/><text x="360" y="129" text-anchor="middle" fill="#fff" font-size="11">输出</text>
    <line x1="76" y1="124" x2="94" y2="124" stroke="#67e8f9" stroke-width="2"/><line x1="158" y1="124" x2="176" y2="124" stroke="#67e8f9" stroke-width="2"/><line x1="240" y1="124" x2="258" y2="124" stroke="#67e8f9" stroke-width="2"/><line x1="322" y1="124" x2="340" y2="124" stroke="#67e8f9" stroke-width="2"/>
  `,
  cqrs: `
    <rect x="132" y="18" width="116" height="32" rx="6" fill="#d97706"/><text x="190" y="39" text-anchor="middle" fill="#fff" font-size="12">命令 / 查询分离</text>
    <rect x="28" y="88" width="124" height="50" rx="8" fill="#f59e0b"/><text x="90" y="118" text-anchor="middle" fill="#111827" font-size="12">写模型</text>
    <rect x="228" y="88" width="124" height="50" rx="8" fill="#10b981"/><text x="290" y="118" text-anchor="middle" fill="#052e16" font-size="12">读模型</text>
    <rect x="36" y="166" width="108" height="34" rx="6" fill="#0f172a" stroke="#475569"/><text x="90" y="187" text-anchor="middle" fill="#cbd5e1" font-size="11">Write DB</text>
    <rect x="236" y="166" width="108" height="34" rx="6" fill="#0f172a" stroke="#475569"/><text x="290" y="187" text-anchor="middle" fill="#cbd5e1" font-size="11">Read DB</text>
    <line x1="90" y1="138" x2="90" y2="166" stroke="#fbbf24"/><line x1="290" y1="138" x2="290" y2="166" stroke="#34d399"/><line x1="144" y1="183" x2="236" y2="183" stroke="#f59e0b" stroke-width="1.5" stroke-dasharray="5"/>
  `,
  hexagonal: `
    <polygon points="190,35 258,76 258,148 190,190 122,148 122,76" fill="rgba(34,197,94,.16)" stroke="#22c55e" stroke-width="2"/>
    <text x="190" y="116" text-anchor="middle" fill="#86efac" font-size="13" font-weight="700">核心领域</text>
    <rect x="42" y="36" width="74" height="30" rx="5" fill="#2563eb"/><text x="79" y="55" text-anchor="middle" fill="#fff" font-size="10">DB 适配器</text>
    <rect x="268" y="36" width="74" height="30" rx="5" fill="#2563eb"/><text x="305" y="55" text-anchor="middle" fill="#fff" font-size="10">API 适配器</text>
    <rect x="42" y="178" width="74" height="30" rx="5" fill="#2563eb"/><text x="79" y="197" text-anchor="middle" fill="#fff" font-size="10">UI 适配器</text>
    <rect x="268" y="178" width="74" height="30" rx="5" fill="#2563eb"/><text x="305" y="197" text-anchor="middle" fill="#fff" font-size="10">MQ 适配器</text>
  `,
  default: `
    <rect x="42" y="48" width="296" height="48" rx="8" fill="#0891b2"/><text x="190" y="78" text-anchor="middle" fill="#fff" font-size="13">架构核心组件</text>
    <rect x="64" y="134" width="96" height="40" rx="6" fill="#0f172a" stroke="#334155"/><text x="112" y="158" text-anchor="middle" fill="#cbd5e1" font-size="11">接口层</text>
    <rect x="220" y="134" width="96" height="40" rx="6" fill="#0f172a" stroke="#334155"/><text x="268" y="158" text-anchor="middle" fill="#cbd5e1" font-size="11">数据层</text>
    <line x1="160" y1="154" x2="220" y2="154" stroke="#67e8f9" stroke-width="1.5"/>
  `,
}

function pickKey(name: string) {
  const n = name.toLowerCase()
  if (n.includes('microservice') || n.includes('微服务')) return 'microservices'
  if (n.includes('event') || n.includes('事件')) return 'event'
  if (n.includes('pipe') || n.includes('管道')) return 'pipe'
  if (n.includes('cqrs')) return 'cqrs'
  if (n.includes('hexagonal') || n.includes('六边形')) return 'hexagonal'
  return 'default'
}

const selectedSVG = computed(() => svgs[pickKey(props.archName)] ?? svgs.default)
</script>

<template>
  <section class="glass p-5 animate-in">
    <div class="mb-4">
      <p class="text-xs font-semibold uppercase tracking-[0.16em] text-cyan-200">Topology</p>
      <h3 class="mt-1 text-lg font-bold text-white">架构拓扑图</h3>
      <p class="mt-1 text-xs text-slate-400">{{ archName }}</p>
    </div>
    <div class="overflow-hidden rounded-lg border border-white/10 bg-slate-950/60">
      <svg viewBox="0 0 380 240" class="h-auto w-full" v-html="selectedSVG" />
    </div>
  </section>
</template>
