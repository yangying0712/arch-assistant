<script setup lang="ts">
import type { Candidate } from './CandidateCards.vue'

defineProps<{ candidates: Candidate[] }>()
</script>

<template>
  <div v-if="candidates.length >= 2" class="glass p-5 animate-in border-purple-500/30"
       style="background: linear-gradient(135deg, rgba(30,41,59,0.7), rgba(26,16,64,0.7))">
    <h3 class="text-lg font-bold text-purple-300 mb-3">💡 推荐组合</h3>
    <p class="text-sm text-slate-300 leading-relaxed">
      ✨ <b class="text-amber-400">{{ candidates[0].name }}</b> 作为核心架构，
      配合 <b class="text-sky-400">{{ candidates[1].name }}</b> 处理特定场景。
      两者优势互补，可显著提升系统整体的可扩展性和灵活性。
    </p>
  </div>
</template>
