import { ref, readonly } from 'vue'

export interface SSEStep {
  name: string
  status: 'pending' | 'active' | 'done' | 'error'
  message: string
}

export function useSSE() {
  const steps = ref<SSEStep[]>([
    { name: 'connect', status: 'pending', message: '连接后端服务' },
    { name: 'features', status: 'pending', message: '需求特征提取' },
    { name: 'candidates', status: 'pending', message: '架构风格匹配' },
    { name: 'report', status: 'pending', message: '评估报告生成' },
    { name: 'done', status: 'pending', message: '完成' },
  ])
  const isStreaming = ref(false)
  const error = ref<string | null>(null)

  function updateStep(name: string, status: SSEStep['status']) {
    const step = steps.value.find(s => s.name === name)
    if (step) step.status = status
  }

  async function streamAnalyze(prompt: string, sessionId: string): Promise<any> {
    isStreaming.value = true
    error.value = null
    steps.value.forEach(s => s.status = 'pending')
    updateStep('connect', 'active')

    const result: any = { features: null, candidates: null, report: null }

    try {
      const res = await fetch('/api/v1/analyze/stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt, session_id: sessionId }),
      })

      if (!res.ok) throw new Error(`HTTP ${res.status}`)

      updateStep('connect', 'done')
      const reader = res.body!.getReader()
      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        buffer += decoder.decode(value, { stream: true })

        const lines = buffer.split('\n')
        buffer = lines.pop() || ''

        for (const line of lines) {
          if (!line.startsWith('data: ')) continue
          try {
            const data = JSON.parse(line.slice(6))
            switch (data.event) {
              case 'status':
                break
              case 'features':
                updateStep('features', 'active')
                result.features = data.data
                updateStep('features', 'done')
                break
              case 'candidates':
                updateStep('candidates', 'active')
                result.candidates = data.data
                updateStep('candidates', 'done')
                break
              case 'report':
                updateStep('report', 'active')
                result.report = data.data
                updateStep('report', 'done')
                break
              case 'done':
                updateStep('done', 'done')
                break
              case 'error':
                error.value = data.message
                updateStep('report', 'error')
                break
            }
          } catch { /* skip parse errors */ }
        }
      }
    } catch (e: any) {
      error.value = e.message
      // fall through - return partial result
      if (!result.features && !result.candidates) throw e
    } finally {
      isStreaming.value = false
    }

    return result
  }

  return { steps: readonly(steps), isStreaming: readonly(isStreaming), error: readonly(error), streamAnalyze }
}
