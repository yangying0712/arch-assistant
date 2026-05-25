<script setup lang="ts">
import type { Candidate } from './CandidateCards.vue'

defineProps<{ candidates: Candidate[] }>()

function shortName(name: string) {
  return name.replace(/\s*\(.+?\)/g, '').trim()
}
</script>

<template>
  <section v-if="candidates.length >= 2" class="combo-panel animate-in">
    <div>
      <p class="text-xs font-semibold uppercase tracking-[0.16em] text-indigo-200">Combination</p>
      <h3 class="mt-1 text-lg font-bold text-white">推荐组合方案</h3>
      <p class="mt-3 text-sm leading-7 text-indigo-100/90">
        以 <b class="text-cyan-100">{{ shortName(candidates[0].name) }}</b> 作为核心架构，
        搭配 <b class="text-violet-100">{{ shortName(candidates[1].name) }}</b> 处理专项能力。
        这种组合能兼顾主流程稳定性与局部扩展弹性，适合在答辩中说明架构演进路径。
      </p>
    </div>
  </section>
</template>
