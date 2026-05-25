<script setup lang="ts">
import { ref, provide } from 'vue'
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
  features: { features?: string[] } | null
  candidates: Candidate[] | null
  report: string | null
  cached: boolean
}

const result = ref<AnalysisResult | null>(null)
const loading = ref(false)

const topArchName = ref('')

async function runAnalysis(prompt: string, sessionId: string) {
  loading.value = true
  result.value = null

  try {
    // Try SSE streaming first for real-time progress
    const sseRes = await fetch('/api/v1/analyze/stream', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prompt, session_id: sessionId }),
    })

    if (sseRes.ok) {
      const reader = sseRes.body!.getReader()
      const decoder = new TextDecoder()
      let buffer = ''
      const data: any = { features: null, candidates: null, report: null }

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
          } catch { /* skip parse errors */ }
        }
      }

      result.value = {
        features: data.features,
        candidates: data.candidates || [],
        report: data.report || null,
        cached: false,
      }
    } else {
      throw new Error(`SSE failed: ${sseRes.status}`)
    }
  } catch {
    // Fallback to regular endpoint
    try {
      const res = await axios.post('/api/v1/analyze', { prompt, session_id: sessionId })
      result.value = {
        features: res.data.features,
        candidates: res.data.candidates || [],
        report: res.data.report || null,
        cached: res.data.cached || false,
      }
    } catch (e: any) {
      console.error('API error:', e)
      result.value = {
        features: null,
        candidates: [],
        report: '❌ 请求失败: ' + (e.response?.data?.detail || e.message),
        cached: false,
      }
    }
  } finally {
    loading.value = false
    // Set top arch for topology
    if (result.value?.candidates?.length) {
      topArchName.value = result.value.candidates[0].name
    }
  }
}
</script>

<template>
  <div class="min-h-screen bg-slate-950">
    <!-- Header -->
    <header class="glass border-b border-blue-500/10 sticky top-0 z-50">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 py-3 flex items-center justify-between">
        <div class="flex items-center gap-3">
          <div class="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white font-bold text-sm">
            A
          </div>
          <div>
            <h1 class="text-base font-bold text-slate-100">Architecture Assistant</h1>
            <p class="text-xs text-slate-500">软件架构风格智能助手 · Vue 3</p>
          </div>
        </div>
        <div class="flex items-center gap-3 text-xs text-slate-500">
          <span v-if="result?.cached" class="px-2 py-0.5 bg-amber-500/10 text-amber-400 rounded border border-amber-500/20">
            ⚡ 缓存命中
          </span>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main class="max-w-7xl mx-auto px-4 sm:px-6 py-6">
      <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
        <!-- Left: Input + Progress -->
        <div class="lg:col-span-5 space-y-4">
          <InputPanel @submit="runAnalysis" @call-utterance="runAnalysis" />
        </div>

        <!-- Right: Results -->
        <div class="lg:col-span-7 space-y-5">
          <!-- Empty State -->
          <div v-if="!result && !loading" class="glass p-12 text-center">
            <div class="text-5xl mb-4">🏗️</div>
            <h2 class="text-xl font-bold text-slate-300 mb-2">软件架构风格智能助手</h2>
            <p class="text-sm text-slate-500 max-w-md mx-auto">
              在左侧输入你的软件需求描述，AI 将自动提取特征、
              匹配最合适的架构风格，并生成专业评估报告。
            </p>
          </div>

          <!-- Loading Skeleton -->
          <div v-if="loading" class="space-y-4">
            <div v-for="i in 3" :key="i" class="glass p-5 animate-pulse">
              <div class="h-4 bg-slate-700/50 rounded w-1/3 mb-4" />
              <div class="space-y-2">
                <div class="h-3 bg-slate-700/30 rounded w-full" />
                <div class="h-3 bg-slate-700/30 rounded w-2/3" />
              </div>
            </div>
          </div>

          <!-- Results -->
          <template v-if="result">
            <!-- Features -->
            <FeatureTags
              v-if="result.features?.features?.length"
              :features="result.features.features"
            />

            <!-- Candidates -->
            <CandidateCards
              v-if="result.candidates?.length"
              :candidates="result.candidates"
            />

            <!-- Radar Chart -->
            <RadarChart
              v-if="result.candidates?.length"
              :candidates="result.candidates"
            />

            <!-- Topology -->
            <TopologyDiagram
              v-if="topArchName"
              :arch-name="topArchName"
            />

            <!-- Decision Trace -->
            <DecisionTrace
              v-if="result.candidates?.length"
              :candidates="result.candidates"
            />

            <!-- Combo -->
            <ComboRec
              v-if="result.candidates?.length"
              :candidates="result.candidates"
            />

            <!-- Report -->
            <ReportPanel
              v-if="result.report"
              :report="result.report"
            />
          </template>
        </div>
      </div>
    </main>
  </div>
</template>
