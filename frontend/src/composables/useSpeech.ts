import { onUnmounted, readonly, ref } from 'vue'

export function useSpeech() {
  const isListening = ref(false)
  const isCallActive = ref(false)
  const isSpeaking = ref(false)
  const statusText = ref('')
  const interimText = ref('')

  let recognition: any = null
  let synthesis: SpeechSynthesis | null = null
  let callTurns: string[] = []
  let onCallUtterance: ((text: string) => void) | null = null

  if (typeof window !== 'undefined') {
    synthesis = window.speechSynthesis
  }

  function speechRecognitionSupported() {
    return typeof window !== 'undefined' && ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window)
  }

  function createRecognition() {
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition
    const instance = new SpeechRecognition()
    instance.lang = 'zh-CN'
    instance.interimResults = true
    instance.continuous = false
    return instance
  }

  function startMic(): Promise<string> {
    return new Promise((resolve, reject) => {
      if (!speechRecognitionSupported()) {
        reject(new Error('当前浏览器不支持语音识别，请使用 Chrome 或 Edge。'))
        return
      }

      interimText.value = ''
      recognition = createRecognition()
      isListening.value = true
      statusText.value = '正在聆听，请说出需求...'

      recognition.onresult = (event: any) => {
        let text = ''
        for (let index = 0; index < event.results.length; index++) {
          text += event.results[index][0].transcript
        }
        interimText.value = text
      }

      recognition.onerror = (event: any) => {
        statusText.value = '语音识别失败：' + event.error
        stopMic()
        reject(event)
      }

      recognition.onend = () => {
        stopMic()
        const finalText = interimText.value.trim()
        if (finalText) resolve(finalText)
      }

      recognition.start()
    })
  }

  function stopMic() {
    isListening.value = false
    if (!isCallActive.value) statusText.value = ''
    if (recognition) {
      try {
        recognition.stop()
      } catch {
        // Recognition may already be stopped.
      }
      recognition = null
    }
  }

  function startCall(callback: (text: string) => void) {
    if (!speechRecognitionSupported()) {
      statusText.value = '语音通话需要 Chrome 或 Edge 桌面浏览器。'
      return
    }

    isCallActive.value = true
    callTurns = []
    onCallUtterance = callback
    synthesis?.cancel()
    statusText.value = '语音通话已开始，说完稍停即可自动分析。'
    startCallRecognition()
  }

  function stopCall() {
    isCallActive.value = false
    callTurns = []
    onCallUtterance = null
    synthesis?.cancel()
    stopMic()
    statusText.value = '语音通话已结束。'
  }

  function startCallRecognition() {
    if (!isCallActive.value || isListening.value) return

    interimText.value = ''
    recognition = createRecognition()

    recognition.onstart = () => {
      isListening.value = true
      statusText.value = '请说话，说完后停顿一下。'
    }

    recognition.onresult = (event: any) => {
      let text = ''
      for (let index = 0; index < event.results.length; index++) {
        text += event.results[index][0].transcript
      }
      interimText.value = text
    }

    recognition.onerror = (event: any) => {
      if (!isCallActive.value) return
      if (event.error === 'no-speech' || event.error === 'audio-capture') {
        statusText.value = '没有听到声音，正在重新聆听...'
        isListening.value = false
        recognition = null
        setTimeout(() => startCallRecognition(), 700)
        return
      }
      statusText.value = '语音识别失败：' + event.error
      isListening.value = false
      recognition = null
      setTimeout(() => startCallRecognition(), 900)
    }

    recognition.onend = () => {
      isListening.value = false
      recognition = null
      const raw = interimText.value.trim()
      interimText.value = ''

      if (!isCallActive.value) return
      if (!raw) {
        startCallRecognition()
        return
      }

      const hangup = /结束通话|挂断电话|停止通话|结束对话|不要说了/i
      if (hangup.test(raw)) {
        stopCall()
        return
      }

      callTurns.push(raw)
      const prompt = callTurns.length === 1
        ? callTurns[0]
        : `【初始需求】\n${callTurns[0]}\n\n${callTurns.slice(1).map((turn, index) => `【补充说明${index + 1}】\n${turn}`).join('\n\n')}`

      onCallUtterance?.(prompt)
    }

    recognition.start()
  }

  function speak(text: string, onEnd?: () => void) {
    if (!synthesis) return

    synthesis.cancel()
    const cleaned = text
      .replace(/\*\*([^*]+)\*\*/g, '$1')
      .replace(/#{1,6}\s*/g, '')
      .replace(/`+/g, '')
      .replace(/\|/g, ' ')
      .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1')
      .replace(/\s+/g, ' ')
      .trim()

    const utterance = new SpeechSynthesisUtterance(cleaned)
    utterance.lang = 'zh-CN'
    utterance.rate = 1.03
    isSpeaking.value = true
    utterance.onend = () => {
      isSpeaking.value = false
      onEnd?.()
    }
    utterance.onerror = () => {
      isSpeaking.value = false
      onEnd?.()
    }
    synthesis.speak(utterance)
  }

  function stopSpeaking() {
    synthesis?.cancel()
    isSpeaking.value = false
  }

  onUnmounted(() => {
    stopCall()
    stopSpeaking()
  })

  return {
    isListening: readonly(isListening),
    isCallActive: readonly(isCallActive),
    isSpeaking: readonly(isSpeaking),
    statusText: readonly(statusText),
    interimText: readonly(interimText),
    startMic,
    stopMic,
    startCall,
    stopCall,
    speak,
    stopSpeaking,
  }
}
