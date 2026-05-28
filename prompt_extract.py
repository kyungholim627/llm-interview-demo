import json
from pathlib import Path


INPUT_FILE = Path("precomputed_medical_demo_answers_with_runs.json")
OUTPUT_FILE = Path("precomputed_medical_demo_prompts_only.json")


def load_json(path: Path):
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {path}")

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def extract_unique_prompts(data):
    seen = set()
    prompts = []

    for item in data:
        prompt = item.get("prompt", "")

        if not isinstance(prompt, str):
            continue

        prompt = prompt.strip()

        if not prompt:
            continue

        if prompt in seen:
            continue

        seen.add(prompt)
        prompts.append(prompt)

    return prompts


def save_json(data, path: Path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def main():
    data = load_json(INPUT_FILE)

    prompts = extract_unique_prompts(data)

    output = [
        {
            "prompt": prompt
        }
        for prompt in prompts
    ]

    save_json(output, OUTPUT_FILE)

    print(f"Extracted {len(output)} unique prompts.")
    print(f"Saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()