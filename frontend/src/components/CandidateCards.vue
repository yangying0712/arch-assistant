<script setup lang="ts">
export interface Candidate {
  name: string
  match_score: number
  match_reasons?: string[]
  risks?: string[]
  rule_engine_note?: string
}

defineProps<{ candidates: Candidate[] }>()

const rankClasses = ['rank-1', 'rank-2', 'rank-3']
const medals = ['🥇', '🥈', '🥉']
const rankColors = [
  'from-amber-500/20 to-amber-600/10 border-amber-500/40',
  'from-slate-400/15 to-slate-500/10 border-slate-400/30',
  'from-orange-500/15 to-orange-600/10 border-orange-500/30',
]
</script>

<template>
  <div class="animate-in">
    <h3 class="text-lg font-bold text-slate-100 mb-4 flex items-center gap-2">
      <span>🏆</span> 推荐架构对比
    </h3>
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div
        v-for="(c, i) in candidates"
        :key="c.name"
        :class="['glass glass-hover p-5 border-2', rankClasses[i] || '']"
      >
        <div class="flex justify-between items-start mb-3">
          <h4 class="text-lg font-bold text-slate-100">{{ c.name }}</h4>
          <span class="text-2xl">{{ medals[i] || '' }}</span>
        </div>
        <!-- Score Bar -->
        <div class="mb-3">
          <div class="flex justify-between text-xs text-slate-400 mb-1">
            <span>匹配度</span>
            <span>{{ (c.match_score * 100).toFixed(0) }}%</span>
          </div>
          <div class="h-2 bg-slate-700/50 rounded-full overflow-hidden">
            <div
              class="h-full rounded-full transition-all duration-1000"
              :class="i === 0 ? 'bg-amber-500' : i === 1 ? 'bg-slate-400' : 'bg-orange-500'"
              :style="{ width: (c.match_score * 100) + '%' }"
            />
          </div>
        </div>
        <!-- Note -->
        <p v-if="c.rule_engine_note" class="text-xs text-amber-400 mb-2">
          ⚡ {{ c.rule_engine_note }}
        </p>
        <!-- Reasons -->
        <div v-if="c.match_reasons?.length" class="mb-2">
          <p class="text-xs text-slate-400 mb-1">推荐理由</p>
          <ul class="space-y-1">
            <li v-for="(r, j) in c.match_reasons.slice(0, 2)" :key="j"
                class="text-xs text-slate-300 flex gap-1">
              <span class="text-green-400 shrink-0">✓</span> {{ r }}
            </li>
          </ul>
        </div>
        <!-- Risks -->
        <div v-if="c.risks?.length">
          <p class="text-xs text-slate-400 mb-1">注意事项</p>
          <ul class="space-y-1">
            <li v-for="(r, j) in c.risks.slice(0, 2)" :key="j"
                class="text-xs text-red-300 flex gap-1">
              <span class="text-red-400 shrink-0">!</span> {{ r }}
            </li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>
