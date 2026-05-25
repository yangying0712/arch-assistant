<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{ report: string }>()

function renderMarkdown(text: string): string {
  if (!text) return ''
  let html = text
  // Code blocks
  html = html.replace(/```(\w*)\n([\s\S]*?)```/g,
    '<pre style="background:#0f172a;padding:12px;border-radius:8px;overflow-x:auto;font-size:12px;border:1px solid #1e293b"><code>$2</code></pre>')
  html = html.replace(/`([^`]+)`/g,
    '<code style="background:#1e293b;padding:1px 5px;border-radius:3px;font-size:12px;color:#e2e8f0">$1</code>')
  // Headers
  html = html.replace(/^#### (.+)$/gm, '<h5 style="color:#93c5fd;margin:8px 0 3px;font-size:13px">$1</h5>')
  html = html.replace(/^### (.+)$/gm, '<h4 style="color:#93c5fd;margin:10px 0 4px">$1</h4>')
  html = html.replace(/^## (.+)$/gm, '<h3 style="color:#60a5fa;margin:14px 0 8px;font-size:16px;font-weight:700">$1</h3>')
  html = html.replace(/^# (.+)$/gm, '<h2 style="color:#3b82f6;margin:16px 0 10px;font-size:18px;font-weight:700">$1</h2>')
  // Bold & italic
  html = html.replace(/\*\*\*(.+?)\*\*\*/g, '<strong><em>$1</em></strong>')
  html = html.replace(/\*\*(.+?)\*\*/g, '<strong style="color:#f1f5f9">$1</strong>')
  html = html.replace(/\*(.+?)\*/g, '<em>$1</em>')
  // Lists
  html = html.replace(/^- (.+)$/gm, '<li style="margin:2px 0">$1</li>')
  html = html.replace(/^\d+\. (.+)$/gm, '<li style="margin:2px 0">$1</li>')
  html = html.replace(/((?:<li[^>]*>.*?<\/li>\n?)+)/g,
    '<ul style="padding-left:20px;margin:6px 0">$1</ul>')
  // Horizontal rules
  html = html.replace(/^---$/gm, '<hr style="border-color:#334155;margin:12px 0">')
  // Line breaks
  html = html.replace(/\n\n/g, '<br><br>')
  return html
}

const reportHtml = computed(() => renderMarkdown(props.report))
</script>

<template>
  <div class="glass p-5 animate-in">
    <h3 class="text-lg font-bold text-slate-100 mb-4">📋 评估报告</h3>
    <div
      class="text-sm text-slate-300 leading-relaxed space-y-2 md-content"
      v-html="reportHtml"
    />
  </div>
</template>
