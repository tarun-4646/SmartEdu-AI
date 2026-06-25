import datetime
from google.genai import types

class StudyPlanner:
    def __init__(self, ai_engine):
        """
        Initializes the StudyPlanner with our AIEngine instance.
        """
        self.ai_engine = ai_engine

    def generate_plan(self, exam_date: datetime.date, completion_pct: int, weak_topics: str, doc_summary: str = "") -> str:
        """
        Queries Gemini to construct a personalized study schedule based on:
        - Exam date (computes remaining prep time)
        - Current syllabus completion rate
        - Specific weak topics identified by the student
        - Document context summaries (if uploaded)
        """
        if not self.ai_engine.is_configured():
            return "Please enter a valid Gemini API Key in the sidebar to generate a study plan."
            
        today = datetime.date.today()
        days_remaining = (exam_date - today).days
        
        if days_remaining < 0:
            return "⚠️ **Error:** The exam date you selected is in the past! Please select a future date."
            
        time_context = f"{days_remaining} days" if days_remaining > 0 else "today (Final day)"
        
        # Build prompt
        prompt = f"""
        You are SmartEdu AI, an elite academic success coach. Your goal is to design a realistic, high-impact, and personalized study plan for a student.

        **Student Profile Details:**
        - **Days left until the exam:** {time_context} (Exam Date: {exam_date.strftime('%A, %B %d, %Y')})
        - **Current syllabus progress:** {completion_pct}% of the material is covered.
        - **Weak topics requiring critical focus:** {weak_topics if weak_topics else "None listed (general review)"}
        - **Uploaded Lecture notes summary context:** {doc_summary if doc_summary else "Not provided (use general academic guidelines)"}

        Create a comprehensive, custom study plan in clean Markdown format with the following sections:
        
        ### 📅 1. Strategic Timeline & Pace Assessment
        - Provide an assessment of the current pace. Is the timeline:
          * **Critical/High Urgency** (very few days left, low completion)
          * **Moderate/Steady** (sufficient time, medium completion)
          * **Advanced/Refinement** (lots of time left or high completion)
        - Suggest a daily study hour recommendation (e.g., 2 hours/day, 4 hours/day).

        ### 🎯 2. Phase-Based Study Plan
        Divide the remaining {days_remaining} days into clear, logical phases.
        - **Phase 1: Knowledge Acquisition & Completion** (Covering the remaining {100 - completion_pct}% of the syllabus).
        - **Phase 2: Targeted Weakness Remediation** (Intensive drills on: {weak_topics if weak_topics else 'general areas'}).
        - **Phase 3: Active Recall & Simulated Testing** (Revision, flashcard testing, quiz practice).

        ### 📚 3. Step-by-Step Study Schedule (Markdown Table)
        Provide a weekly/daily roadmap table mapping out what to study. Include:
        - **Time Period** (e.g., Week 1, Day 1-3, etc.)
        - **Study Focus** (Topic or activity)
        - **Suggested Techniques** (e.g., Pomodoro, Feynman technique, Flashcards)
        - **Goal/Deliverable** (What they should accomplish by the end of the period)

        ### 🧠 4. Personalized Study Hacks & Techniques
        Provide specific advice for this student:
        - How to tackle their weak topics specifically using cognitive science principles.
        - Advice on using the SmartEdu AI Quizzes & Flashcards for active recall.
        
        Keep the tone encouraging, professional, and highly motivational. Use emojis and clear bold headings.
        """
        
        try:
            response = self.ai_engine.client.models.generate_content(
                model=self.ai_engine._get_generation_model(),
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.6
                )
            )
            return response.text
        except Exception as e:
            return f"❌ **Error generating study plan:** {self.ai_engine._clean_error_message(e)}"
