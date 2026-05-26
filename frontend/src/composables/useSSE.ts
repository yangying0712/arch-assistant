import { readonly, ref } from 'vue'

export interface SSEStep {
  name: string
  status: 'pending' | 'active' | 'done' | 'error'
  message: string
}

const initialSteps: SSEStep[] = [
  { name: 'connect', status: 'pending', message: '连接后端服务' },
  { name: 'features', status: 'pending', message: '提取需求特征' },
  { name: 'candidates', status: 'pending', message: '匹配候选架构' },
  { name: 'report', status: 'pending', message: '生成评估报告' },
  { name: 'done', status: 'pending', message: '完成分析' },
]

export function useSSE() {
  const steps = ref<SSEStep[]>(initialSteps.map(step => ({ ...step })))
  const isStreaming = ref(false)
  const error = ref<string | null>(null)

  function resetSteps() {
    steps.value = initialSteps.map(step => ({ ...step }))
  }

  function updateStep(name: string, status: SSEStep['status']) {
    const step = steps.value.find(item => item.name === name)
    if (step) step.status = status
  }

  async function streamAnalyze(prompt: string, sessionId: string): Promise<any> {
    isStreaming.value = true
    error.value = null
    resetSteps()
    updateStep('connect', 'active')

    const result: any = { features: null, candidates: null, report: null }

    try {
      const response = await fetch('/api/v1/analyze/stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt, session_id: sessionId }),
      })

      if (!response.ok || !response.body) throw new Error(`HTTP ${response.status}`)

      updateStep('connect', 'done')
      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const frames = buffer.split('\n\n')
        buffer = frames.pop() || ''

        for (const frame of frames) {
          const line = frame.split('\n').find(item => item.startsWith('data: '))
          if (!line) continue
          try {
            const data = JSON.parse(line.slice(6))
            switch (data.event) {
              case 'features':
                updateStep('features', 'done')
                result.features = data.data
                break
              case 'candidates':
                updateStep('candidates', 'done')
                result.candidates = data.data
                break
              case 'report':
                updateStep('report', 'done')
                result.report = data.data
                break
              case 'done':
                updateStep('done', 'done')
                break
              case 'error':
                error.value = data.message
                updateStep('report', 'error')
                break
            }
          } catch {
            // Ignore malformed partial frames.
          }
        }
      }
    } catch (event: any) {
      error.value = event.message
      if (!result.features && !result.candidates) throw event
    } finally {
      isStreaming.value = false
    }

    return result
  }

  return {
    steps: readonly(steps),
    isStreaming: readonly(isStreaming),
    error: readonly(error),
    streamAnalyze,
  }
}
