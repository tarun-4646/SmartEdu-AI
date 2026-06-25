def get_custom_css():
    """
    Returns custom CSS code to be injected into the Streamlit application.
    Implements a sleek dark mode theme with glassmorphism, glowing borders, custom typography,
    and transitions.
    """
    return """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=Plus+Jakarta+Sans:wght@300;400;500;700&display=swap');

    /* Global Typography Override */
    html, body, [class*="css"], .stText, p, span, h1, h2, h3, h4, h5, h6 {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }
    
    h1, h2, h3, .stSubheader {
        font-family: 'Outfit', sans-serif !important;
        font-weight: 700;
        background: linear-gradient(135deg, #6366f1 0%, #a855f7 50%, #ec4899 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    /* Sleek Container/Card Design */
    .smart-card {
        background: rgba(30, 41, 59, 0.45);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 20px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.2);
        transition: transform 0.3s ease, border-color 0.3s ease;
    }
    .smart-card:hover {
        transform: translateY(-2px);
        border-color: rgba(99, 102, 241, 0.4);
    }
    
    /* Concept Simplifier Layout */
    .concept-title {
        color: #a855f7;
        font-weight: bold;
        font-size: 1.4rem;
        margin-bottom: 10px;
    }
    .analogy-box {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(168, 85, 247, 0.05) 100%);
        border-left: 5px solid #6366f1;
        border-radius: 8px;
        padding: 15px;
        margin: 15px 0;
        font-style: italic;
    }
    .example-box {
        background: rgba(15, 23, 42, 0.6);
        border: 1px solid rgba(99, 102, 241, 0.2);
        border-radius: 8px;
        padding: 15px;
        margin: 15px 0;
    }
    .vocab-tag {
        display: inline-block;
        background: rgba(236, 72, 153, 0.15);
        color: #f472b6;
        border: 1px solid rgba(236, 72, 153, 0.3);
        border-radius: 20px;
        padding: 4px 12px;
        margin: 5px;
        font-size: 0.85rem;
        font-weight: 600;
    }

    /* 3D Flashcard flip structure */
    .flashcard-deck {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
        gap: 20px;
        padding: 15px 0;
    }
    .flip-card-checkbox {
        display: none;
    }
    .flip-card {
        background-color: transparent;
        width: 100%;
        height: 200px;
        perspective: 1000px;
        cursor: pointer;
    }
    .flip-card-inner {
        position: relative;
        width: 100%;
        height: 100%;
        text-align: center;
        transition: transform 0.6s cubic-bezier(0.4, 0, 0.2, 1);
        transform-style: preserve-3d;
    }
    .flip-card-checkbox:checked + .flip-card .flip-card-inner {
        transform: rotateY(180deg);
    }
    .flip-card-front, .flip-card-back {
        position: absolute;
        width: 100%;
        height: 100%;
        -webkit-backface-visibility: hidden;
        backface-visibility: hidden;
        border-radius: 16px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        padding: 20px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        box-sizing: border-box;
    }
    .flip-card-front {
        background: linear-gradient(135deg, #1e1b4b 0%, #2e1065 100%);
        color: #e0e7ff;
        border: 1px solid rgba(99, 102, 241, 0.3);
    }
    .flip-card-back {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        color: #38bdf8;
        transform: rotateY(180deg);
        border: 1px solid rgba(56, 189, 248, 0.3);
        overflow-y: auto;
    }
    .card-label {
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.15em;
        color: rgba(255, 255, 255, 0.4);
        margin-bottom: 8px;
    }
    .card-text {
        font-size: 1.1rem;
        font-weight: 500;
        line-height: 1.4;
    }
    .flip-hint {
        font-size: 0.7rem;
        color: rgba(255, 255, 255, 0.3);
        margin-top: 10px;
    }

    /* Voice input pulse animation */
    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(168, 85, 247, 0.4); }
        70% { box-shadow: 0 0 0 10px rgba(168, 85, 247, 0); }
        100% { box-shadow: 0 0 0 0 rgba(168, 85, 247, 0); }
    }
    .pulse-btn {
        animation: pulse 1.5s infinite;
        border-color: #a855f7 !important;
    }
    
    /* Quiz styling */
    .quiz-option {
        background: rgba(30, 41, 59, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 10px;
        padding: 12px 16px;
        margin: 8px 0;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    .quiz-option:hover {
        background: rgba(99, 102, 241, 0.15);
        border-color: rgba(99, 102, 241, 0.3);
    }
    
    .quiz-feedback-correct {
        background: rgba(16, 185, 129, 0.1);
        border: 1px solid rgba(16, 185, 129, 0.3);
        color: #34d399;
        border-radius: 8px;
        padding: 10px;
        margin: 10px 0;
    }
    
    .quiz-feedback-incorrect {
        background: rgba(239, 68, 68, 0.1);
        border: 1px solid rgba(239, 68, 68, 0.3);
        color: #f87171;
        border-radius: 8px;
        padding: 10px;
        margin: 10px 0;
    }
    </style>
    """

def render_concept_card(concept_data: dict) -> str:
    """
    Renders a beautified, custom HTML concept explanation layout.
    """
    vocab_html = "".join([f'<span class="vocab-tag" title="{v["meaning"]}">{v["term"]}</span>' for v in concept_data.get("vocabulary", [])])
    
    html = f"""
    <div class="smart-card">
        <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid rgba(255,255,255,0.08); padding-bottom:10px; margin-bottom:15px;">
            <div class="concept-title">💡 {concept_data.get('concept', '')}</div>
            <span style="font-size:0.75rem; background:rgba(168,85,247,0.2); color:#c084fc; padding:4px 10px; border-radius:12px;">Concept Breakdown</span>
        </div>
        
        <div style="font-weight: 500; font-size: 1.05rem; line-height: 1.5; color: #f1f5f9; margin-bottom:15px;">
            {concept_data.get('simple_definition', '')}
        </div>
        
        <div class="analogy-box">
            <strong>🔮 Real-World Analogy:</strong><br/>
            {concept_data.get('analogy', '')}
        </div>
        
        <div class="example-box">
            <strong>📝 Step-by-Step Example:</strong><br/>
            <p style="margin-top:8px; line-height:1.5; color: #cbd5e1;">{concept_data.get('example', '')}</p>
        </div>
        
        {f'<div style="margin-top:15px;"><strong>🔑 Related Terminology:</strong><br/><div style="margin-top:8px;">{vocab_html}</div></div>' if vocab_html else ''}
    </div>
    """
    return html

def render_flashcard(card_id: int, question: str, answer: str) -> str:
    """
    Generates the HTML structure for a single 3D interactive flip card.
    Uses the label checkbox hack to support clicking to flip without javascript.
    """
    checkbox_id = f"card_toggle_{card_id}"
    
    html = f"""
    <div style="margin-bottom: 20px;">
        <input type="checkbox" id="{checkbox_id}" class="flip-card-checkbox" />
        <label for="{checkbox_id}" class="flip-card">
            <div class="flip-card-inner">
                <div class="flip-card-front">
                    <div class="card-label">Front • Card #{card_id}</div>
                    <div class="card-text">{question}</div>
                    <div class="flip-hint">🔄 Tap to Reveal Answer</div>
                </div>
                <div class="flip-card-back">
                    <div class="card-label">Back • Answer</div>
                    <div class="card-text">{answer}</div>
                    <div class="flip-hint">🔄 Tap to Flip Back</div>
                </div>
            </div>
        </label>
    </div>
    """
    return html
