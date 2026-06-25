import os
import json
from google import genai
from google.genai import types

class AIEngine:
    def __init__(self, api_key: str = None):
        """
        Initializes the AI Engine with the Gemini API key.
        If api_key is not provided, it attempts to load from environment.
        """
        # Hardcode your Gemini API Key here if you wish:
        self.hardcoded_key = os.getenv("GEMINI_API_KEY", "")
        
        self.api_key = api_key or (self.hardcoded_key if self.hardcoded_key != "YOUR_GEMINI_API_KEY_HERE" else "") or os.getenv("GEMINI_API_KEY")
        self.client = None
        self.generation_model = None
        if self.api_key:
            self.client = genai.Client(api_key=self.api_key)
            
    def set_api_key(self, api_key: str):
        """Sets the API key and configures the SDK Client."""
        self.api_key = api_key
        self.client = genai.Client(api_key=api_key)

    def is_configured(self) -> bool:
        """Checks if the client is initialized."""
        return self.client is not None

    def _clean_error_message(self, error: Exception) -> str:
        msg = str(error)
        try:
            import ast
            start = msg.find('{')
            if start != -1:
                dict_part = msg[start:]
                data = ast.literal_eval(dict_part)
                if isinstance(data, dict) and 'error' in data:
                    return data['error'].get('message', msg)
        except Exception:
            pass
        return msg

    def _get_generation_model(self) -> str:
        """Returns a cached generation model name, resolving it if needed."""
        if self.generation_model is None:
            self.generation_model = self._resolve_generation_model()
        return self.generation_model

    def _resolve_generation_model(self) -> str:
        """Resolves an available text generation model from the API at runtime."""
        if not self.is_configured():
            raise RuntimeError("API Key not configured")

        candidates = [
            "gemini-2.0-flash",
            "gemini-1.5-flash",
            "gemini-2.0-flash-lite",
            "gemini-1.5-flash-lite",
        ]

        for model in candidates:
            try:
                _ = self.client.models.generate_content(
                    model=model,
                    contents="test",
                    config=types.GenerateContentConfig(temperature=0.0),
                )
                return model
            except Exception:
                pass

        model_list = self.client.models.list()
        for m in getattr(model_list, "models", model_list):
            name = getattr(m, "name", None) or getattr(m, "model", None)
            if not name:
                continue
            name = str(name).replace("models/", "")
            supported = (
                getattr(m, "supported_generation_methods", None)
                or getattr(m, "supported_methods", None)
                or getattr(m, "methods", None)
                or ""
            )
            if "generateContent" in str(supported) or not supported:
                return name

        raise RuntimeError(
            "No available text generation model found. "
            "Check ModelService.ListModels for supported models."
        )

    def generate_summary(self, text: str) -> dict:
        """
        Generates a concise summary and a chapter-wise/section-wise breakdown.
        Returns a dictionary with 'concise_summary' and 'sections'.
        """
        if not self.is_configured():
            return {"concise_summary": "API Key not configured", "sections": []}

        prompt = f"""
        Analyze the following text extracted from a study material.
        Provide:
        1. A high-level concise summary of the entire document (approx. 200 words).
        2. A chapter-wise or section-wise breakdown, detailing the key topics discussed, main takeaways, and bullet points.

        Return your response in JSON format matching the following structure:
        {{
            "concise_summary": "Overall summary of the material...",
            "sections": [
                {{
                    "title": "Section/Chapter Title",
                    "summary": "Brief summary of this section...",
                    "key_takeaways": [
                        "Takeaway 1...",
                        "Takeaway 2..."
                    ]
                }}
            ]
        }}
        
        Text to analyze:
        {text[:45000]}
        """
        
        try:
            response = self.client.models.generate_content(
                model=self._get_generation_model(),
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.2
                )
            )
            return json.loads(response.text)
        except Exception as e:
            return {
                "concise_summary": f"Could not generate summary: {self._clean_error_message(e)}",
                "sections": []
            }

    def simplify_concept(self, concept: str, context: str = "") -> dict:
        """
        Explains a complex concept in simple, beginner-friendly terms.
        """
        if not self.is_configured():
            return {"concept": concept, "simple_definition": "API Key not configured", "analogy": "", "example": "", "vocabulary": []}

        context_prompt = f"Use this text context if relevant to the concept: {context[:10000]}" if context else ""
        
        prompt = f"""
        Explain the concept: "{concept}"
        
        {context_prompt}
        
        Provide a beginner-friendly explanation suitable for a student. Your output must include:
        1. A simple definition (in everyday language).
        2. A real-world analogy to help visualize the concept.
        3. A concrete step-by-step example.
        4. Crucial vocabulary or terms related to this concept.
        
        Return your response in JSON format matching the following structure:
        {{
            "concept": "{concept}",
            "simple_definition": "Definition here...",
            "analogy": "Analogy here...",
            "example": "Practical example here...",
            "vocabulary": [
                {{
                    "term": "Term name",
                    "meaning": "Meaning of the term"
                }}
            ]
        }}
        """
        
        try:
            response = self.client.models.generate_content(
                model=self._get_generation_model(),
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.3
                )
            )
            return json.loads(response.text)
        except Exception as e:
            return {
                "concept": concept,
                "simple_definition": f"Could not simplify concept right now: {self._clean_error_message(e)}",
                "analogy": "N/A",
                "example": "N/A",
                "vocabulary": []
            }

    def generate_quiz(self, context: str, num_questions: int = 5) -> dict:
        """
        Generates a set of multiple-choice, true/false, and short answer questions based on the context.
        """
        if not self.is_configured():
            return {"questions": []}

        prompt = f"""
        Based on the following text context, generate {num_questions} educational questions to test a student's knowledge.
        Create a mix of:
        - MCQ (Multiple Choice Questions) - 4 options
        - TF (True/False Questions) - 2 options (True/False)
        - Short Answer Questions - Require a brief answer (1-2 sentences)

        Include the correct answer and a helpful explanation for each.
        Return the result in JSON format matching this schema:
        {{
            "questions": [
                {{
                    "id": 1,
                    "type": "mcq",
                    "question": "Question text...",
                    "options": ["Option A", "Option B", "Option C", "Option D"],
                    "correct_answer": "Option A",
                    "explanation": "Why this is correct..."
                }},
                {{
                    "id": 2,
                    "type": "tf",
                    "question": "True/False statement...",
                    "options": ["True", "False"],
                    "correct_answer": "True",
                    "explanation": "Explanation..."
                }},
                {{
                    "id": 3,
                    "type": "short",
                    "question": "Short answer question...",
                    "correct_answer": "Expected brief answer...",
                    "explanation": "Explanation of the answer..."
                }}
            ]
        }}

        Context:
        {context[:15000]}
        """
        
        try:
            response = self.client.models.generate_content(
                model=self._get_generation_model(),
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.5
                )
            )
            return json.loads(response.text)
        except Exception as e:
            return {
                "questions": [
                    {
                        "id": 1,
                        "type": "mcq",
                        "question": f"Failed to generate quiz: {self._clean_error_message(e)}",
                        "options": ["Error", "None", "Retry", "Check Key"],
                        "correct_answer": "Error",
                        "explanation": "Check API logs."
                    }
                ]
            }

    def generate_flashcards(self, context: str, num_cards: int = 6) -> dict:
        """
        Generates revision flashcards based on the context.
        """
        if not self.is_configured():
            return {"flashcards": []}

        prompt = f"""
        Based on the following context, generate {num_cards} revision flashcards.
        Each card should have a clear, concise question/concept on one side (front) and the answer/explanation on the other (back).
        Focus on key definitions, core concepts, or critical formulas.
        
        Return the result in JSON format matching this schema:
        {{
            "flashcards": [
                {{
                    "id": 1,
                    "question": "Front of card (Question/Term)",
                    "answer": "Back of card (Answer/Explanation)"
                }}
            ]
        }}

        Context:
        {context[:15000]}
        """
        
        try:
            response = self.client.models.generate_content(
                model=self._get_generation_model(),
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.5
                )
            )
            return json.loads(response.text)
        except Exception as e:
            return {
                "flashcards": [
                    {
                        "id": 1,
                        "question": "Error generating flashcards",
                        "answer": self._clean_error_message(e)
                    }
                ]
            }

    def answer_question(self, question: str, retrieved_chunks: list[dict]) -> dict:
        """
        Answers a user question based on the retrieved context chunks.
        Returns a dictionary containing 'answer' and 'sources'.
        """
        if not self.is_configured():
            return {"answer": "API Key not configured", "sources": []}

        context_str = ""
        sources = []
        for i, chunk in enumerate(retrieved_chunks):
            context_str += f"--- Source Chunk {i+1} ---\n{chunk['text']}\n\n"
            sources.append({
                "index": i+1,
                "text_snippet": chunk['text'][:150] + "...",
                "metadata": chunk.get("metadata", {})
            })
            
        prompt = f"""
        You are SmartEdu AI, a friendly and expert academic tutor helping a student.
        Answer the student's question based strictly on the retrieved context from their uploaded notes.
        If the answer cannot be found in the context, politely tell the student that it isn't in their notes, but provide a general educational answer based on your knowledge while clearly marking it as "General Knowledge" rather than "From your notes".
        Be structured, easy to read, use bullet points, bold key terms, and keep it educational.

        Student Question:
        {question}

        Retrieved Notes Context:
        {context_str}
        
        Provide the answer.
        """
        
        try:
            response = self.client.models.generate_content(
                model=self._get_generation_model(),
                contents=prompt
            )
            return {
                "answer": response.text,
                "sources": sources
            }
        except Exception as e:
            return {
                "answer": f"Error processing question: {self._clean_error_message(e)}",
                "sources": []
            }

    def _resolve_embedding_model(self) -> str:
        """Resolve an embeddings-capable model from the API at runtime.

        This prevents hardcoding a model name that might not exist for the user's
        API version/account.
        """
        if not self.is_configured():
            raise RuntimeError("API Key not configured")

        # Common candidates (used as a quick path). If none work, we fall back to
        # searching the model list.
        candidates = [
            "models/gemini-embedding-001",
            "gemini-embedding-001",
            "models/text-embedding-004",
            "text-embedding-004",
        ]

        # 1) Try candidates first (fast)
        for model in candidates:
            try:
                _ = self.client.models.embed_content(
                    model=model if model.startswith("models/") else model,
                    contents="test",
                    config=types.EmbedContentConfig(task_type="RETRIEVAL_DOCUMENT"),
                )
                return model.replace("models/", "")
            except Exception:
                pass

        # 2) List models and pick the first embedding-capable one
        try:
            model_list = self.client.models.list()
            # The SDK models.list() return object shape can differ by version.
            # We defensively read attributes.
            for m in getattr(model_list, "models", model_list):
                name = getattr(m, "name", None) or getattr(m, "model", None)
                if not name:
                    continue

                # Heuristics: embedding model names typically include 'embedding'
                if "embedding" not in str(name):
                    continue

                # Some SDKs expose supported methods; we try to detect embedContent.
                supported_methods = (
                    getattr(m, "supported_generation_methods", None)
                    or getattr(m, "supported_methods", None)
                    or getattr(m, "methods", None)
                    or None
                )

                if supported_methods is not None:
                    supported_str = str(supported_methods).lower()
                    if "embed" not in supported_str:
                        continue

                # Try embedding with this model
                try:
                    _ = self.client.models.embed_content(
                        model=name,
                        contents="test",
                        config=types.EmbedContentConfig(task_type="RETRIEVAL_DOCUMENT"),
                    )
                    return str(name).replace("models/", "")
                except Exception:
                    continue

        except Exception as e:
            raise RuntimeError(f"Failed to list models for embedding resolution: {str(e)}")

        raise RuntimeError(
            "No embeddings-capable model found. "
            "Your API key/account may not have embedding support, "
            "or the SDK/API version doesn't support embedContent. "
            "Check ModelService.ListModels and available methods."
        )

    def get_embedding(self, text: str) -> list[float]:
        """Generates a vector embedding for the input text."""
        if not self.is_configured():
            raise RuntimeError("API Key not configured")

        model = self._resolve_embedding_model()
        try:
            response = self.client.models.embed_content(
                model=model,
                contents=text,
                config=types.EmbedContentConfig(task_type="RETRIEVAL_DOCUMENT"),
            )
            return response.embeddings[0].values
        except Exception as e:
            raise RuntimeError(f"Failed to generate embeddings using model '{model}': {str(e)}")

    def get_embeddings_batch(self, texts: list[str]) -> list[list[float]]:
        """Generates vector embeddings for a batch of texts."""
        if not self.is_configured():
            raise RuntimeError("API Key not configured")

        model = self._resolve_embedding_model()
        try:
            response = self.client.models.embed_content(
                model=model,
                contents=texts,
                config=types.EmbedContentConfig(task_type="RETRIEVAL_DOCUMENT"),
            )
            return [emb.values for emb in response.embeddings]
        except Exception as e:
            raise RuntimeError(f"Failed to generate batch embeddings using model '{model}': {str(e)}")

