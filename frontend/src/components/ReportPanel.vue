<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{ report: string }>()

function escapeHtml(value: string) {
  return value
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
}

function inlineMarkdown(value: string) {
  return escapeHtml(value)
    .replace(/`([^`]+)`/g, '<code>$1</code>')
    .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
    .replace(/\*([^*]+)\*/g, '<em>$1</em>')
}

function tableToHtml(lines: string[]) {
  const rows = lines
    .filter(line => !/^\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?\s*$/.test(line))
    .map(line => line.trim().replace(/^\|/, '').replace(/\|$/, '').split('|').map(cell => inlineMarkdown(cell.trim())))

  if (!rows.length) return ''

  const [head, ...body] = rows
  const thead = `<thead><tr>${head.map(cell => `<th>${cell}</th>`).join('')}</tr></thead>`
  const tbody = `<tbody>${body.map(row => `<tr>${row.map(cell => `<td>${cell}</td>`).join('')}</tr>`).join('')}</tbody>`
  return `<div class="report-table-wrap"><table>${thead}${tbody}</table></div>`
}

function renderMarkdown(text: string): string {
  if (!text) return ''

  const normalized = text
    .replace(/\r\n/g, '\n')
    .replace(/^好的[，,].{0,160}?报告[。.]?\s*/s, '')
    .replace(/\n{3,}/g, '\n\n')

  const lines = normalized.split('\n')
  const output: string[] = []
  let listItems: string[] = []
  let tableLines: string[] = []

  function flushList() {
    if (!listItems.length) return
    output.push(`<ul>${listItems.map(item => `<li>${item}</li>`).join('')}</ul>`)
    listItems = []
  }

  function flushTable() {
    if (!tableLines.length) return
    output.push(tableToHtml(tableLines))
    tableLines = []
  }

  function flushBlocks() {
    flushList()
    flushTable()
  }

  for (const rawLine of lines) {
    const line = rawLine.trim()

    if (!line) {
      flushBlocks()
      continue
    }

    if (line.includes('|') && line.split('|').length >= 3) {
      flushList()
      tableLines.push(line)
      continue
    }

    flushTable()

    if (/^-{3,}$/.test(line)) {
      flushList()
      output.push('<hr>')
      continue
    }

    const heading = line.match(/^(#{1,4})\s+(.+)$/)
    if (heading) {
      flushList()
      const level = Math.min(heading[1].length + 1, 4)
      output.push(`<h${level}>${inlineMarkdown(heading[2])}</h${level}>`)
      continue
    }

    if (/^([一二三四五六七八九十]+|[IVX]+|\d+)[、.．]\s*\S+/.test(line)) {
      flushList()
      output.push(`<h3>${inlineMarkdown(line)}</h3>`)
      continue
    }

    const bullet = line.match(/^[-*]\s+(.+)$/)
    const ordered = line.match(/^\d+[.、]\s+(.+)$/)
    if (bullet || ordered) {
      listItems.push(inlineMarkdown((bullet || ordered)![1]))
      continue
    }

    flushList()
    output.push(`<p>${inlineMarkdown(line)}</p>`)
  }

  flushBlocks()
  return output.join('')
}

const reportHtml = computed(() => renderMarkdown(props.report))
</script>

<template>
  <section class="glass p-5 animate-in">
    <div class="mb-4">
      <p class="text-xs font-semibold uppercase tracking-[0.16em] text-cyan-200">Evaluation Report</p>
      <h3 class="mt-1 text-lg font-bold text-white">专业评估报告</h3>
    </div>
    <div class="md-content report-content text-sm leading-7 text-slate-300" v-html="reportHtml" />
  </section>
</template>
