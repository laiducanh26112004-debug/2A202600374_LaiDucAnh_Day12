from groq import Groq
from context_builder import BuiltContext
from dotenv import load_dotenv
import os
load_dotenv()  
GROQ_API_KEY= os.getenv('GROQ_API_KEY')

SYSTEM_PROMPT = """You are a precise and reliable question-answering assistant.

Rules:
1. Answer ONLY using the provided context passages.
2. Every factual claim MUST be cited using [N] where N is the passage index.
3. If the context does not contain sufficient information, say: "Xin lỗi tôi không có đủ thông tin để trả lời câu hỏi này." (Sorry, I don't have enough information to answer this question.)
4. Do NOT fabricate, infer beyond the text, or use prior knowledge.
5. Be concise and accurate.
"""

USER_TEMPLATE = """Context:
{context}

Question: {query}

Answer (with citations like [1][2]):"""


class LLMGenerator:
    """Generate grounded answers using Groq."""

    def __init__(self, model: str = "openai/gpt-oss-120b"):
        self.client = Groq(api_key=GROQ_API_KEY)
        self.model = model

    def generate_answer(
        self,
        query: str,
        context: BuiltContext,
        max_tokens: int = 1024,
    ) -> str:
        """
        Generate a grounded answer from query + built context.

        Args:
            query: User question.
            context: BuiltContext from ContextBuilder.
            max_tokens: Max tokens for the answer.

        Returns:
            Generated answer string with inline citations.
            with Vietnamese translation. The answer should be concise and directly address the question using only the provided context.
        """
        user_message = USER_TEMPLATE.format(
            context=context.formatted_text,
            query=query,
        )

        response = self.client.chat.completions.create(
            model=self.model,
            max_tokens=max_tokens,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
        )

        return response.choices[0].message.content