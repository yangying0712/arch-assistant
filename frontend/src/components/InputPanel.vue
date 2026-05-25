<script setup lang="ts">
import { ref, computed } from 'vue'
import { useSpeech } from '../composables/useSpeech'
import { useSSE, type SSEStep } from '../composables/useSSE'

const emit = defineEmits<{
  submit: [prompt: string, sessionId: string]
  callUtterance: [prompt: string, sessionId: string]
}>()

const { isListening, isCallActive, isSpeaking, statusText, startMic, stopMic, startCall, stopCall, speak, stopSpeaking } = useSpeech()
const { steps, isStreaming, error, streamAnalyze } = useSSE()

const prompt = ref('')
const sessionId = ref(crypto.randomUUID())

const canSend = computed(() => prompt.value.trim().length > 0 && !isStreaming.value)

// Text submit
async function handleSend() {
  if (!canSend.value) return
  const p = prompt.value.trim()
  prompt.value = ''
  const sid = crypto.randomUUID()
  sessionId.value = sid

  // Try SSE first
  try {
    emit('submit', p, sid)
  } catch {
    // handled by parent
  }
}

// Voice call callback
function handleVoiceUtterance(text: string) {
  const sid = crypto.randomUUID()
  sessionId.value = sid
  emit('callUtterance', text, sid)
}

function handleStartCall() {
  if (isCallActive.value) {
    stopCall()
  } else {
    startCall(handleVoiceUtterance)
  }
}

// Voice mic (single)
async function handleMic() {
  if (isListening.value) {
    stopMic()
    return
  }
  try {
    const text = await startMic()
    prompt.value = text
    handleSend()
  } catch {
    // user cancelled
  }
}

const stepIcons: Record<SSEStep['status'], string> = {
  pending: '○',
  active: '◉',
  done: '✓',
  error: '✕',
}
const stepIconColors: Record<SSEStep['status'], string> = {
  pending: 'text-slate-600',
  active: 'text-blue-400 animate-pulse',
  done: 'text-green-400',
  error: 'text-red-400',
}
</script>

<template>
  <div class="space-y-4">
    <!-- Input Area -->
    <div class="glass p-4">
      <textarea
        v-model="prompt"
        class="w-full h-28 p-4 bg-slate-900/50 border border-slate-600/30 rounded-xl text-slate-200 placeholder-slate-500 text-sm resize-none focus:outline-none focus:border-blue-500/50 focus:ring-1 focus:ring-blue-500/30 transition-all"
        placeholder="描述你的软件需求，例如：开发一个跨平台的即时通讯系统，要求支持万人同时在线..."
        :disabled="isStreaming"
        @keydown.enter.exact.prevent="handleSend"
      />

      <div class="flex items-center justify-between mt-3">
        <div class="flex items-center gap-2">
          <!-- Mic button -->
          <button
            @click="handleMic"
            :class="[
              'px-3 py-2 rounded-lg text-xs font-medium transition-all flex items-center gap-1.5',
              isListening
                ? 'bg-red-600 text-white animate-pulse'
                : 'bg-slate-700/50 text-slate-300 hover:bg-slate-600/50 border border-slate-600/30'
            ]"
            :disabled="isCallActive || isStreaming"
            :title="isListening ? '停止' : '语音输入'"
          >
            {{ isListening ? '⏹' : '🎤' }}
            <span class="hidden sm:inline">{{ isListening ? '聆听中' : '语音' }}</span>
          </button>

          <!-- Voice Call button -->
          <button
            @click="handleStartCall"
            :class="[
              'px-3 py-2 rounded-lg text-xs font-medium transition-all flex items-center gap-1.5 border',
              isCallActive
                ? 'bg-red-600/80 text-white border-red-500 animate-pulse'
                : 'bg-emerald-900/30 text-emerald-300 hover:bg-emerald-800/40 border-emerald-500/30'
            ]"
            :disabled="isStreaming"
            :title="isCallActive ? '结束通话' : '语音通话'"
          >
            {{ isCallActive ? '⏹' : '📞' }}
            <span class="hidden sm:inline">{{ isCallActive ? '通话中' : '通话' }}</span>
          </button>

          <!-- Stop Speaking -->
          <button
            v-if="isSpeaking"
            @click="stopSpeaking"
            class="px-3 py-2 rounded-lg text-xs font-medium bg-slate-700/50 text-slate-300 hover:bg-slate-600/50 border border-slate-600/30 transition-all flex items-center gap-1.5"
          >
            🔇 停止朗读
          </button>
        </div>

        <!-- Send button -->
        <button
          @click="handleSend"
          :disabled="!canSend"
          class="px-5 py-2 rounded-lg text-sm font-bold transition-all flex items-center gap-2
                 bg-gradient-to-r from-blue-600 to-blue-500 text-white
                 hover:from-blue-500 hover:to-blue-400
                 disabled:from-slate-600 disabled:to-slate-600 disabled:text-slate-400 disabled:cursor-not-allowed
                 shadow-lg shadow-blue-500/20"
        >
          <span v-if="isStreaming" class="animate-spin">⟳</span>
          <span v-else>→</span>
          {{ isStreaming ? '分析中' : '发送' }}
        </button>
      </div>
    </div>

    <!-- SSE Progress -->
    <div v-if="isStreaming" class="glass p-4 animate-in">
      <div class="space-y-2">
        <div v-for="step in steps" :key="step.name" class="flex items-center gap-3">
          <span :class="['text-xs font-bold w-5 text-center', stepIconColors[step.status]]">
            {{ stepIcons[step.status] }}
          </span>
          <span :class="[
            'text-xs transition-colors',
            step.status === 'active' ? 'text-blue-300' :
            step.status === 'done' ? 'text-green-300' :
            step.status === 'error' ? 'text-red-300' :
            'text-slate-500'
          ]">{{ step.message }}</span>
        </div>
      </div>
    </div>

    <!-- Error -->
    <div v-if="error && !isStreaming" class="glass p-3 border-red-500/30 text-red-300 text-xs">
      ⚠️ {{ error }}
    </div>

    <!-- Status bar -->
    <div v-if="statusText" class="text-center text-xs text-slate-500 py-1">
      {{ statusText }}
    </div>
  </div>
</template>
