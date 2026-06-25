import streamlit.components.v1 as components

def voice_input_button():
    """
    Renders a clean, styled microphone button inside a custom HTML/JS component.
    Uses browser Web Speech API (SpeechRecognition) to transcribe speech locally
    in the client browser, then sends the transcribed text back to the Streamlit app.
    """
    html_code = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {
                margin: 0;
                padding: 0;
                background-color: transparent;
                color: #f1f5f9;
                font-family: 'Plus Jakarta Sans', system-ui, -apple-system, sans-serif;
                overflow: hidden;
            }
            .mic-container {
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                gap: 8px;
                padding: 12px;
                border-radius: 12px;
                background: rgba(30, 41, 59, 0.4);
                border: 1px solid rgba(255, 255, 255, 0.08);
            }
            .mic-button {
                background: linear-gradient(135deg, #a855f7 0%, #6366f1 100%);
                border: none;
                color: white;
                width: 54px;
                height: 54px;
                border-radius: 50%;
                cursor: pointer;
                display: flex;
                align-items: center;
                justify-content: center;
                box-shadow: 0 4px 15px rgba(168, 85, 247, 0.3);
                transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
            }
            .mic-button:hover {
                transform: scale(1.08);
                box-shadow: 0 6px 20px rgba(168, 85, 247, 0.5);
            }
            .mic-button:active {
                transform: scale(0.95);
            }
            .mic-button.recording {
                background: #ef4444;
                box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.7);
                animation: pulse 1.5s infinite;
            }
            .status-text {
                font-size: 0.8rem;
                color: #94a3b8;
                min-height: 18px;
                font-weight: 500;
            }
            .transcript-display {
                font-size: 0.85rem;
                background: rgba(15, 23, 42, 0.6);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 6px;
                padding: 8px 12px;
                width: 100%;
                box-sizing: border-box;
                min-height: 38px;
                display: none;
                color: #38bdf8;
                max-height: 60px;
                overflow-y: auto;
            }
            @keyframes pulse {
                0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.5); }
                70% { transform: scale(1.05); box-shadow: 0 0 0 12px rgba(239, 68, 68, 0); }
                100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(239, 68, 68, 0); }
            }
            
            /* SVG Styling */
            svg {
                width: 22px;
                height: 22px;
                fill: currentColor;
            }
        </style>
    </head>
    <body>
        <div class="mic-container">
            <button class="mic-button" id="start-btn" title="Click to Speak">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3zm5.3-3c0 3-2.54 5.1-5.3 5.1S6.7 14 6.7 11H5c0 3.41 2.72 6.23 6 6.72V21h2v-3.28c3.28-.48 6-3.3 6-6.72h-1.7z"/></svg>
            </button>
            <div class="status-text" id="status">Click mic to ask a doubt</div>
            <div class="transcript-display" id="transcript-box"></div>
        </div>

        <script>
            // Streamlit communications function using postMessage protocol
            function sendToStreamlit(value) {
                if (window.parent && window.parent.postMessage) {
                    const message = {
                        type: 'streamlit:setComponentValue',
                        value: value
                    };
                    window.parent.postMessage(message, '*');
                }
            }

            const startBtn = document.getElementById('start-btn');
            const statusText = document.getElementById('status');
            const transcriptBox = document.getElementById('transcript-box');
            
            let recognition = null;
            let isRecording = false;

            if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
                const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
                recognition = new SpeechRecognition();
                recognition.continuous = false;
                recognition.interimResults = false;
                recognition.lang = 'en-US';

                recognition.onstart = () => {
                    isRecording = true;
                    startBtn.classList.add('recording');
                    statusText.innerText = "Listening... Speak now.";
                    transcriptBox.style.display = "none";
                };

                recognition.onerror = (event) => {
                    console.error(event);
                    statusText.innerText = "Error: " + event.error;
                    startBtn.classList.remove('recording');
                    isRecording = false;
                };

                recognition.onend = () => {
                    startBtn.classList.remove('recording');
                    isRecording = false;
                    if (statusText.innerText.startsWith("Listening")) {
                        statusText.innerText = "Click mic to ask a doubt";
                    }
                };

                recognition.onresult = (event) => {
                    const resultText = event.results[0][0].transcript;
                    transcriptBox.innerText = resultText;
                    transcriptBox.style.display = "block";
                    statusText.innerText = "Transcribed!";
                    // Push data to Python Streamlit interface
                    sendToStreamlit(resultText);
                };

                startBtn.addEventListener('click', () => {
                    if (isRecording) {
                        recognition.stop();
                    } else {
                        recognition.start();
                    }
                });
            } else {
                statusText.innerText = "Speech recognition unsupported in this browser.";
                startBtn.disabled = true;
                startBtn.style.opacity = 0.4;
                startBtn.style.cursor = 'not-allowed';
            }
        </script>
    </body>
    </html>
    """
    # Create the Streamlit HTML component
    return components.html(html_code, height=140)
