<script setup lang="ts">
import type { Candidate } from './CandidateCards.vue'

defineProps<{ candidates: Candidate[] }>()
</script>

<template>
  <section v-if="candidates.length" class="glass p-5 animate-in">
    <div class="mb-4">
      <p class="text-xs font-semibold uppercase tracking-[0.16em] text-cyan-200">Decision Trace</p>
      <h3 class="mt-1 text-lg font-bold text-white">决策溯源</h3>
    </div>

    <div class="space-y-3">
      <div
        v-for="(reason, index) in candidates[0]?.match_reasons || []"
        :key="reason"
        class="trace-row"
      >
        <span class="trace-index">{{ index + 1 }}</span>
        <span class="text-sm leading-6 text-slate-300">{{ reason }}</span>
      </div>

      <div v-if="candidates.length > 1 && candidates[1]?.risks?.length" class="trace-row trace-risk">
        <span class="trace-index">!</span>
        <span class="text-sm leading-6 text-rose-100">
          备选方案 <b>{{ candidates[1].name }}</b> 的主要风险：
          {{ candidates[1].risks.slice(0, 2).join('；') }}
        </span>
      </div>
    </div>
  </section>
</template>
