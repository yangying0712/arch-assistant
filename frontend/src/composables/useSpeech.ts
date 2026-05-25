import { ref, readonly, onUnmounted } from 'vue'

export function useSpeech() {
  const isListening = ref(false)
  const isCallActive = ref(false)
  const isSpeaking = ref(false)
  const statusText = ref('')
  const interimText = ref('')

  let recognition: any = null
  let synthesis: SpeechSynthesis | null = null
  let callTurns: string[] = []
  let callSessionId: string | null = null
  let onCallUtterance: ((text: string) => void) | null = null

  if (typeof window !== 'undefined') {
    synthesis = window.speechSynthesis
  }

  // ── Single Mic ──────────────────────
  function startMic(): Promise<string> {
    return new Promise((resolve, reject) => {
      if (!('webkitSpeechRecognition' in window || 'SpeechRecognition' in window)) {
        reject(new Error('浏览器不支持语音识别'))
        return
      }
      const SR = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition
      recognition = new SR()
      recognition.lang = 'zh-CN'
      recognition.interimResults = true
      recognition.continuous = false
      isListening.value = true
      statusText.value = '🎙️ 正在聆听...'

      recognition.onresult = (e: any) => {
        let text = ''
        for (let i = 0; i < e.results.length; i++) text += e.results[i][0].transcript
        interimText.value = text
      }
      recognition.onerror = (e: any) => {
        statusText.value = '语音识别错误: ' + e.error
        stopMic()
        reject(e)
      }
      recognition.onend = () => {
        stopMic()
        const final = interimText.value.trim()
        if (final) resolve(final)
      }
      recognition.start()
    })
  }

  function stopMic() {
    isListening.value = false
    if (!isCallActive.value) statusText.value = ''
    if (recognition) { try { recognition.stop() } catch (_) {}; recognition = null }
  }

  // ── Voice Call ──────────────────────
  function startCall(callback: (text: string) => void) {
    if (!('webkitSpeechRecognition' in window || 'SpeechRecognition' in window)) {
      statusText.value = '⚠️ 语音识别需 Chrome/Edge 桌面版'
      return
    }
    isCallActive.value = true
    callTurns = []
    callSessionId = crypto.randomUUID()
    onCallUtterance = callback
    synthesis?.cancel()
    statusText.value = '📞 语音通话已开始'
    startCallRecognition()
  }

  function stopCall() {
    isCallActive.value = false
    callTurns = []
    callSessionId = null
    onCallUtterance = null
    synthesis?.cancel()
    stopMic()
    statusText.value = '已结束语音通话'
  }

  function startCallRecognition() {
    if (!isCallActive.value || isListening.value) return
    const SR = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition
    recognition = new SR()
    recognition.lang = 'zh-CN'
    recognition.interimResults = true
    recognition.continuous = false
    recognition.onstart = () => {
      isListening.value = true
      statusText.value = '📞 请说话…（说完稍停）'
    }
    recognition.onresult = (e: any) => {
      let text = ''
      for (let i = 0; i < e.results.length; i++) text += e.results[i][0].transcript
      interimText.value = text
    }
    recognition.onerror = (e: any) => {
      if (!isCallActive.value) return
      if (e.error === 'no-speech' || e.error === 'audio-capture') {
        statusText.value = '未听到声音，再试…'
        setTimeout(() => { if (isCallActive.value && !isListening.value) startCallRecognition() }, 600)
        return
      }
      statusText.value = '语音识别: ' + e.error
      isListening.value = false; recognition = null
      if (isCallActive.value) setTimeout(() => startCallRecognition(), 800)
    }
    recognition.onend = () => {
      isListening.value = false; recognition = null
      const raw = interimText.value.trim()
      interimText.value = ''
      if (!isCallActive.value) return
      if (!raw) { startCallRecognition(); return }
      const hangup = /结束通话|挂断电话|挂了|停止通话|结束对话|不要说了/i
      if (hangup.test(raw)) {
        stopCall()
        return
      }
      callTurns.push(raw)
      const prompt = callTurns.length === 1
        ? callTurns[0]
        : '【初始需求】\n' + callTurns[0] + '\n\n' +
          callTurns.slice(1).map((t, i) => '【补充说明' + (i + 1) + '】\n' + t).join('\n\n')
      if (onCallUtterance) onCallUtterance(prompt)
    }
    recognition.start()
  }

  // ── TTS ─────────────────────────────
  function speak(text: string, onEnd?: () => void) {
    if (!synthesis) return
    synthesis.cancel()
    const cleaned = text
      .replace(/\*\*([^*]+)\*\*/g, '$1')
      .replace(/#{1,6}\s*/g, '')
      .replace(/`+/g, '')
      .replace(/\|/g, ' ')
      .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1')
      .replace(/\s+/g, ' ').trim()
    const utter = new SpeechSynthesisUtterance(cleaned)
    utter.lang = 'zh-CN'
    utter.rate = 1.03
    isSpeaking.value = true
    utter.onend = () => { isSpeaking.value = false; if (onEnd) onEnd() }
    utter.onerror = () => { isSpeaking.value = false; if (onEnd) onEnd() }
    synthesis.speak(utter)
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
    startMic, stopMic,
    startCall, stopCall,
    speak, stopSpeaking,
  }
}
