<script setup lang="ts">
import { computed, ref } from 'vue'
import axios from 'axios'
import InputPanel from './components/InputPanel.vue'
import FeatureTags from './components/FeatureTags.vue'
import CandidateCards from './components/CandidateCards.vue'
import RadarChart from './components/RadarChart.vue'
import TopologyDiagram from './components/TopologyDiagram.vue'
import DecisionTrace from './components/DecisionTrace.vue'
import ComboRec from './components/ComboRec.vue'
import ReportPanel from './components/ReportPanel.vue'
import type { Candidate } from './components/CandidateCards.vue'

interface AnalysisResult {
  features: { features?: string[]; constraints?: Record<string, string>; domain?: string } | null
  candidates: Candidate[] | null
  report: string | null
  cached: boolean
}

const result = ref<AnalysisResult | null>(null)
const loading = ref(false)
const topArchName = ref('')

const topCandidate = computed(() => result.value?.candidates?.[0])
const featureCount = computed(() => result.value?.features?.features?.length ?? 0)

async function runAnalysis(prompt: string, sessionId: string) {
  loading.value = true
  result.value = null
  topArchName.value = ''

  try {
    const sseRes = await fetch('/api/v1/analyze/stream', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prompt, session_id: sessionId }),
    })

    if (sseRes.ok && sseRes.body) {
      const reader = sseRes.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''
      const data: Partial<AnalysisResult> = { features: null, candidates: [], report: null }

      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() || ''

        for (const line of lines) {
          if (!line.startsWith('data: ')) continue
          try {
            const event = JSON.parse(line.slice(6))
            if (event.event === 'features') data.features = event.data
            if (event.event === 'candidates') data.candidates = event.data
            if (event.event === 'report') data.report = event.data
          } catch {
            // Ignore incomplete SSE frames.
          }
        }
      }

      result.value = {
        features: data.features ?? null,
        candidates: data.candidates ?? [],
        report: data.report ?? null,
        cached: false,
      }
    } else {
      throw new Error(`SSE failed: ${sseRes.status}`)
    }
  } catch {
    try {
      const res = await axios.post('/api/v1/analyze', { prompt, session_id: sessionId })
      result.value = {
        features: res.data.features,
        candidates: res.data.candidates || [],
        report: res.data.report || null,
        cached: res.data.cached || false,
      }
    } catch (e: any) {
      result.value = {
        features: null,
        candidates: [],
        report: '请求失败：' + (e.response?.data?.detail || e.message),
        cached: false,
      }
    }
  } finally {
    loading.value = false
    if (result.value?.candidates?.length) {
      topArchName.value = result.value.candidates[0].name
    }
  }
}
</script>

<template>
  <div class="min-h-screen app-shell text-slate-100">
    <header class="sticky top-0 z-50 border-b border-white/10 bg-[#09111f]/90 backdrop-blur-xl">
      <div class="mx-auto flex max-w-7xl items-center justify-between gap-4 px-4 py-3 sm:px-6">
        <div class="flex items-center gap-3">
          <div class="flex h-9 w-9 items-center justify-center rounded-lg bg-cyan-500 text-sm font-black text-slate-950 shadow-lg shadow-cyan-500/25">
            AA
          </div>
          <div>
            <h1 class="text-base font-bold tracking-normal text-white">Architecture Assistant</h1>
            <p class="text-xs text-slate-400">软件架构风格智能助手 · 多 Agent 决策工作台</p>
          </div>
        </div>
        <div class="flex items-center gap-2 text-xs">
          <span class="hidden rounded border border-emerald-400/20 bg-emerald-400/10 px-2 py-1 text-emerald-200 sm:inline-flex">
            4 个微服务
          </span>
          <span class="hidden rounded border border-cyan-400/20 bg-cyan-400/10 px-2 py-1 text-cyan-200 sm:inline-flex">
            3 个智能体
          </span>
          <span v-if="result?.cached" class="rounded border border-amber-400/30 bg-amber-400/10 px-2 py-1 text-amber-200">
            缓存命中
          </span>
        </div>
      </div>
    </header>

    <main class="mx-auto grid max-w-7xl grid-cols-1 gap-6 px-4 py-6 sm:px-6 lg:grid-cols-12">
      <section class="lg:col-span-5 xl:col-span-4">
        <div class="sticky top-20 space-y-4">
          <InputPanel @submit="runAnalysis" @call-utterance="runAnalysis" />
        </div>
      </section>

      <section class="space-y-5 lg:col-span-7 xl:col-span-8">
        <div v-if="!result && !loading" class="hero-panel overflow-hidden rounded-lg border border-white/10 p-6 sm:p-8">
          <div class="max-w-2xl">
            <p class="mb-3 text-xs font-semibold uppercase tracking-[0.18em] text-cyan-200">Architecture Decision Support</p>
            <h2 class="max-w-2xl text-2xl font-bold text-white sm:text-3xl">从自然语言需求到可解释的架构推荐</h2>
            <p class="mt-3 max-w-xl text-sm leading-7 text-slate-300">
              输入业务场景后，系统会提取关键约束、排序候选架构、生成对比矩阵、拓扑图和决策溯源，用于课程演示和架构选型说明。
            </p>
          </div>
          <div class="mt-8 grid grid-cols-1 gap-3 sm:grid-cols-3">
            <div class="metric-card">
              <span class="metric-value">12</span>
              <span class="metric-label">架构风格知识库</span>
            </div>
            <div class="metric-card">
              <span class="metric-value">20</span>
              <span class="metric-label">典型测试场景</span>
            </div>
            <div class="metric-card">
              <span class="metric-value">95%</span>
              <span class="metric-label">当前回归准确率</span>
            </div>
          </div>
        </div>

        <div v-if="loading" class="grid gap-4">
          <div v-for="i in 3" :key="i" class="glass p-5">
            <div class="mb-4 h-4 w-1/3 rounded bg-slate-700/60" />
            <div class="space-y-2">
              <div class="h-3 w-full rounded bg-slate-800" />
              <div class="h-3 w-2/3 rounded bg-slate-800" />
            </div>
          </div>
        </div>

        <template v-if="result">
          <div class="grid grid-cols-1 gap-3 md:grid-cols-3">
            <div class="summary-tile">
              <span class="summary-label">首选架构</span>
              <strong>{{ topCandidate?.name || '暂无' }}</strong>
            </div>
            <div class="summary-tile">
              <span class="summary-label">匹配度</span>
              <strong>{{ topCandidate ? `${(topCandidate.match_score * 100).toFixed(0)}%` : '--' }}</strong>
            </div>
            <div class="summary-tile">
              <span class="summary-label">提取特征</span>
              <strong>{{ featureCount }} 项</strong>
            </div>
          </div>

          <FeatureTags v-if="result.features?.features?.length" :features="result.features.features" />
          <CandidateCards v-if="result.candidates?.length" :candidates="result.candidates" />
          <div class="grid grid-cols-1 gap-5 xl:grid-cols-2">
            <RadarChart v-if="result.candidates?.length" :candidates="result.candidates" />
            <TopologyDiagram v-if="topArchName" :arch-name="topArchName" />
          </div>
          <DecisionTrace v-if="result.candidates?.length" :candidates="result.candidates" />
          <ComboRec v-if="result.candidates?.length" :candidates="result.candidates" />
          <ReportPanel v-if="result.report" :report="result.report" />
        </template>
      </section>
    </main>
  </div>
</template>
