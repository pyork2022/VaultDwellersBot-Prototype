import random
from owlmind.pipeline import ModelProvider

class QuizManager:
    provider = None  # This will be set when the bot starts

    @classmethod
    def initialize(cls, model_provider: ModelProvider):
        """ Assign the ModelProvider (usually LLaMA through Ollama) """
        cls.provider = model_provider

    @classmethod
    def create_quiz(cls, subject: str) -> dict:
        """
        Generate a quiz question dynamically based on the user's subject.
        Returns a dictionary: {'question': str, 'answer': str}
        """
        if not cls.provider:
            raise ValueError("QuizManager provider is not initialized.")

        # Custom prompt to generate more involved questions
        prompt = (
            f"Create a challenging and detailed quiz question about '{subject}'. "
            f"The question should be specific to the topic and focus on advanced details. "
            f"Make sure the question tests deep understanding and includes specific terminology. "
            f"Provide the answer in the following format:\n\n"
            f"Question: <detailed question>\nAnswer: <the correct, well-explained answer>"
        )

        # Request to the provider to generate a quiz question
        response = cls.provider.request(prompt)

        # Log the response for debugging purposes
        print(f"AI Response: {response}")

        # Parse the response to extract the question and answer
        question_text = ""
        answer_text = ""

        if "Question:" in response and "Answer:" in response:
            # Split at "Question:" and "Answer:"
            question_part = response.split("Question:")[1].strip()
            if "Answer:" in question_part:
                question_text, answer_text = question_part.split("Answer:", 1)
                question_text = question_text.strip()
                answer_text = answer_text.strip()

        # If parsing fails, fallback to a default question format
        if not question_text or not answer_text:
            question_text = f"What is an advanced concept in {subject}?"
            answer_text = "A nuanced explanation of the topic."

        # Return the formatted question and answer
        return {
            "question": f"🔎 **Skill Check**: {question_text}",
            "answer": answer_text
        }

    @staticmethod
    def evaluate(user_answer: str, correct_answer: str) -> bool:
        """Evaluate user answer (case-insensitive match)."""
        user = user_answer.strip().lower()
        correct = correct_answer.strip().lower()

        # If the answer is AI-generated and we have a fallback question, we can check for relevance
        if correct.startswith("A nuanced explanation of"):
            # We only want answers that are somewhat related to the subject, not just any answer
            keywords = correct_answer.split(" ")
            # Check if the user answer contains relevant keywords
            if all(keyword in user for keyword in keywords):
                return True
            return False

        # Strict matching for factual questions
        return user == correct
