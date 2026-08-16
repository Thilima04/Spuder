# 🛡️ J.A.R.V.I.S. - Assistente Virtual com Visão Computacional & Voz

Assistente virtual avançado inspirado no **JARVIS das Indústrias Stark (Homem de Ferro)**, equipado com visão computacional em tempo real (OpenCV), cérebro de inteligência artificial multimodal (Google Gemini), acionamento e síntese de voz neural (Edge-TTS + Web Speech API) e um **HUD holográfico futurista** estilo Reator Arc.

---

## ⚡ Recursos Principais

- **🧠 Cérebro Multimodal (Gemini AI)**: Capacidade de raciocinar, responder com personalidade britânica refinada e analisar simultaneamente o que vê através da câmera.
- **👁️ Visão Computacional Tática (OpenCV)**: Detecção de alvos biométricos em tempo real, mira holográfica sobre rostos e transmissão de feed para o HUD.
- **🎙️ Acionamento e Síntese de Voz**:
  - Escuta ativa por voz no navegador com detecção da palavra-chave *"Jarvis"*.
  - Voz neural fluida e natural (*pt-BR-AntonioNeural* ou personalizável).
  - Espectrograma de áudio animado em Canvas reativo às frequências sonoras.
- **📊 Telemetria de Sistemas Stark**: Monitoramento em tempo real de CPU, Memória RAM, Bateria e integridade dos sensores.
- **🛠️ Automação do Windows**: Abertura de aplicativos, diagnósticos de hardware e consultas de clima e buscas na web.

---

## 🚀 Como Executar

### 1. Instalar as dependências
Abra o terminal (PowerShell ou Prompt de Comando) na pasta do projeto e instale as bibliotecas necessárias:

```bash
pip install -r backend/requirements.txt
```

### 2. Configurar a Chave do Gemini (Opcional na inicialização)
Você pode obter sua chave de API gratuitamente em [Google AI Studio](https://aistudio.google.com/app/apikey).
- Você pode criar um arquivo `.env` baseado no `.env.example` com `GEMINI_API_KEY=sua_chave_aqui`
- **OU** simplesmente colar sua chave diretamente pela interface clicando no ícone de engrenagem ⚙️ no HUD!

### 3. Iniciar o JARVIS
Execute o comando:

```bash
python run.py
```

O servidor será inicializado e o navegador abrirá automaticamente o HUD tático em `http://127.0.0.1:8000`.

---

## 🗣️ Exemplos de Comandos para Testar

- *"Jarvis, qual o status geral dos nossos sistemas?"*
- *"Jarvis, o que você está vendo agora?"* (Ele utilizará a câmera para descrever objetos, pessoas ou o ambiente)
- *"Jarvis, como está o clima em São Paulo hoje?"*
- *"Jarvis, abra a calculadora"* ou *"Abra o navegador"*
- *"Jarvis, faça uma análise estratégica sobre computação quântica"*
