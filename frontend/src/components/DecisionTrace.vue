<script setup lang="ts">
import type { Candidate } from './CandidateCards.vue'

defineProps<{ candidates: Candidate[] }>()
</script>

<template>
  <div v-if="candidates.length >= 1" class="glass p-5 animate-in">
    <h3 class="text-lg font-bold text-slate-100 mb-4">🔗 决策溯源</h3>
    <div class="space-y-3">
      <div
        v-for="(reason, i) in candidates[0]?.match_reasons || []"
        :key="i"
        class="flex items-start gap-3 p-3 bg-slate-800/40 rounded-lg border border-slate-700/30"
      >
        <span class="text-amber-400 font-bold shrink-0 mt-0.5">{{ i + 1 }} →</span>
        <span class="text-sm text-slate-300">{{ reason }}</span>
      </div>
      <div
        v-if="candidates.length > 1 && candidates[1]?.risks"
        class="flex items-start gap-3 p-3 bg-red-900/10 rounded-lg border border-red-500/20"
      >
        <span class="text-red-400 font-bold shrink-0 mt-0.5">✕</span>
        <span class="text-sm text-red-300">
          排除 <b>{{ candidates[1].name }}</b>：
          {{ candidates[1].risks!.slice(0, 2).join('；') }}
        </span>
      </div>
    </div>
  </div>
</template>
