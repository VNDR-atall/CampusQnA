<template>
  <div class="app-container">
    <div class="chat-wrapper">
      <div class="header">
        <div class="logo">
          <span class="logo-icon">🎓</span>
          <h1>校园百事通</h1>
        </div>
        <p class="subtitle">基于 RAG 的智能问答系统</p>
      </div>

      <div class="chat-container" ref="chatContainer">
        <div v-if="messages.length === 0" class="welcome">
          <div class="welcome-icon">🤖</div>
          <h2>你好！</h2>
          <p>我是校园百事通，有什么可以帮助你的？</p>
          <div class="quick-questions">
            <button v-for="q in quickQuestions" :key="q" @click="sendQuestion(q)" class="quick-btn">
              {{ q }}
            </button>
          </div>
        </div>
        <div v-else class="messages">
          <div v-for="(msg, index) in messages" :key="index" :class="['message', msg.role]">
            <div class="message-avatar">
              {{ msg.role === 'user' ? '👤' : '🤖' }}
            </div>
            <div class="message-content">
              <div class="message-text" v-html="formatMessage(msg.content)"></div>
              <div v-if="msg.sources && msg.sources.length > 0" class="sources">
                <div class="sources-label">来源：</div>
                <div class="sources-list">
                  <div v-for="(source, si) in msg.sources" :key="si" class="source-item">
                    <span class="source-department">{{ source.department || '未知部门' }}</span>
                    <span class="source-title">{{ source.title }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div v-if="isLoading" class="loading">
          <div class="loading-icon"></div>
          <span>正在思考中...</span>
        </div>
      </div>

      <div class="input-area">
        <div class="input-wrapper">
          <input
            v-model="inputText"
            @keypress.enter="sendMessage"
            placeholder="请输入你的问题..."
            :disabled="isLoading"
          />
          <button @click="sendMessage" :disabled="isLoading || !inputText.trim()">
            发送
          </button>
        </div>
        <div v-if="lastResponseTime" class="response-time">
          响应时间：{{ lastResponseTime }}ms
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, nextTick, onMounted } from 'vue'
import axios from 'axios'

export default {
  name: 'App',
  setup() {
    const chatContainer = ref(null)
    const messages = ref([])
    const inputText = ref('')
    const isLoading = ref(false)
    const lastResponseTime = ref(null)
    
    const quickQuestions = [
      '计算机学院有哪些专业？',
      '数学与信息科学学院培养方案',
      '土木与交通工程学院简介'
    ]

    const formatMessage = (content) => {
      return content
        .replace(/\n/g, '<br>')
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    }

    const scrollToBottom = () => {
      nextTick(() => {
        if (chatContainer.value) {
          chatContainer.value.scrollTop = chatContainer.value.scrollHeight
        }
      })
    }

    const sendQuestion = (question) => {
      inputText.value = question
      sendMessage()
    }

    const sendMessage = async () => {
      if (!inputText.value.trim() || isLoading.value) return

      const userQuestion = inputText.value
      inputText.value = ''

      messages.value.push({
        role: 'user',
        content: userQuestion
      })
      scrollToBottom()

      isLoading.value = true
      const startTime = Date.now()

      const assistantMsgIndex = messages.value.push({
        role: 'assistant',
        content: '',
        sources: []
      }) - 1

      try {
        const response = await axios.post('/api/query', {
          question: userQuestion
        })

        messages.value[assistantMsgIndex] = {
          role: 'assistant',
          content: response.data.answer,
          sources: response.data.sources
        }
      } catch (error) {
        console.error('请求失败:', error)
        messages.value[assistantMsgIndex] = {
          role: 'assistant',
          content: error.response?.data?.detail || '抱歉，发生了错误，请稍后再试。',
          sources: []
        }
      } finally {
        isLoading.value = false
        lastResponseTime.value = Date.now() - startTime
        scrollToBottom()
      }
    }

    return {
      chatContainer,
      messages,
      inputText,
      isLoading,
      lastResponseTime,
      quickQuestions,
      formatMessage,
      sendQuestion,
      sendMessage
    }
  }
}
</script>

<style scoped>
.app-container {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px;
  min-height: 100vh;
}

.chat-wrapper {
  width: 100%;
  max-width: 800px;
  background: white;
  border-radius: 20px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  display: flex;
  flex-direction: column;
  height: 90vh;
  max-height: 700px;
  overflow: hidden;
}

.header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 25px 30px;
  text-align: center;
}

.logo {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  margin-bottom: 5px;
}

.logo-icon {
  font-size: 32px;
}

.header h1 {
  color: white;
  font-size: 28px;
}

.subtitle {
  color: rgba(255, 255, 255, 0.9);
  font-size: 14px;
}

.chat-container {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  background: #f5f7fa;
}

.welcome {
  text-align: center;
  padding: 40px 20px;
}

.welcome-icon {
  font-size: 64px;
  margin-bottom: 20px;
}

.welcome h2 {
  color: #333;
  font-size: 24px;
  margin-bottom: 10px;
}

.welcome p {
  color: #666;
  margin-bottom: 30px;
}

.quick-questions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  justify-content: center;
}

.quick-btn {
  background: white;
  border: 1px solid #e0e0e0;
  padding: 10px 20px;
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.3s;
  font-size: 14px;
}

.quick-btn:hover {
  background: #667eea;
  color: white;
  border-color: #667eea;
}

.messages {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.message {
  display: flex;
  gap: 15px;
}

.message.user {
  flex-direction: row-reverse;
}

.message-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: #e0e0e0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  flex-shrink: 0;
}

.message-content {
  flex: 1;
  max-width: 80%;
}

.message.user .message-content {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

.message-text {
  background: white;
  padding: 15px 20px;
  border-radius: 15px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  line-height: 1.6;
  color: #333;
}

.message.user .message-text {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.sources {
  margin-top: 10px;
  background: #f0f4f8;
  padding: 10px 15px;
  border-radius: 10px;
  font-size: 12px;
}

.sources-label {
  color: #666;
  margin-bottom: 5px;
  font-weight: 500;
}

.sources-list {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.source-item {
  display: flex;
  gap: 8px;
}

.source-department {
  background: #667eea;
  color: white;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 11px;
}

.source-title {
  color: #333;
}

.loading {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 15px;
  color: #666;
}

.loading-icon {
  width: 24px;
  height: 24px;
  border: 3px solid #e0e0e0;
  border-top-color: #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.input-area {
  padding: 20px;
  border-top: 1px solid #e0e0e0;
  background: white;
}

.input-wrapper {
  display: flex;
  gap: 10px;
}

.input-wrapper input {
  flex: 1;
  padding: 12px 20px;
  border: 2px solid #e0e0e0;
  border-radius: 25px;
  font-size: 16px;
  outline: none;
  transition: border-color 0.3s;
}

.input-wrapper input:focus {
  border-color: #667eea;
}

.input-wrapper input:disabled {
  background: #f5f5f5;
  cursor: not-allowed;
}

.input-wrapper button {
  padding: 12px 30px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 25px;
  font-size: 16px;
  cursor: pointer;
  transition: transform 0.2s;
}

.input-wrapper button:hover:not(:disabled) {
  transform: scale(1.05);
}

.input-wrapper button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.response-time {
  text-align: center;
  font-size: 12px;
  color: #999;
  margin-top: 10px;
}
</style>
