<script setup lang="ts">
defineProps<{ features: string[] }>()
</script>

<template>
  <div class="glass p-5 animate-in">
    <h3 class="text-sm font-semibold text-blue-300 mb-3 flex items-center gap-2">
      <span>🤖</span> 语义理解与特征提取
    </h3>
    <div class="flex flex-wrap gap-2">
      <span
        v-for="(f, i) in features"
        :key="i"
        class="px-3 py-1.5 bg-blue-500/10 text-blue-300 rounded-lg text-xs font-medium border border-blue-500/20"
      >
        {{ f }}
      </span>
    </div>
  </div>
</template>
