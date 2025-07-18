import pandas as pd
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import path_finder
from utils.aho_engine import AhoEngine
from utils.llm_bootstrap import bootstrap_categories
from utils.db import load_keywords, save_keywords

nltk.download('stopwords')
nltk.download('wordnet')
stop_words = set(stopwords.words('english'))
lemmatizer = WordNetLemmatizer()

def clean_text(text):
    # Basic cleaner: lower, split, remove stopwords, lemmatize
    words = text.lower().split()
    return [lemmatizer.lemmatize(w) for w in words if w not in stop_words]

def process_file(filepath):
    print(f"\n📄 Processing: {filepath}")

    tool_name = filepath.split("\\")[-1].split(".")[0]  # Example: Asset Panda.xlsx -> 'Asset Panda'
    print(f"[DB] Checking buckets for tool: {tool_name}")

    # --- Load from DB ---
    buckets = load_keywords(tool_name)
    total = sum(len(v) for v in buckets.values())
    '''
    print(f"  actions: {len(buckets['actions'])}")
    print(f"  applications: {len(buckets['applications'])}")
    print(f"  objects: {len(buckets['objects'])}")
    print(f"  non_ito_objects: {len(buckets['non_ito_objects'])}")
    print(f"  non-ito_words: {len(buckets['non-ito_words'])}")
'''
    # --- Fallback ---
    if total == 0:
        print(f"[LLM] No existing buckets found. Running bootstrap for {tool_name}...")
        df = pd.read_excel(filepath) if filepath.endswith('.xlsx') else pd.read_csv(filepath)
        text = "\n".join(df.iloc[:, 2].dropna().astype(str).tolist())  # All rows 3rd column
        chunk = text[:5000]  # You can adjust this chunk limit
        categories = bootstrap_categories(chunk, tool_name)
        for k, words in categories.items():
            save_keywords(tool_name, k, words)
        print(f"[DB] Saved new keywords. Reloading buckets...")
        buckets = load_keywords(tool_name)
        print(f"  actions: {len(buckets['actions'])}")
        print(f"  applications: {len(buckets['applications'])}")
        print(f"  objects: {len(buckets['objects'])}")
        print(f"  non_ito_objects: {len(buckets['non_ito_objects'])}")
        print(f"  non-ito_words: {len(buckets['non-ito_words'])}")

    # --- Always re-build engine ---
    engine = AhoEngine(tool_name, buckets)

    # --- Read file ---
    df = pd.read_excel(filepath) if filepath.endswith('.xlsx') else pd.read_csv(filepath)
    rows = df.iloc[:, 2].dropna().astype(str).tolist()

    for idx, ticket in enumerate(rows, start=1):
        cleaned_words = clean_text(ticket)
        matches = engine.match(" ".join(cleaned_words))

        print(f"\n[Row {idx}] Ticket: {ticket}")
        print(f"  [Local buckets] {matches}")

        if engine.is_complete(matches):
            print("  🔍 Verdict: ✅ Automatable (local)")
        else:
            print("  🔍 Verdict: ❌ Needs LLM boostering")

            # Fallback for single ticket if needed:
            categories = bootstrap_categories(ticket, tool_name)
            MAPPING = {
            "action": "actions",
            "application": "applications",
            "object": "objects",
            "non_ito_object": "non_ito_objects",
            "non-ito_words": "non_ito_words"
            }

            for k_raw, k_target in MAPPING.items():
                words = categories.get(k_raw, [])
                save_keywords(tool_name, k_target, words)


            # Reload for next rows
            buckets = load_keywords(tool_name)
            engine = AhoEngine(tool_name, buckets)

def process_custom_sentence():
    sample = input("\nYour text: ").strip()
    if not sample:
        print("⚠️ Empty input.")
        return

    # Use tool name "Manual" or prompt for it
    tool_name = "Manual"

    # Run LLM
    categories = bootstrap_categories(sample, tool_name)
    print("[LLM RAW]", categories)

    # Save to DB
    for category, words in categories.items():
        save_keywords(tool_name, category, words)

    # Rebuild engine with updated keywords
    engine = AhoEngine(tool_name)

    # Match
    cleaned = sample.lower()
    matches = engine.match(cleaned)

    print("\n[INFO] Matched buckets:")
    MAPPING = {
    "action": "actions",
    "application": "applications",
    "object": "objects",
    "non_ito_object": "non_ito_objects",
    "non-ito_words": "non_ito_words"
}

    for k_raw, k_target in MAPPING.items():
        words = categories.get(k_raw, [])
        save_keywords(tool_name, k_target, words)


    verdict = "✅ Automatable" if engine.is_automatable(matches) else "❌ Non-Automatable"
    print("\n🔍 Verdict:", verdict)


def main():
    root_directory = r"C:\Users\navak\Desktop\Hex 2025\Ticket Analyzer\Usecases"

    while True:
        file_paths = path_finder.get_file_paths_dict(root_directory)
        filenames = list(file_paths.keys())

        print("\n=== Menu ===")
        for idx, filename in enumerate(filenames, 1):
            print(f"{idx}. {filename}")
        print("A. Process ALL")
        print("M. Manual input")
        print("0. Exit")

        choice = input("\nChoice: ").strip().lower()

        if choice == "0":
            print("✅ Exiting program.")
            break

        elif choice == "a":
            for f in file_paths.values():
                print(f"\n📄 Processing: {f}")
                process_file(f)

        elif choice == "m":
            text = input("\nYour text: ")
            bootstrap_categories(text, "Manual")

        else:
            try:
                idx = int(choice)
                if 1 <= idx <= len(filenames):
                    selected_file = filenames[idx - 1]
                    print(f"\n📄 Processing: {selected_file}")
                    process_file(file_paths[selected_file])
                else:
                    print("⚠️ Invalid number. Please try again.")
            except ValueError:
                print("⚠️ Invalid input. Please enter a number, 'A', 'M', or '0'.")
if __name__ == "__main__":
    main()