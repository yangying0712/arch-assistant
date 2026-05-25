<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{ archName: string }>()

const commonDefs = `
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
    <linearGradient id="panel-blue" x1="0" x2="1">
      <stop offset="0%" stop-color="#0f2a4a"/>
      <stop offset="100%" stop-color="#0b3b5f"/>
    </linearGradient>
    <linearGradient id="panel-amber" x1="0" x2="1">
      <stop offset="0%" stop-color="#92400e"/>
      <stop offset="100%" stop-color="#b45309"/>
    </linearGradient>
    <linearGradient id="panel-green" x1="0" x2="1">
      <stop offset="0%" stop-color="#047857"/>
      <stop offset="100%" stop-color="#0f766e"/>
    </linearGradient>
    <filter id="soft-shadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="6" stdDeviation="5" flood-color="#020617" flood-opacity=".38"/>
    </filter>
  </defs>
`

const diagrams: Record<string, string> = {
  cqrs: `
    ${commonDefs}
    <rect x="18" y="18" width="684" height="372" rx="18" fill="#071426" stroke="#1f3b5c"/>
    <rect x="40" y="42" width="640" height="58" rx="14" fill="#0c1f35" stroke="#274862"/>
    <text x="64" y="68" fill="#e0f2fe" font-size="15" font-weight="700">CQRS 读写分离拓扑</text>
    <text x="64" y="88" fill="#8fb3cf" font-size="11">命令侧处理业务一致性，查询侧服务高频读取，中间通过事件投影同步。</text>

    <rect x="64" y="132" width="112" height="46" rx="12" fill="#0e7490" filter="url(#soft-shadow)"/>
    <text x="120" y="160" text-anchor="middle" fill="#ecfeff" font-size="13" font-weight="700">Client / UI</text>

    <rect x="224" y="122" width="164" height="70" rx="14" fill="url(#panel-amber)" stroke="#f59e0b" filter="url(#soft-shadow)"/>
    <text x="306" y="148" text-anchor="middle" fill="#fff7ed" font-size="14" font-weight="800">命令处理层</text>
    <text x="306" y="169" text-anchor="middle" fill="#fde68a" font-size="11">Command Handler / Domain</text>

    <rect x="224" y="236" width="164" height="58" rx="14" fill="#111c31" stroke="#f59e0b" filter="url(#soft-shadow)"/>
    <text x="306" y="260" text-anchor="middle" fill="#fde68a" font-size="13" font-weight="700">写库</text>
    <text x="306" y="280" text-anchor="middle" fill="#94a3b8" font-size="11">事务边界 / 审计日志</text>

    <rect x="438" y="122" width="164" height="70" rx="14" fill="url(#panel-green)" stroke="#2dd4bf" filter="url(#soft-shadow)"/>
    <text x="520" y="148" text-anchor="middle" fill="#ecfdf5" font-size="14" font-weight="800">查询服务层</text>
    <text x="520" y="169" text-anchor="middle" fill="#a7f3d0" font-size="11">Query API / Read Model</text>

    <rect x="438" y="236" width="164" height="58" rx="14" fill="#111c31" stroke="#2dd4bf" filter="url(#soft-shadow)"/>
    <text x="520" y="260" text-anchor="middle" fill="#a7f3d0" font-size="13" font-weight="700">读库 / 缓存</text>
    <text x="520" y="280" text-anchor="middle" fill="#94a3b8" font-size="11">投影表 / 聚合视图</text>

    <rect x="286" y="326" width="236" height="38" rx="19" fill="#312e81" stroke="#818cf8"/>
    <text x="404" y="350" text-anchor="middle" fill="#ddd6fe" font-size="12" font-weight="700">事件总线：Domain Events / Projection</text>

    <path d="M176 148 C194 142, 204 140, 224 140" fill="none" stroke="#67e8f9" stroke-width="2.2" marker-end="url(#arrow-cyan)"/>
    <path d="M176 164 C282 215, 392 115, 438 142" fill="none" stroke="#67e8f9" stroke-width="2.2" stroke-dasharray="6 5" marker-end="url(#arrow-cyan)"/>
    <path d="M306 192 L306 236" fill="none" stroke="#fbbf24" stroke-width="2.2" marker-end="url(#arrow-amber)"/>
    <path d="M520 192 L520 236" fill="none" stroke="#34d399" stroke-width="2.2" marker-end="url(#arrow-green)"/>
    <path d="M388 265 C418 284, 438 285, 438 265" fill="none" stroke="#fbbf24" stroke-width="2" stroke-dasharray="7 6" marker-end="url(#arrow-amber)"/>
    <path d="M306 294 C310 330, 340 344, 286 345" fill="none" stroke="#fbbf24" stroke-width="1.8" marker-end="url(#arrow-amber)"/>
    <path d="M522 326 C550 313, 560 296, 546 294" fill="none" stroke="#34d399" stroke-width="1.8" marker-end="url(#arrow-green)"/>

    <rect x="64" y="314" width="154" height="50" rx="12" fill="#0f172a" stroke="#334155"/>
    <text x="141" y="336" text-anchor="middle" fill="#cbd5e1" font-size="12" font-weight="700">监控与治理</text>
    <text x="141" y="354" text-anchor="middle" fill="#64748b" font-size="10">Trace / Retry / Idempotency</text>
  `,
  microservices: `
    ${commonDefs}
    <rect x="18" y="18" width="684" height="312" rx="18" fill="#071426" stroke="#1f3b5c"/>
    <rect x="292" y="40" width="136" height="44" rx="12" fill="#0891b2" filter="url(#soft-shadow)"/>
    <text x="360" y="67" text-anchor="middle" fill="#ecfeff" font-size="14" font-weight="800">API Gateway</text>
    <g fill="#0e7490" filter="url(#soft-shadow)">
      <rect x="72" y="136" width="120" height="58" rx="14"/>
      <rect x="224" y="136" width="120" height="58" rx="14"/>
      <rect x="376" y="136" width="120" height="58" rx="14"/>
      <rect x="528" y="136" width="120" height="58" rx="14"/>
    </g>
    <text x="132" y="170" text-anchor="middle" fill="#fff" font-size="13" font-weight="700">商品服务</text>
    <text x="284" y="170" text-anchor="middle" fill="#fff" font-size="13" font-weight="700">订单服务</text>
    <text x="436" y="170" text-anchor="middle" fill="#fff" font-size="13" font-weight="700">支付服务</text>
    <text x="588" y="170" text-anchor="middle" fill="#fff" font-size="13" font-weight="700">用户服务</text>
    <path d="M360 84 L132 136 M360 84 L284 136 M360 84 L436 136 M360 84 L588 136" stroke="#67e8f9" stroke-width="2" marker-end="url(#arrow-cyan)"/>
    <rect x="108" y="238" width="504" height="48" rx="14" fill="#0f172a" stroke="#334155"/>
    <text x="360" y="267" text-anchor="middle" fill="#cbd5e1" font-size="12">服务发现 · 配置中心 · 容器编排 · 分布式追踪</text>
  `,
  event: `
    ${commonDefs}
    <rect x="18" y="18" width="684" height="312" rx="18" fill="#071426" stroke="#1f3b5c"/>
    <rect x="250" y="128" width="220" height="56" rx="18" fill="#6d28d9" stroke="#a78bfa" filter="url(#soft-shadow)"/>
    <text x="360" y="162" text-anchor="middle" fill="#fff" font-size="15" font-weight="800">事件总线 / Message Broker</text>
    <rect x="66" y="78" width="128" height="50" rx="14" fill="#7c3aed" filter="url(#soft-shadow)"/>
    <text x="130" y="108" text-anchor="middle" fill="#fff" font-size="13" font-weight="700">事件生产者</text>
    <rect x="66" y="202" width="128" height="50" rx="14" fill="#7c3aed" filter="url(#soft-shadow)"/>
    <text x="130" y="232" text-anchor="middle" fill="#fff" font-size="13" font-weight="700">业务服务</text>
    <rect x="526" y="78" width="128" height="50" rx="14" fill="#4f46e5" filter="url(#soft-shadow)"/>
    <text x="590" y="108" text-anchor="middle" fill="#fff" font-size="13" font-weight="700">订阅者 A</text>
    <rect x="526" y="202" width="128" height="50" rx="14" fill="#4f46e5" filter="url(#soft-shadow)"/>
    <text x="590" y="232" text-anchor="middle" fill="#fff" font-size="13" font-weight="700">订阅者 B</text>
    <path d="M194 103 C235 120, 240 136, 250 145 M194 227 C235 205, 238 186, 250 171 M470 145 C500 130, 502 116, 526 103 M470 171 C506 190, 506 212, 526 227" fill="none" stroke="#c4b5fd" stroke-width="2" marker-end="url(#arrow-cyan)"/>
  `,
  default: `
    ${commonDefs}
    <rect x="18" y="18" width="684" height="292" rx="18" fill="#071426" stroke="#1f3b5c"/>
    <rect x="76" y="62" width="568" height="56" rx="16" fill="#0e7490" filter="url(#soft-shadow)"/>
    <text x="360" y="96" text-anchor="middle" fill="#fff" font-size="15" font-weight="800">架构核心组件</text>
    <rect x="110" y="178" width="180" height="58" rx="14" fill="#0f172a" stroke="#334155"/>
    <text x="200" y="212" text-anchor="middle" fill="#cbd5e1" font-size="13" font-weight="700">接口层</text>
    <rect x="430" y="178" width="180" height="58" rx="14" fill="#0f172a" stroke="#334155"/>
    <text x="520" y="212" text-anchor="middle" fill="#cbd5e1" font-size="13" font-weight="700">数据层</text>
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
    <div class="overflow-hidden rounded-lg border border-white/10 bg-slate-950/60">
      <svg viewBox="0 0 720 410" class="h-auto w-full topology-svg" v-html="selectedSVG" />
    </div>
  </section>
</template>
