<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{ archName: string }>()

// Each SVG is a function returning SVG markup
const svgs: Record<string, string> = {
  microservices: `
    <rect x="140" y="10" width="100" height="30" rx="6" fill="#1d4ed8"/><text x="190" y="30" text-anchor="middle" fill="#fff" font-size="11">API网关</text>
    <rect x="10" y="70" width="80" height="40" rx="6" fill="#2563eb"/><text x="50" y="93" text-anchor="middle" fill="#fff" font-size="10">商品服务</text>
    <rect x="100" y="70" width="80" height="40" rx="6" fill="#2563eb"/><text x="140" y="93" text-anchor="middle" fill="#fff" font-size="10">订单服务</text>
    <rect x="190" y="70" width="80" height="40" rx="6" fill="#2563eb"/><text x="230" y="93" text-anchor="middle" fill="#fff" font-size="10">支付服务</text>
    <rect x="280" y="70" width="80" height="40" rx="6" fill="#2563eb"/><text x="320" y="93" text-anchor="middle" fill="#fff" font-size="10">用户服务</text>
    <rect x="10" y="135" width="80" height="35" rx="6" fill="#1e293b" stroke="#475569"/><text x="50" y="157" text-anchor="middle" fill="#94a3b8" font-size="10">DB</text>
    <rect x="190" y="135" width="80" height="35" rx="6" fill="#1e293b" stroke="#475569"/><text x="230" y="157" text-anchor="middle" fill="#94a3b8" font-size="10">DB</text>
    <rect x="280" y="135" width="80" height="35" rx="6" fill="#1e293b" stroke="#475569"/><text x="320" y="157" text-anchor="middle" fill="#94a3b8" font-size="10">DB</text>
    <line x1="190" y1="40" x2="50" y2="70" stroke="#60a5fa" stroke-width="1.5"/><line x1="190" y1="40" x2="140" y2="70" stroke="#60a5fa" stroke-width="1.5"/><line x1="190" y1="40" x2="230" y2="70" stroke="#60a5fa" stroke-width="1.5"/><line x1="190" y1="40" x2="320" y2="70" stroke="#60a5fa" stroke-width="1.5"/>
    <line x1="50" y1="110" x2="50" y2="135" stroke="#475569" stroke-width="1"/><line x1="230" y1="110" x2="230" y2="135" stroke="#475569" stroke-width="1"/><line x1="320" y1="110" x2="320" y2="135" stroke="#475569" stroke-width="1"/>
    <rect x="40" y="195" width="300" height="40" rx="6" fill="#0f172a" stroke="#1e3a5f"/><text x="190" y="220" text-anchor="middle" fill="#64748b" font-size="11">服务发现 · 容器编排 · 分布式追踪</text>
  `,
  eventdriven: `
    <rect x="140" y="10" width="100" height="28" rx="6" fill="#9333ea"/><text x="190" y="28" text-anchor="middle" fill="#fff" font-size="10">事件总线</text>
    <rect x="15" y="70" width="80" height="35" rx="6" fill="#a855f7"/><text x="55" y="92" text-anchor="middle" fill="#fff" font-size="10">生产者A</text>
    <rect x="110" y="70" width="80" height="35" rx="6" fill="#a855f7"/><text x="150" y="92" text-anchor="middle" fill="#fff" font-size="10">生产者B</text>
    <rect x="205" y="70" width="80" height="35" rx="6" fill="#7c3aed"/><text x="245" y="92" text-anchor="middle" fill="#fff" font-size="10">消费者A</text>
    <rect x="300" y="70" width="80" height="35" rx="6" fill="#7c3aed"/><text x="340" y="92" text-anchor="middle" fill="#fff" font-size="10">消费者B</text>
    <line x1="55" y1="70" x2="175" y2="38" stroke="#a855f7" stroke-width="1.5"/><line x1="150" y1="70" x2="190" y2="38" stroke="#a855f7" stroke-width="1.5"/>
    <line x1="200" y1="38" x2="245" y2="70" stroke="#7c3aed" stroke-width="1.5"/><line x1="200" y1="38" x2="340" y2="70" stroke="#7c3aed" stroke-width="1.5"/>
    <rect x="40" y="140" width="320" height="35" rx="6" fill="#1e293b" stroke="#475569"/><text x="200" y="162" text-anchor="middle" fill="#94a3b8" font-size="11">Kafka / RabbitMQ · 事件溯源 · Saga</text>
  `,
  pipefilter: `
    <rect x="10" y="90" width="55" height="36" rx="6" fill="#0ea5e9"/><text x="37" y="112" text-anchor="middle" fill="#fff" font-size="10">源数据</text>
    <rect x="78" y="90" width="55" height="36" rx="6" fill="#0284c7"/><text x="105" y="112" text-anchor="middle" fill="#fff" font-size="10">过滤器1</text>
    <rect x="146" y="90" width="55" height="36" rx="6" fill="#0284c7"/><text x="173" y="112" text-anchor="middle" fill="#fff" font-size="10">过滤器2</text>
    <rect x="214" y="90" width="55" height="36" rx="6" fill="#0284c7"/><text x="241" y="112" text-anchor="middle" fill="#fff" font-size="10">过滤器3</text>
    <rect x="282" y="90" width="55" height="36" rx="6" fill="#0ea5e9"/><text x="309" y="112" text-anchor="middle" fill="#fff" font-size="10">输出</text>
    <line x1="65" y1="108" x2="78" y2="108" stroke="#38bdf8" stroke-width="2.5"/><line x1="133" y1="108" x2="146" y2="108" stroke="#38bdf8" stroke-width="2.5"/><line x1="201" y1="108" x2="214" y2="108" stroke="#38bdf8" stroke-width="2.5"/><line x1="269" y1="108" x2="282" y2="108" stroke="#38bdf8" stroke-width="2.5"/>
  `,
  cqrs: `
    <rect x="140" y="10" width="100" height="28" rx="6" fill="#d97706"/><text x="190" y="28" text-anchor="middle" fill="#fff" font-size="10">命令/查询分离</text>
    <rect x="20" y="65" width="130" height="50" rx="6" fill="#f59e0b"/><text x="85" y="85" text-anchor="middle" fill="#111" font-size="11">写模型 (Command)</text>
    <rect x="230" y="65" width="130" height="50" rx="6" fill="#10b981"/><text x="295" y="85" text-anchor="middle" fill="#111" font-size="11">读模型 (Query)</text>
    <rect x="20" y="140" width="130" height="38" rx="6" fill="#1e293b" stroke="#475569"/><text x="85" y="164" text-anchor="middle" fill="#94a3b8" font-size="10">Write DB</text>
    <rect x="230" y="140" width="130" height="38" rx="6" fill="#1e293b" stroke="#475569"/><text x="295" y="164" text-anchor="middle" fill="#94a3b8" font-size="10">Read DB</text>
    <line x1="85" y1="115" x2="85" y2="140" stroke="#475569"/><line x1="295" y1="115" x2="295" y2="140" stroke="#475569"/>
    <line x1="150" y1="159" x2="230" y2="159" stroke="#d97706" stroke-width="1.5" stroke-dasharray="4"/>
  `,
  hexagonal: `
    <polygon points="190,15 255,55 255,115 190,155 125,115 125,55" fill="#22c55e" opacity=".25" stroke="#22c55e" stroke-width="1.5"/>
    <text x="190" y="85" text-anchor="middle" fill="#22c55e" font-size="12" font-weight="bold">核心业务</text>
    <rect x="70" y="5" width="40" height="25" rx="4" fill="#3b82f6"/><text x="90" y="22" text-anchor="middle" fill="#fff" font-size="9">DB适配器</text>
    <rect x="275" y="5" width="40" height="25" rx="4" fill="#3b82f6"/><text x="295" y="22" text-anchor="middle" fill="#fff" font-size="9">API适配器</text>
    <rect x="275" y="130" width="45" height="25" rx="4" fill="#3b82f6"/><text x="297" y="147" text-anchor="middle" fill="#fff" font-size="9">MQ适配器</text>
    <rect x="70" y="130" width="45" height="25" rx="4" fill="#3b82f6"/><text x="92" y="147" text-anchor="middle" fill="#fff" font-size="9">UI适配器</text>
  `,
  p2p: `
    <circle cx="100" cy="70" r="25" fill="#a855f7"/><text x="100" y="75" text-anchor="middle" fill="#fff" font-size="10">节点A</text>
    <circle cx="280" cy="70" r="25" fill="#a855f7"/><text x="280" y="75" text-anchor="middle" fill="#fff" font-size="10">节点B</text>
    <circle cx="190" cy="160" r="25" fill="#a855f7"/><text x="190" y="165" text-anchor="middle" fill="#fff" font-size="10">节点C</text>
    <circle cx="60" cy="180" r="20" fill="#7c3aed" opacity=".7"/><text x="60" y="185" text-anchor="middle" fill="#fff" font-size="9">节点D</text>
    <line x1="120" y1="60" x2="260" y2="60" stroke="#a855f7" stroke-width="1.5"/><line x1="110" y1="90" x2="170" y2="140" stroke="#a855f7" stroke-width="1.5"/><line x1="260" y1="90" x2="210" y2="140" stroke="#a855f7" stroke-width="1.5"/><line x1="80" y1="180" x2="170" y2="160" stroke="#7c3aed" stroke-width=".8"/>
  `,
  layered: `
    <rect x="20" y="10" width="340" height="38" rx="4" fill="#3b82f6"/><text x="190" y="34" text-anchor="middle" fill="#fff" font-size="11">表示层 (Presentation)</text>
    <rect x="20" y="58" width="340" height="38" rx="4" fill="#2563eb"/><text x="190" y="82" text-anchor="middle" fill="#fff" font-size="11">业务逻辑层 (Business Logic)</text>
    <rect x="20" y="106" width="340" height="38" rx="4" fill="#1d4ed8"/><text x="190" y="130" text-anchor="middle" fill="#fff" font-size="11">数据访问层 (Data Access)</text>
    <rect x="20" y="154" width="340" height="38" rx="4" fill="#1e3a5f"/><text x="190" y="178" text-anchor="middle" fill="#93c5fd" font-size="11">数据库 (Database)</text>
  `,
  mvc: `
    <rect x="145" y="10" width="90" height="30" rx="4" fill="#3b82f6"/><text x="190" y="30" text-anchor="middle" fill="#fff" font-size="11">Controller</text>
    <rect x="145" y="120" width="90" height="30" rx="4" fill="#1d4ed8"/><text x="190" y="140" text-anchor="middle" fill="#fff" font-size="11">Model</text>
    <rect x="15" y="45" width="90" height="55" rx="4" fill="#2563eb"/><text x="60" y="78" text-anchor="middle" fill="#fff" font-size="11">View</text>
    <line x1="105" y1="55" x2="145" y2="25" stroke="#60a5fa" stroke-width="1.5"/><line x1="105" y1="95" x2="145" y2="135" stroke="#60a5fa" stroke-width="1.5"/>
    <line x1="190" y1="40" x2="190" y2="120" stroke="#60a5fa" stroke-width="1.5"/>
  `,
  soa: `
    <rect x="135" y="10" width="120" height="40" rx="6" fill="#d97706"/><text x="195" y="35" text-anchor="middle" fill="#fff" font-size="12">ESB 企业服务总线</text>
    <rect x="10" y="90" width="90" height="38" rx="4" fill="#f59e0b"/><text x="55" y="113" text-anchor="middle" fill="#111" font-size="10">系统A（遗留）</text>
    <rect x="115" y="90" width="90" height="38" rx="4" fill="#f59e0b"/><text x="160" y="113" text-anchor="middle" fill="#111" font-size="10">系统B（ERP）</text>
    <rect x="220" y="90" width="90" height="38" rx="4" fill="#f59e0b"/><text x="265" y="113" text-anchor="middle" fill="#111" font-size="10">系统C（CRM）</text>
    <line x1="55" y1="90" x2="160" y2="50" stroke="#f59e0b" stroke-width="1.5"/><line x1="160" y1="90" x2="195" y2="50" stroke="#f59e0b" stroke-width="1.5"/><line x1="265" y1="90" x2="230" y2="50" stroke="#f59e0b" stroke-width="1.5"/>
  `,
  plugin: `
    <rect x="130" y="80" width="120" height="50" rx="6" fill="#9333ea"/><text x="190" y="110" text-anchor="middle" fill="#fff" font-size="12">微内核</text>
    <rect x="15" y="18" width="85" height="38" rx="4" fill="#7c3aed"/><text x="57" y="42" text-anchor="middle" fill="#fff" font-size="10">插件A (语法)</text>
    <rect x="280" y="18" width="85" height="38" rx="4" fill="#7c3aed"/><text x="322" y="42" text-anchor="middle" fill="#fff" font-size="10">插件B (调试)</text>
    <rect x="15" y="155" width="85" height="38" rx="4" fill="#7c3aed"/><text x="57" y="179" text-anchor="middle" fill="#fff" font-size="10">插件C (部署)</text>
    <rect x="280" y="155" width="85" height="38" rx="4" fill="#7c3aed"/><text x="322" y="179" text-anchor="middle" fill="#fff" font-size="10">插件D (测试)</text>
    <line x1="100" y1="37" x2="140" y2="100" stroke="#a855f7" stroke-width="1.5"/><line x1="280" y1="37" x2="240" y2="100" stroke="#a855f7" stroke-width="1.5"/><line x1="100" y1="174" x2="140" y2="115" stroke="#a855f7" stroke-width="1.5"/><line x1="280" y1="174" x2="240" y2="115" stroke="#a855f7" stroke-width="1.5"/>
  `,
  serverless: `
    <rect x="20" y="40" width="75" height="36" rx="4" fill="#0ea5e9"/><text x="57" y="62" text-anchor="middle" fill="#fff" font-size="10">API请求</text>
    <rect x="120" y="40" width="75" height="36" rx="4" fill="#0ea5e9"/><text x="157" y="62" text-anchor="middle" fill="#fff" font-size="10">定时触发</text>
    <rect x="220" y="40" width="75" height="36" rx="4" fill="#0ea5e9"/><text x="257" y="62" text-anchor="middle" fill="#fff" font-size="10">文件事件</text>
    <rect x="100" y="105" width="180" height="60" rx="8" fill="#0284c7"/><text x="190" y="130" text-anchor="middle" fill="#fff" font-size="12">FaaS 函数</text><text x="190" y="148" text-anchor="middle" fill="#93c5fd" font-size="10">自动扩缩 · 按需计费</text>
    <line x1="57" y1="76" x2="140" y2="105" stroke="#38bdf8" stroke-width="1.5"/><line x1="157" y1="76" x2="190" y2="105" stroke="#38bdf8" stroke-width="1.5"/><line x1="257" y1="76" x2="240" y2="105" stroke="#38bdf8" stroke-width="1.5"/>
  `,
  spacebased: `
    <rect x="30" y="10" width="310" height="120" rx="8" fill="#1e293b" stroke="#a855f7" stroke-width="1.5"/>
    <text x="185" y="35" text-anchor="middle" fill="#a855f7" font-size="12">分布式内存网格</text>
    <circle cx="100" cy="72" r="20" fill="#7c3aed"/><text x="100" y="77" text-anchor="middle" fill="#fff" font-size="9">分区1</text>
    <circle cx="185" cy="72" r="20" fill="#7c3aed"/><text x="185" y="77" text-anchor="middle" fill="#fff" font-size="9">分区2</text>
    <circle cx="270" cy="72" r="20" fill="#7c3aed"/><text x="270" y="77" text-anchor="middle" fill="#fff" font-size="9">分区3</text>
    <line x1="120" y1="72" x2="165" y2="72" stroke="#a855f7" stroke-width="1.5"/><line x1="205" y1="72" x2="250" y2="72" stroke="#a855f7" stroke-width="1.5"/>
  `,
}

function pickSVG(name: string): string {
  const n = name.toLowerCase()
  if (n.includes('微服务') || n.includes('microservice')) return svgs.microservices
  if (n.includes('事件驱动') || n.includes('event')) return svgs.eventdriven
  if (n.includes('管道') || n.includes('过滤器') || n.includes('pipe')) return svgs.pipefilter
  if (n.includes('cqrs')) return svgs.cqrs
  if (n.includes('六边形') || n.includes('hexagonal')) return svgs.hexagonal
  if (n.includes('对等') || n.includes('p2p') || n.includes('peer')) return svgs.p2p
  if (n.includes('分层') || n.includes('layer')) return svgs.layered
  if (n.includes('mvc')) return svgs.mvc
  if (n.includes('soa')) return svgs.soa
  if (n.includes('插件') || n.includes('微内核') || n.includes('plugin') || n.includes('microkernel')) return svgs.plugin
  if (n.includes('serverless') || n.includes('无服务器')) return svgs.serverless
  if (n.includes('space') || n.includes('空间')) return svgs.spacebased
  return svgs.microservices
}

const selectedSVG = computed(() => pickSVG(props.archName))
</script>

<template>
  <div class="glass p-5 animate-in">
    <h3 class="text-lg font-bold text-slate-100 mb-4">🕸️ 架构拓扑图 — {{ archName }}</h3>
    <div class="bg-slate-950/50 rounded-xl border border-slate-700/30 overflow-hidden">
      <svg viewBox="0 0 380 260" class="w-full" v-html="selectedSVG" />
    </div>
  </div>
</template>
