import os
import streamlit as st
import datetime
from src.ai_engine import AIEngine
from src.pdf_processor import extract_text_from_pdf, chunk_text
from src.vector_store import SmartEduVectorStore
from src.study_planner import StudyPlanner
from src.ui_components import get_custom_css, render_concept_card, render_flashcard
from src.voice_helper import voice_input_button

# ---------------------------------------------------------
# Page Configuration & UI Initialization
# ---------------------------------------------------------
st.set_page_config(
    page_title="SmartEdu AI - Student Learning Hub",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject custom CSS styles (typography, glassmorphism, 3D flip card animations)
st.markdown(get_custom_css(), unsafe_allow_html=True)

# Initialize Session States
if "ai_engine" not in st.session_state:
    st.session_state["ai_engine"] = AIEngine()
if "vector_store" not in st.session_state:
    st.session_state["vector_store"] = None
if "pdf_processed" not in st.session_state:
    st.session_state["pdf_processed"] = False
if "pdf_text" not in st.session_state:
    st.session_state["pdf_text"] = ""
if "pdf_chunks" not in st.session_state:
    st.session_state["pdf_chunks"] = []
if "summary_data" not in st.session_state:
    st.session_state["summary_data"] = None
if "concept_cache" not in st.session_state:
    st.session_state["concept_cache"] = {}
if "quiz_data" not in st.session_state:
    st.session_state["quiz_data"] = None
if "quiz_submitted" not in st.session_state:
    st.session_state["quiz_submitted"] = False
if "quiz_answers" not in st.session_state:
    st.session_state["quiz_answers"] = {}
if "flashcards_data" not in st.session_state:
    st.session_state["flashcards_data"] = None
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []
if "study_plan" not in st.session_state:
    st.session_state["study_plan"] = ""
if "last_voice_transcript" not in st.session_state:
    st.session_state["last_voice_transcript"] = ""

ai_engine = st.session_state["ai_engine"]

# ---------------------------------------------------------
# Sidebar Elements (API Key Setup & PDF Upload)
# ---------------------------------------------------------
st.sidebar.markdown("<h2 style='text-align: center; margin-bottom: 0;'>🎓 SmartEdu AI</h2>", unsafe_allow_html=True)
st.sidebar.markdown("<p style='text-align: center; color: #94a3b8; font-size: 0.85rem; margin-top: 0;'>Your Personal AI Study Companion</p>", unsafe_allow_html=True)
st.sidebar.markdown("---")

# 1. API Key Verification
if ai_engine.is_configured():
    st.sidebar.success("🔑 Gemini API Key configured in code.")
else:
    api_key_input = st.sidebar.text_input(
        "🔑 Enter Gemini API Key",
        type="password",
        value=os.getenv("GEMINI_API_KEY", ""),
        help="Get a free key from Google AI Studio"
    )
    
    if api_key_input:
        ai_engine.set_api_key(api_key_input)
        st.sidebar.success("Gemini API Key Configured!")
    else:
        st.sidebar.warning("Please enter your Gemini API Key to activate AI features.")

st.sidebar.markdown("---")

# 2. PDF Document Uploader
st.sidebar.subheader("📂 Upload Study Materials")
uploaded_file = st.sidebar.file_uploader(
    "Choose lecture notes, syllabus, or textbooks (PDF)",
    type=["pdf"]
)

# Handle PDF Extraction on upload
if uploaded_file is not None and not st.session_state["pdf_processed"]:
    if not ai_engine.is_configured():
        st.sidebar.error("Please enter a Gemini API Key first to enable processing embeddings!")
    else:
        with st.sidebar.status("Processing PDF notes...", expanded=True) as status:
            try:
                # Step 1: Text extraction
                status.write("Reading document pages...")
                extracted_text = extract_text_from_pdf(uploaded_file)
                st.session_state["pdf_text"] = extracted_text
                
                # Step 2: Text chunking
                status.write("Chunking text content...")
                chunks = chunk_text(extracted_text, chunk_size=1000, chunk_overlap=200)
                st.session_state["pdf_chunks"] = chunks
                
                # Step 3: Embed & index into Vector Store
                status.write("Generating embeddings and building database...")
                vector_store = SmartEduVectorStore(ai_engine)
                vector_store.initialize_db(chunks)
                st.session_state["vector_store"] = vector_store
                
                st.session_state["pdf_processed"] = True
                status.update(label="Document indexed successfully!", state="complete")
                
                # Reset downstream caches on new document upload
                st.session_state["summary_data"] = None
                st.session_state["quiz_data"] = None
                st.session_state["flashcards_data"] = None
                st.session_state["chat_history"] = []
                st.session_state["study_plan"] = ""
                st.rerun()
            except Exception as e:
                status.update(label=f"Error processing document: {e}", state="error")

# Display status of current document
if st.session_state["pdf_processed"]:
    st.sidebar.info(f"📄 **Current Doc:** {uploaded_file.name}\n\n🧩 **Chunks:** {len(st.session_state['pdf_chunks'])} segments indexed")
    if st.sidebar.button("Clear Document", type="secondary"):
        st.session_state["pdf_processed"] = False
        st.session_state["pdf_text"] = ""
        st.session_state["pdf_chunks"] = []
        st.session_state["vector_store"] = None
        st.session_state["summary_data"] = None
        st.session_state["quiz_data"] = None
        st.session_state["flashcards_data"] = None
        st.session_state["chat_history"] = []
        st.session_state["study_plan"] = ""
        st.rerun()

# ---------------------------------------------------------
# Main Page Router / Tab Setup
# ---------------------------------------------------------
st.markdown("<h1>SmartEdu AI Learning Platform</h1>", unsafe_allow_html=True)

# Verify setup
if not ai_engine.is_configured():
    st.info("💡 **Welcome to SmartEdu AI!** Get started by entering your **Gemini API Key** in the sidebar. Once configured, upload your notes to unlock summarized topics, custom study plans, active recall quizzes, and interactive flashcards!")
    st.image("https://images.unsplash.com/photo-1501504905252-473c47e087f8?auto=format&fit=crop&q=80&w=800", caption="Enhance your learning efficiency", use_container_width=True)
elif not st.session_state["pdf_processed"]:
    st.info("📂 **Ready to Learn!** Please upload a lecture PDF or study material in the sidebar to start summarizing and generating revision assets.")
    
    # Showcase standard Concept Simplifier & Study Planner even without PDF
    st.markdown("---")
    st.subheader("Explore Features Available Without Documents:")
    col1, col2 = st.columns(2)
    with col1:
        with st.container(border=True):
            st.markdown("### 💡 Concept Simplifier")
            st.write("Understand any complex topic in simple language with analogies.")
            quick_concept = st.text_input("Enter a concept to simplify:", placeholder="e.g. TCP/IP, Photosynthesis, Quantum Computing")
            if st.button("Simplify Concept", key="quick_simplify"):
                if quick_concept:
                    with st.spinner("Simplifying..."):
                        res = ai_engine.simplify_concept(quick_concept)
                        st.markdown(render_concept_card(res), unsafe_allow_html=True)
                else:
                    st.warning("Please enter a concept name.")
    with col2:
        with st.container(border=True):
            st.markdown("### 📅 Study Planner")
            st.write("Generate a detailed study planner based on your exam date.")
            quick_date = st.date_input("Exam Date:", min_value=datetime.date.today(), key="quick_date")
            quick_pct = st.slider("Completion %:", 0, 100, 30, key="quick_pct")
            quick_weak = st.text_input("Weak Topics:", placeholder="e.g. Dynamic Programming, Recursion", key="quick_weak")
            if st.button("Generate Study Plan", key="quick_plan"):
                with st.spinner("Generating..."):
                    planner = StudyPlanner(ai_engine)
                    plan = planner.generate_plan(quick_date, quick_pct, quick_weak)
                    st.markdown(plan)
else:
    # Full suite of tools once PDF notes are uploaded
    tab_summary, tab_concept, tab_quiz, tab_flashcard, tab_doubt, tab_plan = st.tabs([
        "📊 Summary & Breakdown",
        "💡 Concept Simplifier",
        "🎯 Quiz Zone",
        "🎴 Flashcard Deck",
        "💬 AI Doubt Solver",
        "📅 Study Planner"
    ])

    # ---------------------------------------------------------
    # TAB 1: AI Summary
    # ---------------------------------------------------------
    with tab_summary:
        st.subheader("Document Summarization")
        st.write("AI-generated summaries split by core chapters or content sections.")
        
        # Check cache or generate
        if st.session_state["summary_data"] is None:
            if st.button("✨ Generate AI Summary", type="primary"):
                with st.spinner("Analyzing document content to extract key insights..."):
                    summary = ai_engine.generate_summary(st.session_state["pdf_text"])
                    st.session_state["summary_data"] = summary
                    st.rerun()
        else:
            summary = st.session_state["summary_data"]
            
            # Render Concise Summary
            st.markdown("<div class='smart-card'>", unsafe_allow_html=True)
            st.markdown("### 📝 Concise Overview")
            st.write(summary.get("concise_summary", ""))
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Render Section breakdowns
            st.markdown("### 📑 Section-wise Detailed Breakdown")
            for i, section in enumerate(summary.get("sections", [])):
                with st.expander(f"📌 Section {i+1}: {section.get('title', 'Chapter Overview')}", expanded=True):
                    st.write(section.get("summary", ""))
                    st.write("**Key Takeaways:**")
                    for takeaway in section.get("key_takeaways", []):
                        st.markdown(f"- {takeaway}")

    # ---------------------------------------------------------
    # TAB 2: Concept Simplifier
    # ---------------------------------------------------------
    with tab_concept:
        st.subheader("Concept Simplifier")
        st.write("Extract difficult topics from your notes or search them here, and the AI will explain them in beginner-friendly language.")
        
        concept_input = st.text_input("What concept from this document would you like simplified?", placeholder="e.g. OSI Model, Backpropagation, Cellular Respiration")
        
        if st.button("Explain in Simple Terms", type="primary"):
            if concept_input:
                with st.spinner(f"Breaking down '{concept_input}'..."):
                    # We pass the full text as context so the model can customize the definition to the lecture slides/textbook
                    context = st.session_state["pdf_text"][:8000]
                    res = ai_engine.simplify_concept(concept_input, context)
                    st.session_state["concept_cache"][concept_input] = res
            else:
                st.warning("Please enter a concept name.")
                
        # Display simplified concept cards
        if concept_input in st.session_state["concept_cache"]:
            card_data = st.session_state["concept_cache"][concept_input]
            st.markdown(render_concept_card(card_data), unsafe_allow_html=True)

    # ---------------------------------------------------------
    # TAB 3: Quiz Zone
    # ---------------------------------------------------------
    with tab_quiz:
        st.subheader("Quiz Zone")
        st.write("Generate interactive quizzes from your study material to practice active recall.")
        
        col_setup, col_quiz = st.columns([1, 3])
        
        with col_setup:
            st.markdown("<div class='smart-card'>", unsafe_allow_html=True)
            st.markdown("#### Configure Quiz")
            num_q = st.slider("Number of questions:", 3, 10, 5)
            
            if st.button("🎲 Generate New Quiz", type="primary"):
                with st.spinner("Extracting content and formulating questions..."):
                    # Retrieve a random/varied portion of text or select representative chunks
                    context = "\n".join(st.session_state["pdf_chunks"][:10])
                    quiz = ai_engine.generate_quiz(context, num_q)
                    st.session_state["quiz_data"] = quiz
                    st.session_state["quiz_submitted"] = False
                    st.session_state["quiz_answers"] = {}
                    st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
            
        with col_quiz:
            if st.session_state["quiz_data"] is None:
                st.info("Click **Generate New Quiz** on the left to start testing your knowledge!")
            else:
                quiz = st.session_state["quiz_data"]
                questions = quiz.get("questions", [])
                
                form_placeholder = st.container()
                
                with form_placeholder:
                    st.markdown("### Test Your Understanding")
                    
                    correct_count = 0
                    total_scorable = 0
                    
                    for idx, q in enumerate(questions):
                        q_id = q.get("id", idx)
                        q_type = q.get("type", "mcq")
                        q_text = q.get("question", "")
                        
                        st.markdown(f"**Question {idx+1}:** {q_text}")
                        
                        # Handle MCQ / True False
                        if q_type in ["mcq", "tf"]:
                            options = q.get("options", ["True", "False"] if q_type == "tf" else [])
                            
                            # Determine index of previous selection
                            selected_val = st.session_state["quiz_answers"].get(q_id, None)
                            try:
                                default_idx = options.index(selected_val) if selected_val else 0
                            except ValueError:
                                default_idx = 0
                                
                            user_ans = st.radio(
                                f"Select option for Q{idx+1}",
                                options,
                                index=default_idx,
                                key=f"q_radio_{q_id}",
                                label_visibility="collapsed"
                            )
                            st.session_state["quiz_answers"][q_id] = user_ans
                            
                            # Grading feedback
                            if st.session_state["quiz_submitted"]:
                                correct_ans = q.get("correct_answer", "")
                                if user_ans == correct_ans:
                                    st.markdown(f"<div class='quiz-feedback-correct'>🟢 Correct! Explanation: {q.get('explanation', '')}</div>", unsafe_allow_html=True)
                                    correct_count += 1
                                else:
                                    st.markdown(f"<div class='quiz-feedback-incorrect'>🔴 Incorrect. Correct Answer: {correct_ans}<br/>Explanation: {q.get('explanation', '')}</div>", unsafe_allow_html=True)
                                total_scorable += 1
                        
                        # Handle Short Answer
                        elif q_type == "short":
                            user_ans = st.text_input(
                                f"Type your answer for Q{idx+1}",
                                value=st.session_state["quiz_answers"].get(q_id, ""),
                                key=f"q_text_{q_id}",
                                label_visibility="collapsed"
                            )
                            st.session_state["quiz_answers"][q_id] = user_ans
                            
                            if st.session_state["quiz_submitted"]:
                                st.info(f"💡 **Expected Answer:** {q.get('correct_answer', '')}\n\n**AI Explanation:** {q.get('explanation', '')}")
                        
                        st.markdown("---")
                    
                    if not st.session_state["quiz_submitted"]:
                        if st.button("🚀 Submit Answers", type="primary"):
                            st.session_state["quiz_submitted"] = True
                            st.rerun()
                    else:
                        st.balloons()
                        # Render Score
                        if total_scorable > 0:
                            score_pct = (correct_count / total_scorable)
                            st.subheader(f"Your Score: {correct_count} / {total_scorable} ({int(score_pct*100)}%)")
                            st.progress(score_pct)
                        else:
                            st.success("Quiz completed! Review the short answers above.")
                            
                        if st.button("🔄 Try Again / Reset", type="secondary"):
                            st.session_state["quiz_submitted"] = False
                            st.session_state["quiz_answers"] = {}
                            st.rerun()

    # ---------------------------------------------------------
    # TAB 4: Flashcards
    # ---------------------------------------------------------
    with tab_flashcard:
        st.subheader("Interactive Revision Flashcards")
        st.write("Generate interactive 3D cards that flip when clicked. Excellent for memorizing key formulas, terms, and definitions.")
        
        col1, col2 = st.columns([1, 4])
        
        with col1:
            st.markdown("<div class='smart-card'>", unsafe_allow_html=True)
            st.markdown("#### Configure Deck")
            num_cards = st.slider("Number of flashcards:", 3, 12, 6)
            
            if st.button("🎴 Generate Flashcards", type="primary"):
                with st.spinner("Extracting terminology and compiling review cards..."):
                    # Use a portion of chunks for content extraction
                    context = "\n".join(st.session_state["pdf_chunks"][:8])
                    cards = ai_engine.generate_flashcards(context, num_cards)
                    st.session_state["flashcards_data"] = cards
                    st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
            
        with col2:
            if st.session_state["flashcards_data"] is None:
                st.info("Click **Generate Flashcards** to generate a custom review deck!")
            else:
                cards = st.session_state["flashcards_data"].get("flashcards", [])
                
                # Render in a clean grid
                cols = st.columns(3)
                for idx, card in enumerate(cards):
                    col_idx = idx % 3
                    with cols[col_idx]:
                        card_html = render_flashcard(
                            card_id=idx + 1,
                            question=card.get("question", ""),
                            answer=card.get("answer", "")
                        )
                        st.markdown(card_html, unsafe_allow_html=True)

    # ---------------------------------------------------------
    # TAB 5: AI Doubt Solver (RAG Chat with Voice)
    # ---------------------------------------------------------
    with tab_doubt:
        st.subheader("AI Doubt Solver & Chat")
        st.write("Ask questions about your notes or chat with the document. Supports voice inputs.")
        
        # Display chat interface
        chat_container = st.container(height=350)
        
        with chat_container:
            if not st.session_state["chat_history"]:
                st.chat_message("assistant").write("Hello! I am your study assistant. Ask me anything about your uploaded document, or tap the microphone to ask via voice.")
            else:
                for msg in st.session_state["chat_history"]:
                    st.chat_message(msg["role"]).write(msg["content"])
                    
        # Input methods container
        st.write("---")
        
        # Setup two columns: one for textual typing and one for browser microphone
        col_text, col_voice = st.columns([4, 1])
        
        with col_voice:
            st.markdown("##### 🎙️ Voice Input")
            voice_transcript = voice_input_button()
            
            # Reactive voice update capture
            if voice_transcript and voice_transcript != st.session_state["last_voice_transcript"]:
                st.session_state["last_voice_transcript"] = voice_transcript
                # Queue voice transcript directly as user query
                user_query = voice_transcript
            else:
                user_query = None
                
        with col_text:
            text_query = st.chat_input("Ask a doubt about the material:")
            if text_query:
                user_query = text_query
                
        # Handle user queries (either text or voice transcription)
        if user_query:
            # Append user message
            st.session_state["chat_history"].append({"role": "user", "content": user_query})
            
            with st.spinner("Searching document notes and formulating answer..."):
                # RAG: Retrieve top matching chunks
                retrieved_chunks = st.session_state["vector_store"].search(user_query, k=4)
                
                # QA: Call Gemini
                response_data = ai_engine.answer_question(user_query, retrieved_chunks)
                
                # Append assistant reply
                st.session_state["chat_history"].append({"role": "assistant", "content": response_data["answer"]})
                st.rerun()

    # ---------------------------------------------------------
    # TAB 6: Personalized Study Planner
    # ---------------------------------------------------------
    with tab_plan:
        st.subheader("Personalized Study Plan")
        st.write("Generate a highly optimized, day-by-day and week-by-week study plan tailored to your upcoming exam, current progress, and weak areas.")
        
        col_inputs, col_plan = st.columns([1, 2])
        
        with col_inputs:
            st.markdown("<div class='smart-card'>", unsafe_allow_html=True)
            st.markdown("#### Study Plan Settings")
            
            exam_date = st.date_input(
                "📅 Scheduled Exam Date",
                value=datetime.date.today() + datetime.timedelta(days=14),
                min_value=datetime.date.today()
            )
            
            completion_pct = st.slider(
                "📈 Current Syllabus Progress (%)",
                min_value=0,
                max_value=100,
                value=30,
                help="What percentage of the syllabus have you read or reviewed so far?"
            )
            
            weak_topics = st.text_area(
                "⚠️ Weak Topics / Concepts",
                placeholder="List topics you find hardest (e.g., Dijkstra's algorithm, stoichiometry, photosynthesis phases)...",
                height=100
            )
            
            generate_clicked = st.button("📅 Generate Study Plan", type="primary")
            st.markdown("</div>", unsafe_allow_html=True)
            
        with col_plan:
            if generate_clicked:
                with st.spinner("Designing study schedules based on your timeline and topics..."):
                    # Get summary context if we have it
                    summary_context = ""
                    if st.session_state["summary_data"] is not None:
                        summary_context = st.session_state["summary_data"].get("concise_summary", "")
                    else:
                        summary_context = st.session_state["pdf_text"][:2000] # Use a snippet of pdf text if no summary generated yet
                        
                    planner = StudyPlanner(ai_engine)
                    plan_markdown = planner.generate_plan(
                        exam_date=exam_date,
                        completion_pct=completion_pct,
                        weak_topics=weak_topics,
                        doc_summary=summary_context
                    )
                    st.session_state["study_plan"] = plan_markdown
            
            if st.session_state["study_plan"]:
                st.markdown(st.session_state["study_plan"])
            else:
                st.info("Fill out the settings on the left and click **Generate Study Plan** to create your study schedule!")
