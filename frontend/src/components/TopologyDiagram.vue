<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{ archName: string }>()

const defs = `
  <defs>
    <marker id="arrow-cyan" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto">
      <path d="M0,0 L9,4.5 L0,9 Z" fill="#67e8f9"/>
    </marker>
    <marker id="arrow-amber" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto">
      <path d="M0,0 L9,4.5 L0,9 Z" fill="#fbbf24"/>
    </marker>
    <marker id="arrow-green" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto">
      <path d="M0,0 L9,4.5 L0,9 Z" fill="#34d399"/>
    </marker>
    <linearGradient id="node-blue" x1="0" x2="1">
      <stop offset="0%" stop-color="#0891b2"/>
      <stop offset="100%" stop-color="#2563eb"/>
    </linearGradient>
    <linearGradient id="node-amber" x1="0" x2="1">
      <stop offset="0%" stop-color="#b45309"/>
      <stop offset="100%" stop-color="#d97706"/>
    </linearGradient>
    <linearGradient id="node-green" x1="0" x2="1">
      <stop offset="0%" stop-color="#059669"/>
      <stop offset="100%" stop-color="#0d9488"/>
    </linearGradient>
    <linearGradient id="node-violet" x1="0" x2="1">
      <stop offset="0%" stop-color="#7c3aed"/>
      <stop offset="100%" stop-color="#4f46e5"/>
    </linearGradient>
    <filter id="soft-shadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="8" stdDeviation="7" flood-color="#020617" flood-opacity=".34"/>
    </filter>
  </defs>
`

const diagrams: Record<string, string> = {
  cqrs: `
    ${defs}
    <rect x="18" y="18" width="684" height="372" rx="18" fill="#071426" stroke="#1f3b5c"/>
    <rect x="46" y="42" width="628" height="58" rx="14" fill="#0c1f35" stroke="#274862"/>
    <text x="70" y="67" fill="#e0f2fe" font-size="15" font-weight="800">CQRS 读写分离拓扑</text>
    <text x="70" y="88" fill="#93c5fd" font-size="11">命令侧保证业务一致性，查询侧承接高频读取，通过事件投影同步读模型。</text>

    <rect x="64" y="136" width="116" height="48" rx="14" fill="url(#node-blue)" filter="url(#soft-shadow)"/>
    <text x="122" y="165" text-anchor="middle" fill="#ecfeff" font-size="13" font-weight="800">Client / API</text>

    <rect x="226" y="122" width="164" height="72" rx="16" fill="url(#node-amber)" stroke="#fbbf24" filter="url(#soft-shadow)"/>
    <text x="308" y="149" text-anchor="middle" fill="#fff7ed" font-size="14" font-weight="800">命令处理层</text>
    <text x="308" y="170" text-anchor="middle" fill="#fde68a" font-size="11">Command Handler</text>

    <rect x="438" y="122" width="164" height="72" rx="16" fill="url(#node-green)" stroke="#2dd4bf" filter="url(#soft-shadow)"/>
    <text x="520" y="149" text-anchor="middle" fill="#ecfdf5" font-size="14" font-weight="800">查询服务层</text>
    <text x="520" y="170" text-anchor="middle" fill="#a7f3d0" font-size="11">Query API / Read Model</text>

    <rect x="226" y="244" width="164" height="58" rx="14" fill="#111c31" stroke="#f59e0b" filter="url(#soft-shadow)"/>
    <text x="308" y="268" text-anchor="middle" fill="#fde68a" font-size="13" font-weight="800">Write DB</text>
    <text x="308" y="287" text-anchor="middle" fill="#94a3b8" font-size="10">事务边界 / 审计日志</text>

    <rect x="438" y="244" width="164" height="58" rx="14" fill="#111c31" stroke="#2dd4bf" filter="url(#soft-shadow)"/>
    <text x="520" y="268" text-anchor="middle" fill="#a7f3d0" font-size="13" font-weight="800">Read DB / Cache</text>
    <text x="520" y="287" text-anchor="middle" fill="#94a3b8" font-size="10">投影视图 / 聚合查询</text>

    <rect x="285" y="328" width="242" height="38" rx="19" fill="#312e81" stroke="#818cf8"/>
    <text x="406" y="352" text-anchor="middle" fill="#ddd6fe" font-size="12" font-weight="800">Domain Events / Projection</text>

    <path d="M180 152 C198 145, 210 143, 226 143" fill="none" stroke="#67e8f9" stroke-width="2.3" marker-end="url(#arrow-cyan)"/>
    <path d="M180 170 C288 222, 392 119, 438 145" fill="none" stroke="#67e8f9" stroke-width="2.3" stroke-dasharray="7 6" marker-end="url(#arrow-cyan)"/>
    <path d="M308 194 L308 244" fill="none" stroke="#fbbf24" stroke-width="2.4" marker-end="url(#arrow-amber)"/>
    <path d="M520 194 L520 244" fill="none" stroke="#34d399" stroke-width="2.4" marker-end="url(#arrow-green)"/>
    <path d="M390 272 C414 292, 438 292, 438 272" fill="none" stroke="#fbbf24" stroke-width="2" stroke-dasharray="7 6" marker-end="url(#arrow-amber)"/>
    <path d="M308 302 C310 330, 340 347, 285 347" fill="none" stroke="#fbbf24" stroke-width="1.8" marker-end="url(#arrow-amber)"/>
    <path d="M527 347 C560 330, 560 305, 548 302" fill="none" stroke="#34d399" stroke-width="1.8" marker-end="url(#arrow-green)"/>
  `,
  microservices: `
    ${defs}
    <rect x="18" y="18" width="684" height="312" rx="18" fill="#071426" stroke="#1f3b5c"/>
    <rect x="292" y="42" width="136" height="48" rx="14" fill="url(#node-blue)" filter="url(#soft-shadow)"/>
    <text x="360" y="72" text-anchor="middle" fill="#ecfeff" font-size="14" font-weight="800">API Gateway</text>
    <g fill="url(#node-green)" filter="url(#soft-shadow)">
      <rect x="70" y="140" width="122" height="58" rx="14"/>
      <rect x="224" y="140" width="122" height="58" rx="14"/>
      <rect x="378" y="140" width="122" height="58" rx="14"/>
      <rect x="532" y="140" width="122" height="58" rx="14"/>
    </g>
    <text x="131" y="174" text-anchor="middle" fill="#fff" font-size="13" font-weight="800">商品服务</text>
    <text x="285" y="174" text-anchor="middle" fill="#fff" font-size="13" font-weight="800">订单服务</text>
    <text x="439" y="174" text-anchor="middle" fill="#fff" font-size="13" font-weight="800">支付服务</text>
    <text x="593" y="174" text-anchor="middle" fill="#fff" font-size="13" font-weight="800">用户服务</text>
    <path d="M360 90 L131 140 M360 90 L285 140 M360 90 L439 140 M360 90 L593 140" stroke="#67e8f9" stroke-width="2" marker-end="url(#arrow-cyan)"/>
    <rect x="108" y="240" width="504" height="48" rx="14" fill="#0f172a" stroke="#334155"/>
    <text x="360" y="269" text-anchor="middle" fill="#cbd5e1" font-size="12">服务发现 · 配置中心 · 容器编排 · 分布式追踪</text>
  `,
  event: `
    ${defs}
    <rect x="18" y="18" width="684" height="312" rx="18" fill="#071426" stroke="#1f3b5c"/>
    <rect x="250" y="128" width="220" height="56" rx="18" fill="url(#node-violet)" stroke="#a78bfa" filter="url(#soft-shadow)"/>
    <text x="360" y="162" text-anchor="middle" fill="#fff" font-size="15" font-weight="800">事件总线 / Message Broker</text>
    <rect x="66" y="78" width="128" height="50" rx="14" fill="#7c3aed" filter="url(#soft-shadow)"/>
    <text x="130" y="108" text-anchor="middle" fill="#fff" font-size="13" font-weight="800">事件生产者</text>
    <rect x="66" y="202" width="128" height="50" rx="14" fill="#7c3aed" filter="url(#soft-shadow)"/>
    <text x="130" y="232" text-anchor="middle" fill="#fff" font-size="13" font-weight="800">业务服务</text>
    <rect x="526" y="78" width="128" height="50" rx="14" fill="#4f46e5" filter="url(#soft-shadow)"/>
    <text x="590" y="108" text-anchor="middle" fill="#fff" font-size="13" font-weight="800">订阅者 A</text>
    <rect x="526" y="202" width="128" height="50" rx="14" fill="#4f46e5" filter="url(#soft-shadow)"/>
    <text x="590" y="232" text-anchor="middle" fill="#fff" font-size="13" font-weight="800">订阅者 B</text>
    <path d="M194 103 C235 120, 240 136, 250 145 M194 227 C235 205, 238 186, 250 171 M470 145 C500 130, 502 116, 526 103 M470 171 C506 190, 506 212, 526 227" fill="none" stroke="#c4b5fd" stroke-width="2" marker-end="url(#arrow-cyan)"/>
  `,
  default: `
    ${defs}
    <rect x="18" y="18" width="684" height="292" rx="18" fill="#071426" stroke="#1f3b5c"/>
    <rect x="76" y="62" width="568" height="56" rx="16" fill="url(#node-blue)" filter="url(#soft-shadow)"/>
    <text x="360" y="96" text-anchor="middle" fill="#fff" font-size="15" font-weight="800">架构核心组件</text>
    <rect x="110" y="178" width="180" height="58" rx="14" fill="#0f172a" stroke="#334155"/>
    <text x="200" y="212" text-anchor="middle" fill="#cbd5e1" font-size="13" font-weight="800">接口层</text>
    <rect x="430" y="178" width="180" height="58" rx="14" fill="#0f172a" stroke="#334155"/>
    <text x="520" y="212" text-anchor="middle" fill="#cbd5e1" font-size="13" font-weight="800">数据层</text>
    <path d="M290 207 L430 207" stroke="#67e8f9" stroke-width="2" marker-end="url(#arrow-cyan)"/>
  `,
}

function pickKey(name: string) {
  const normalized = name.toLowerCase()
  if (normalized.includes('cqrs')) return 'cqrs'
  if (normalized.includes('microservice') || name.includes('微服务')) return 'microservices'
  if (normalized.includes('event') || name.includes('事件')) return 'event'
  return 'default'
}

const selectedSVG = computed(() => diagrams[pickKey(props.archName)] ?? diagrams.default)
</script>

<template>
  <section class="glass p-5 animate-in">
    <div class="mb-4">
      <p class="text-xs font-semibold uppercase tracking-[0.16em] text-cyan-200">Topology</p>
      <h3 class="mt-1 text-lg font-bold text-white">架构拓扑图</h3>
      <p class="mt-1 text-xs text-slate-400">{{ archName }}</p>
    </div>
    <div class="overflow-hidden rounded-lg border border-white/10 bg-slate-950/50">
      <svg viewBox="0 0 720 410" class="h-auto w-full topology-svg" v-html="selectedSVG" />
    </div>
  </section>
</template>
