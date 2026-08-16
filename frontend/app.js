// SPUDER 2.0 // Cybernetic Spider HUD Controller
let ws = null;
let audioContext = null;
let analyserNode = null;
let currentAudioSource = null;
let isListening = false;
let isSpeaking = false;
let isManualListening = false;
let recognition = null;
let continuousVoiceMode = true;
let lastGesture = "NONE";
let ownerWelcomed = false;

// Câmera do Celular / Dispositivo Móvel
let mobileStream = null;
let isUsingMobileCam = false;
let mobileFacingMode = "environment"; // 'environment' = câmera traseira, 'user' = frontal

// Elementos do DOM
const clockDisplay = document.getElementById("hud-clock");
const dateDisplay = document.getElementById("hud-date");
const statusLabel = document.getElementById("status-label");
const statusDot = document.querySelector(".status-dot");
const terminalLogs = document.getElementById("hud-terminal-logs");
const cameraImg = document.getElementById("camera-stream-img");
const mobileCameraVideo = document.getElementById("mobile-camera-video");
const cameraPlaceholder = document.getElementById("camera-placeholder");
const hudLensLabel = document.getElementById("hud-lens-label");
const btnToggleMobileCam = document.getElementById("btn-toggle-mobile-cam");
const btnMobileCamText = document.getElementById("btn-mobile-cam-text");

// Telemetria & Biometria
const valOwnerStatus = document.getElementById("val-owner-status");
const valOwnerDetail = document.getElementById("val-owner-detail");
const valGesture = document.getElementById("val-gesture");
const valCpu = document.getElementById("val-cpu");
const barCpu = document.getElementById("bar-cpu");
const valCpuCores = document.getElementById("val-cpu-cores");
const valRam = document.getElementById("val-ram");
const barRam = document.getElementById("bar-ram");
const valRamUsage = document.getElementById("val-ram-usage");
const valBattery = document.getElementById("val-battery");
const barBattery = document.getElementById("bar-battery");
const valBatteryStatus = document.getElementById("val-battery-status");

// Diálogos & Formulário
const userQueryText = document.getElementById("user-query-text");
const jarvisResponseText = document.getElementById("jarvis-response-text");
const chatForm = document.getElementById("chat-form");
const textInput = document.getElementById("text-input");
const btnVoiceToggle = document.getElementById("btn-voice-toggle");
const micStatusText = document.getElementById("mic-status-text");
const btnScanVision = document.getElementById("btn-scan-vision");
const btnScanScreen = document.getElementById("btn-scan-screen");

// Modais
const btnOpenMemory = document.getElementById("btn-open-memory");
const btnCloseMemory = document.getElementById("btn-close-memory");
const modalMemory = document.getElementById("modal-memory");
const memoryModalContent = document.getElementById("memory-modal-content");

const btnOpenSettings = document.getElementById("btn-open-settings");
const btnCloseSettings = document.getElementById("btn-close-settings");
const modalSettings = document.getElementById("modal-settings");
const inputApiKey = document.getElementById("input-api-key");
const btnSaveSettings = document.getElementById("btn-save-settings");

// Canvas Visualizador
const canvas = document.getElementById("audio-visualizer-canvas");
const canvasCtx = canvas.getContext("2d");

// --- INICIALIZAÇÃO ---
window.addEventListener("DOMContentLoaded", () => {
    initClock();
    initCanvas();
    initWebSocket();
    initSpeechRecognition();
    setupEventListeners();
    addTerminalLog("Núcleo Aranha Cibernética SPUDER 2.0 online.");
});

// --- RELÓGIO & DATA ---
function initClock() {
    function update() {
        const now = new Date();
        clockDisplay.innerText = now.toTimeString().split(" ")[0];
        dateDisplay.innerText = now.toLocaleDateString("pt-BR", { 
            weekday: "short", day: "2-digit", month: "short", year: "numeric" 
        }).toUpperCase();
    }
    update();
    setInterval(update, 1000);
}

// --- LOGS NO TERMINAL ---
function addTerminalLog(msg) {
    const time = new Date().toTimeString().split(" ")[0];
    const logLine = document.createElement("div");
    logLine.className = "log-line";
    logLine.innerText = `[${time}] ${msg}`;
    terminalLogs.appendChild(logLine);
    terminalLogs.scrollTop = terminalLogs.scrollHeight;
}

// --- STATUS DO SISTEMA ---
function setSystemStatus(status, text) {
    statusLabel.innerText = text || status;
    
    if (status === "SPEAKING") {
        document.body.classList.add("jarvis-speaking");
        statusDot.style.backgroundColor = "#ffb800";
        statusDot.style.boxShadow = "0 0 12px #ffb800";
    } else if (status === "LISTENING") {
        document.body.classList.remove("jarvis-speaking");
        statusDot.style.backgroundColor = "#ff3344";
        statusDot.style.boxShadow = "0 0 12px #ff3344";
    } else if (status === "THINKING" || status === "ANALYZING_VISION" || status === "ANALYZING_SCREEN") {
        document.body.classList.remove("jarvis-speaking");
        statusDot.style.backgroundColor = "#00f3ff";
        statusDot.style.boxShadow = "0 0 18px #00f3ff";
    } else {
        document.body.classList.remove("jarvis-speaking");
        statusDot.style.backgroundColor = "#00ffaa";
        statusDot.style.boxShadow = "0 0 8px #00ffaa";
    }
}

// --- WEBSOCKET REAL-TIME ---
function initWebSocket() {
    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const host = window.location.host || "127.0.0.1:8000";
    const wsUrl = `${protocol}//${host}/ws`;

    ws = new WebSocket(wsUrl);

    ws.onopen = () => {
        addTerminalLog("Mainframe neural conectado com sucesso.");
        setSystemStatus("ONLINE", "SPIDER CORE // OPERACIONAL");
    };

    ws.onmessage = (event) => {
        try {
            const data = JSON.parse(event.data);
            
            // Frame de vídeo da visão computacional
            if (data.type === "video_frame") {
                if (data.frame) {
                    cameraImg.src = `data:image/jpeg;base64,${data.frame}`;
                    cameraImg.style.display = "block";
                    cameraPlaceholder.style.display = "none";
                }
                if (data.gesture) {
                    valGesture.innerText = data.gesture;
                    handleGestureEvent(data.gesture);
                }
                if (data.owner_detected) {
                    valOwnerStatus.innerText = "SENHOR THIAGO";
                    valOwnerDetail.innerText = "RECONHECIMENTO ATIVO // AUTORIZADO";
                }
            }
            
            // Telemetria de hardware
            else if (data.type === "telemetry" && data.data) {
                updateTelemetryUI(data.data);
            }
            
            // Notificação de logs
            else if (data.type === "log") {
                addTerminalLog(data.message);
            }
            
            // Status de processamento
            else if (data.type === "status") {
                setSystemStatus(data.status);
            }
        } catch (e) {
            console.error("Erro ao processar dados WS:", e);
        }
    };

    ws.onclose = () => {
        addTerminalLog("Conexão perdida. Tentando reconexão em 3s...");
        setSystemStatus("OFFLINE", "STANDBY // RECONECTANDO");
        setTimeout(initWebSocket, 3000);
    };
}

function handleGestureEvent(gesture) {
    if (gesture === lastGesture || gesture === "NENHUM" || gesture === "NONE") return;
    lastGesture = gesture;

    // Gesto de Palma Aberta = Silencia fala atual
    if (gesture === "PALMA ABERTA" && isSpeaking && currentAudioSource) {
        try {
            currentAudioSource.stop();
            isSpeaking = false;
            setSystemStatus("ONLINE", "FALA INTERROMPIDA POR GESTO");
            addTerminalLog("[GESTO] Fala interrompida por comando de palma aberta.");
        } catch (e) {}
    }
}

function updateTelemetryUI(tel) {
    if (tel.cpu_usage) {
        valCpu.innerText = tel.cpu_usage;
        barCpu.style.width = tel.cpu_usage;
    }
    if (tel.cpu_cores && tel.cpu_freq_mhz) {
        valCpuCores.innerText = `CORES: ${tel.cpu_cores} // FREQ: ${tel.cpu_freq_mhz}`;
    }
    if (tel.ram_usage) {
        valRam.innerText = tel.ram_usage;
        barRam.style.width = tel.ram_usage;
        valRamUsage.innerText = `${tel.ram_used_gb} / ${tel.ram_total_gb}`;
    }
    if (tel.battery) {
        valBattery.innerText = `${tel.battery.percent}%`;
        barBattery.style.width = `${tel.battery.percent}%`;
        valBatteryStatus.innerText = tel.battery.power_plugged ? "ALIMENTAÇÃO EXTERNA (PLUGADO)" : "OPERANDO EM BATERIA";
    }
}

// --- VISUALIZADOR DE ÁUDIO (CANVAS SPECTRUM) ---
function initCanvas() {
    canvas.width = canvas.parentElement.clientWidth;
    canvas.height = canvas.parentElement.clientHeight;
    
    window.addEventListener("resize", () => {
        canvas.width = canvas.parentElement.clientWidth;
        canvas.height = canvas.parentElement.clientHeight;
    });

    drawIdleVisualizer();
}

function drawIdleVisualizer() {
    if (isSpeaking) return;
    
    canvasCtx.clearRect(0, 0, canvas.width, canvas.height);
    const centerY = canvas.height / 2;
    const time = Date.now() * 0.003;
    
    canvasCtx.beginPath();
    canvasCtx.strokeStyle = "rgba(0, 243, 255, 0.35)";
    canvasCtx.lineWidth = 1.5;
    
    for (let x = 0; x < canvas.width; x += 4) {
        const y = centerY + Math.sin(time + x * 0.03) * 4;
        if (x === 0) canvasCtx.moveTo(x, y);
        else canvasCtx.lineTo(x, y);
    }
    canvasCtx.stroke();

    requestAnimationFrame(drawIdleVisualizer);
}

function renderAudioSpectrum() {
    if (!analyserNode || !isSpeaking) {
        drawIdleVisualizer();
        return;
    }

    const bufferLength = analyserNode.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);
    analyserNode.getByteFrequencyData(dataArray);

    canvasCtx.clearRect(0, 0, canvas.width, canvas.height);

    const barWidth = (canvas.width / bufferLength) * 2.2;
    let x = 0;

    for (let i = 0; i < bufferLength; i++) {
        const barHeight = (dataArray[i] / 255) * (canvas.height * 0.85);
        
        const gradient = canvasCtx.createLinearGradient(0, canvas.height, 0, 0);
        gradient.addColorStop(0, "rgba(0, 136, 255, 0.4)");
        gradient.addColorStop(0.7, "rgba(0, 243, 255, 0.85)");
        gradient.addColorStop(1, "#ffffff");

        canvasCtx.fillStyle = gradient;
        canvasCtx.fillRect(x, canvas.height - barHeight, barWidth - 1, barHeight);

        x += barWidth;
    }

    requestAnimationFrame(renderAudioSpectrum);
}

// --- REPRODUÇÃO DE ÁUDIO DO SPUDER ---
async function playJarvisAudio(base64Audio) {
    if (!base64Audio) return;

    try {
        if (!audioContext) {
            audioContext = new (window.AudioContext || window.webkitAudioContext)();
        }
        if (audioContext.state === 'suspended') {
            await audioContext.resume();
        }

        const audioData = Uint8Array.from(atob(base64Audio), c => c.charCodeAt(0)).buffer;
        const decodedBuffer = await audioContext.decodeAudioData(audioData);

        currentAudioSource = audioContext.createBufferSource();
        currentAudioSource.buffer = decodedBuffer;

        analyserNode = audioContext.createAnalyser();
        analyserNode.fftSize = 64;

        currentAudioSource.connect(analyserNode);
        analyserNode.connect(audioContext.destination);

        isSpeaking = true;
        setSystemStatus("SPEAKING", "TRANSMITINDO RESPOSTA VOCAL");
        renderAudioSpectrum();

        currentAudioSource.onended = () => {
            isSpeaking = false;
            currentAudioSource = null;
            setSystemStatus("ONLINE", "SISTEMAS PRONTOS // EM ESPERA");
        };

        currentAudioSource.start(0);
    } catch (e) {
        console.error("Erro ao reproduzir áudio:", e);
        isSpeaking = false;
        setSystemStatus("ONLINE", "SISTEMAS PRONTOS");
    }
}

// --- RECONHECIMENTO DE VOZ ---
async function requestMicPermission() {
    try {
        if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            stream.getTracks().forEach(t => t.stop());
            return true;
        }
    } catch (err) {
        addTerminalLog("[MICROFONE] Permissão de áudio não concedida no navegador.");
        return false;
    }
    return true;
}

function initSpeechRecognition() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
        addTerminalLog("[AVISO] Reconhecimento de fala nativo não suportado. Use Chrome ou Edge.");
        return;
    }

    try {
        recognition = new SpeechRecognition();
        recognition.lang = "pt-BR";
        recognition.continuous = true;
        recognition.interimResults = true;
        recognition.maxAlternatives = 1;

        recognition.onstart = () => {
            isListening = true;
            btnVoiceToggle.classList.add("active");
            micStatusText.innerText = "ESCUTANDO SUA VOZ...";
            setSystemStatus("LISTENING", "ESCUTANDO COMANDO DO SENHOR THIAGO...");
            addTerminalLog("Sensor auditivo ativado.");
        };

        recognition.onresult = (event) => {
            let interimTranscript = "";
            let finalTranscript = "";

            for (let i = event.resultIndex; i < event.results.length; ++i) {
                if (event.results[i].isFinal) {
                    finalTranscript += event.results[i][0].transcript;
                } else {
                    interimTranscript += event.results[i][0].transcript;
                }
            }

            if (interimTranscript.trim()) {
                userQueryText.innerText = `[Falando]: ${interimTranscript}`;
            }

            if (finalTranscript.trim()) {
                const text = finalTranscript.trim();
                userQueryText.innerText = text;
                
                const lower = text.toLowerCase();
                const triggers = ["spuder", "spider", "espuder", "jarvis"];
                const hasTrigger = triggers.some(t => lower.includes(t));

                let command = text;
                for (const t of triggers) {
                    const reg = new RegExp(t, "gi");
                    command = command.replace(reg, "");
                }
                command = command.trim();
                const queryToSend = command.length > 0 ? command : text;

                if (isManualListening || hasTrigger || !continuousVoiceMode) {
                    addTerminalLog(`Comando de voz: "${text}"`);
                    sendCommandToJarvis(queryToSend);
                    
                    if (isManualListening && !continuousVoiceMode) {
                        toggleVoiceRecognition();
                    }
                }
            }
        };

        recognition.onerror = (event) => {
            if (event.error === "not-allowed" || event.error === "service-not-allowed") {
                addTerminalLog("[ERRO] Microfone bloqueado pelo navegador!");
                isListening = false;
                btnVoiceToggle.classList.remove("active");
                micStatusText.innerText = "FALAR COM SPUDER";
            }
        };

        recognition.onend = () => {
            if (isListening) {
                setTimeout(() => {
                    if (isListening) {
                        try { recognition.start(); } catch (err) {}
                    }
                }, 300);
            } else {
                btnVoiceToggle.classList.remove("active");
                micStatusText.innerText = "FALAR COM SPUDER";
            }
        };
    } catch (e) {
        console.error("Falha ao iniciar SpeechRecognition:", e);
    }
}

async function toggleVoiceRecognition() {
    if (!recognition) {
        initSpeechRecognition();
    }

    if (isListening) {
        isListening = false;
        isManualListening = false;
        try {
            recognition.stop();
        } catch (e) {}
        btnVoiceToggle.classList.remove("active");
        micStatusText.innerText = "FALAR COM SPUDER";
        setSystemStatus("ONLINE", "SISTEMAS PRONTOS");
        addTerminalLog("Sensor auditivo desativado.");
    } else {
        await requestMicPermission();
        isManualListening = true;
        isListening = true;
        try {
            recognition.start();
            setSystemStatus("LISTENING", "ESCUTANDO COMANDO DO SENHOR THIAGO...");
        } catch (e) {
            console.warn("SpeechRecognition em andamento:", e);
        }
    }
}

// --- CÂMERA DO CELULAR (WEBCAM DO SMARTPHONE) ---
async function toggleMobileCamera() {
    if (isUsingMobileCam) {
        // Alterna entre frontal e traseira se já estiver ativa
        mobileFacingMode = (mobileFacingMode === "environment") ? "user" : "environment";
        if (mobileStream) {
            mobileStream.getTracks().forEach(t => t.stop());
        }
    } else {
        isUsingMobileCam = true;
    }

    try {
        mobileStream = await navigator.mediaDevices.getUserMedia({
            video: { 
                facingMode: mobileFacingMode,
                width: { ideal: 1280 },
                height: { ideal: 720 }
            },
            audio: false
        });

        mobileCameraVideo.srcObject = mobileStream;
        mobileCameraVideo.style.display = "block";
        cameraImg.style.display = "none";
        cameraPlaceholder.style.display = "none";
        
        hudLensLabel.innerText = `MOBILE CAM: ${mobileFacingMode === 'environment' ? 'TRASEIRA' : 'FRONTAL'} // ATIVA`;
        btnMobileCamText.innerText = `ALTERNAR CÂMERA (${mobileFacingMode === 'environment' ? 'FRONTAL' : 'TRASEIRA'})`;
        addTerminalLog(`[CÂMERA] Câmera do celular (${mobileFacingMode}) ativada.`);
    } catch (err) {
        console.error("Erro ao abrir câmera do celular:", err);
        alert("Não foi possível acessar a câmera do celular. Verifique as permissões do navegador.");
        isUsingMobileCam = false;
        mobileCameraVideo.style.display = "none";
        btnMobileCamText.innerText = "USAR CÂMERA DO CELULAR";
    }
}

function captureMobileFrameBase64() {
    if (!isUsingMobileCam || !mobileCameraVideo || mobileCameraVideo.videoWidth === 0) {
        return "";
    }
    const canvasTmp = document.createElement("canvas");
    canvasTmp.width = mobileCameraVideo.videoWidth;
    canvasTmp.height = mobileCameraVideo.videoHeight;
    const ctx = canvasTmp.getContext("2d");
    ctx.drawImage(mobileCameraVideo, 0, 0, canvasTmp.width, canvasTmp.height);
    return canvasTmp.toDataURL("image/jpeg", 0.85);
}

// --- ENVIO DE COMANDOS PARA O BACKEND ---
async function sendCommandToJarvis(messageText, forceVision = false, forceScreen = false) {
    if (!messageText.trim()) return;

    userQueryText.innerText = messageText;
    
    let statusMsg = "PROCESSANDO...";
    if (forceScreen) statusMsg = "ANALISANDO MONITOR / TELA...";
    else if (forceVision || isUsingMobileCam) statusMsg = "PROCESSANDO SENSORES ÓPTICOS...";
    
    jarvisResponseText.innerText = statusMsg;
    setSystemStatus(forceScreen ? "ANALYZING_SCREEN" : ((forceVision || isUsingMobileCam) ? "ANALYZING_VISION" : "THINKING"), statusMsg);
    addTerminalLog(`Requisição: "${messageText}"`);

    // Captura imagem do celular se a câmera móvel estiver ligada
    let clientImage = "";
    if (isUsingMobileCam && (forceVision || messageText.toLowerCase().includes("vendo") || messageText.toLowerCase().includes("vê") || messageText.toLowerCase().includes("olhe") || messageText.toLowerCase().includes("foto"))) {
        clientImage = captureMobileFrameBase64();
    }

    try {
        const response = await fetch("/api/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                message: messageText,
                force_vision: forceVision,
                force_screen: forceScreen,
                image_base64: clientImage
            })
        });

        if (!response.ok) {
            throw new Error(`Erro na API (${response.status})`);
        }

        const data = await response.json();
        jarvisResponseText.innerText = data.response_text;
        addTerminalLog(`SPUDER: "${data.response_text.substring(0, 70)}..."`);

        if (data.audio_base64) {
            await playJarvisAudio(data.audio_base64);
        }

    } catch (err) {
        jarvisResponseText.innerText = `Ocorreu uma falha no enlace de dados: ${err.message}`;
        addTerminalLog(`[ERRO] Falha no processamento: ${err.message}`);
        setSystemStatus("ONLINE", "SISTEMAS PRONTOS");
    }
}

function sendQuickCommand(cmd) {
    const isScreen = cmd.includes("tela") || cmd.includes("Screen");
    const isVision = cmd.includes("Câmera") || cmd.includes("vendo");
    sendCommandToJarvis(cmd, isVision, isScreen);
}

// --- CARREGAMENTO DE MEMÓRIAS ---
async function loadMemoryModal() {
    memoryModalContent.innerHTML = "<p>Carregando registros neurais...</p>";
    try {
        const res = await fetch("/api/memory");
        const data = await res.json();
        
        let html = `
            <div class="form-group">
                <label>OPERADOR REGISTRADO</label>
                <div class="gauge-value highlight-green" style="font-size: 16px;">${data.owner_name || 'Thiago'}</div>
                <div class="gauge-sub">${data.owner_profile?.role || 'Criador & Operador Chefe'}</div>
            </div>
            <hr style="border-color: rgba(0,243,255,0.2); margin: 12px 0;">
            <div class="form-group">
                <label>FATOS & PREFERÊNCIAS MEMORIZADAS (${data.facts?.length || 0})</label>
        `;
        
        if (data.facts && data.facts.length > 0) {
            data.facts.forEach(f => {
                html += `
                    <div class="memory-item">
                        <div class="memory-text">${f.fact}</div>
                        <div class="memory-date">${f.timestamp || ''}</div>
                    </div>
                `;
            });
        } else {
            html += `<p style="color: var(--text-dim);">Nenhum fato memorizado ainda. Diga <em>"Spuder, lembre-se que..."</em> para registrar.</p>`;
        }
        
        html += `</div>`;
        memoryModalContent.innerHTML = html;
    } catch (e) {
        memoryModalContent.innerHTML = `<p style="color: var(--red-alert);">Erro ao carregar memórias: ${e.message}</p>`;
    }
}

// --- EVENT LISTENERS ---
function setupEventListeners() {
    chatForm.addEventListener("submit", (e) => {
        e.preventDefault();
        const text = textInput.value.trim();
        if (text) {
            sendCommandToJarvis(text);
            textInput.value = "";
        }
    });

    btnVoiceToggle.addEventListener("click", () => {
        toggleVoiceRecognition();
    });

    btnScanVision.addEventListener("click", () => {
        sendCommandToJarvis("Descreva com precisão o que você está vendo agora através da câmera.", true, false);
    });

    btnScanScreen.addEventListener("click", () => {
        sendCommandToJarvis("Analise detalhadamente o que está exibido na minha tela agora (código, janelas, texto ou gráficos).", false, true);
    });

    if (btnToggleMobileCam) {
        btnToggleMobileCam.addEventListener("click", () => {
            toggleMobileCamera();
        });
    }

    // Modal de Memória
    btnOpenMemory.addEventListener("click", () => {
        loadMemoryModal();
        modalMemory.classList.add("open");
    });

    btnCloseMemory.addEventListener("click", () => {
        modalMemory.classList.remove("open");
    });

    // Modal de Configurações
    btnOpenSettings.addEventListener("click", () => {
        modalSettings.classList.add("open");
    });

    btnCloseSettings.addEventListener("click", () => {
        modalSettings.classList.remove("open");
    });

    btnSaveSettings.addEventListener("click", async () => {
        const key = inputApiKey.value.trim();
        if (key) {
            btnSaveSettings.innerText = "SALVANDO...";
            btnSaveSettings.disabled = true;
            try {
                const endpoint = `${window.location.origin}/api/config/key`;
                const res = await fetch(endpoint, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ api_key: key })
                });
                
                if (!res.ok) throw new Error(`Status ${res.status}`);
                
                const result = await res.json();
                addTerminalLog(result.message || "Chave Gemini atualizada.");
                alert("✓ Chave salva com sucesso, Senhor Thiago!");
                modalSettings.classList.remove("open");
            } catch (err) {
                alert(`Erro ao salvar chave: ${err.message}`);
            } finally {
                btnSaveSettings.innerText = "SALVAR CONFIGURAÇÕES";
                btnSaveSettings.disabled = false;
            }
        } else {
            modalSettings.classList.remove("open");
        }
    });
}
