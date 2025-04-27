# adventure_manager.py
import re
from owlmind.pipeline import ModelProvider

class AdventureManager:
    """
    Tracks per-user story state, including current quiz question
    and correct answer metadata.
    """
    def __init__(self, provider: ModelProvider, model: str):
        self.provider = provider
        self.model    = model
        self.sessions = {}  # uid -> { 'history': [...], 'pending_quiz': {question,choices,answer} }

    def start(self, uid: str, theme: str, stats: dict) -> str:
        prompt = (
            f"You are the GM for a Fallout-style adventure. "
            f"The player’s SPECIAL stats are {stats}. "
            f"Begin a short scene about **{theme}**, then at the end ask ONE multiple-choice quiz question "
            f"on that same subject. "
            f"Format your question like:\n\n"
            f"Q: <question>\nChoices: A) …  B) …  C) …  D) …\n"
            f"Answer: <correct letter>\n\n"
            f"Wrap the answer key in a tag so we can parse it: `<ans: X>`"
        )
        resp = self.provider.request(prompt, model=self.model)
        # extract answer tag:
        m = re.search(r"<ans:\s*([A-D])>", resp)
        answer = m.group(1) if m else None
        # store session
        self.sessions[uid] = {
            'history': [resp],
            'pending_quiz': {
                'question': resp.split("Q:")[1].split("Choices:")[0].strip(),
                'choices': resp.split("Choices:")[1].split("<ans:")[0].strip(),
                'answer': answer
            }
        }
        # send everything *before* the tag
        return resp.split("<ans:")[0].strip()

    def answer(self, uid: str, guess: str) -> (bool, str):
        sess = self.sessions.get(uid)
        if not sess or 'pending_quiz' not in sess:
            return None, "❌ No quiz in progress. Start one with `/adventure <theme>`."

        quiz = sess['pending_quiz']
        correct = (guess.upper() == quiz['answer'])
        # clear pending quiz so we don’t double-count
        del sess['pending_quiz']
        # continue story
        followup_prompt = (
            f"The player answered **{guess.upper()}** which is "
            f"{'correct' if correct else 'incorrect'} (it was {quiz['answer']}). "
            f"Continue the Fallout adventure, updating the narrative "
            f"and then, if you’d like, ask another question or end the scene."
        )
        resp = self.provider.request(followup_prompt, model=self.model)
        sess['history'].append(resp)
        return correct, resp
