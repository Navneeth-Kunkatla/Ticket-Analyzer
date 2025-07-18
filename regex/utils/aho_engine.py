import ahocorasick
import nltk
from nltk.stem import WordNetLemmatizer
from utils.db import load_keywords

nltk.download("wordnet", quiet=True)
lemmatizer = WordNetLemmatizer()

class AhoEngine:
    def __init__(self, tool_name, buckets):
        self.tool_name = tool_name
        self.buckets = buckets  # ✅ You pass it in from process_file()

        self.automaton = ahocorasick.Automaton()
        for category, words in buckets.items():
            for word in words:
                # Store both the bucket name & word so we can group matches
                self.automaton.add_word(word.lower().strip(), (category, word.lower().strip()))
        if len(self.automaton) > 0:
            self.automaton.make_automaton()

    def match(self, text):
        matches = {k: [] for k in self.buckets.keys()}
        text_lower = text.lower()
        for _, (bucket, word) in self.automaton.iter(text_lower):
            if word not in matches[bucket]:
                matches[bucket].append(word) 
        return matches

    def is_complete(self, matches):
        ito_count = [
            bool(matches["actions"]),
            bool(matches["applications"]),
            bool(matches["objects"]),
        ]
        if matches.get("non_ito_objects") or matches.get("non_ito_words"):
            return False  # ❌ override

        return sum(ito_count) >= 2

    def is_automatable(self, matches):
        return self.is_complete(matches)
