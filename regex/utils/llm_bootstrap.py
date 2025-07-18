import os
import json
from openai import OpenAI
from utils.db import save_keywords
import nltk
from nltk.stem import WordNetLemmatizer
import ast

lemmatizer = WordNetLemmatizer()

client = OpenAI(api_key=(""))



def lemmatize_words(words):
    return [lemmatizer.lemmatize(w.lower().strip()) for w in words]


def bootstrap_categories(text, tool_name):
    """
    Calls LLM → categorizes → saves → returns dict.
    Handles markdown formatting.
    """
    prompt = (
    "You are a highly precise **keyword extraction agent** for IT operations.\n"
    "Your sole job is to analyze a sentence and categorize its elements into exactly FIVE lists:\n\n"
    "1️⃣ **actions**: Verbs or phrases describing tasks or operations that can be automated or scripted.\n"
    "2️⃣ **applications**: IT tools, platforms, or software mentioned.\n"
    "3️⃣ **objects**: Digital objects, data, or elements that can be handled programmatically.\n"
    "4️⃣ **non_ito_objects**: Real-world physical objects or contexts that require human physical presence, site work, or cannot be fully automated.\n"
    "5️⃣ **non_ito_words**: Keywords indicating human-in-the-loop requirements, managerial tasks, physical processes, travel, finance, or any scenario that means full automation is impossible.\n\n"
    
    "**✅ IMPORTANT DOMAIN GUIDANCE:**\n"
    "- Classify anything related to real-life physical maintenance, repair, or facilities as `non_ito_objects`.\n"
    "- Classify HR tasks like **bonus**, **leave**, **reimbursement**, **salary**, or **travel booking** as `non_ito_words`.\n"
    "- Facilities words like **coffee**, **printer**, **chairs**, **badge**, **parking**, **pantry**, **ac**, **cleaning** → `non_ito_objects`.\n"
    "- If a word can belong to multiple buckets, pick the most conservative: prefer `non_ito_*`.\n"
    "- For finance, travel, HR, or on-premise tasks → assume `non_ito` by default.\n"
    "- For purely digital workflows with no physical dependency, classify as ITO (actions/applications/objects).\n\n"
    
    "**✅ OUTPUT CONSTRAINTS:**\n"
    "- Always return valid JSON ONLY. Use EXACT keys: `action`, `application`, `object`, `non_ito_object`, `non_ito_words`.\n"
    "- No markdown, no explanations, no comments — just JSON.\n"
    "- Even if a list is empty, include it as an empty list `[]`.\n\n"
    
    "**✅ EXAMPLES:**\n"
    "Sentence: *'Fix the broken coffee machine in pantry'* → `non_ito_objects`: ['coffee machine', 'pantry'], `action`: ['fix'].\n"
    "Sentence: *'Automate asset tracking with RFID'* → `actions`: ['automate'], `applications`: ['RFID'], `objects`: ['asset tracking'].\n\n"
    
    "Your task: be consistent, conservative, and correct.\n\n"
    f"Sentence: {text}\n"
    "Return only JSON."
)


    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are an master keyword categorizer in the IT industry. Your main task is to split IT and Non-IT words and objects"},
            {"role": "user", "content": prompt}
        ],
        temperature=0
    )

    raw = response.choices[0].message.content.strip()
    print(f"[LLM RAW] {raw}")

    try:
        start = raw.find("{")
        end = raw.rfind("}") + 1
        cleaned_json = raw[start:end]
        data = json.loads(cleaned_json)
    except Exception as e:
        print(f"❌ Failed to parse LLM output: {e}")
        return {}

    MAPPING = {
    "action": "actions",
    "application": "applications",
    "object": "objects",
    "non_ito_object": "non_ito_objects",
    "non-ito_words": "non_ito_words"
}

    for k_raw, k_target in MAPPING.items():
        words = data.get(k_raw, [])
        lemmatized = lemmatize_words(words)
        save_keywords(tool_name, k_target, lemmatized)

    return data
