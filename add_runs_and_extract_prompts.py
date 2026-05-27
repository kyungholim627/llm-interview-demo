import json
from collections import defaultdict
from pathlib import Path


INPUT_FILE = Path("precomputed_medical_demo_answers.json")
RUN_OUTPUT_FILE = Path("precomputed_medical_demo_answers_with_runs.json")
PROMPT_OUTPUT_FILE = Path("precomputed_medical_demo_prompts_only.json")


def main():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    group_counts = defaultdict(int)
    labeled_rows = []

    for idx, item in enumerate(data, start=1):
        model = str(item.get("model", "")).strip()
        prompt = str(item.get("prompt", ""))

        group_key = (model, prompt)
        group_counts[group_key] += 1

        new_item = dict(item)
        new_item.setdefault("id", f"item_{idx:04d}")
        new_item["model"] = model
        new_item["run"] = group_counts[group_key]

        labeled_rows.append(new_item)

    with open(RUN_OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(labeled_rows, f, ensure_ascii=False, indent=2)

    prompt_groups = defaultdict(list)
    for item in labeled_rows:
        prompt_groups[(item.get("model", ""), item.get("prompt", ""))].append(item["run"])

    prompt_only_rows = []
    for prompt_idx, ((model, prompt), runs) in enumerate(prompt_groups.items(), start=1):
        prompt_only_rows.append({
            "prompt_id": f"prompt_{prompt_idx:04d}",
            "model": model,
            "prompt": prompt,
            "available_runs": sorted(runs),
            "n_runs": len(runs)
        })

    with open(PROMPT_OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(prompt_only_rows, f, ensure_ascii=False, indent=2)

    print(f"Saved: {RUN_OUTPUT_FILE}")
    print(f"Saved: {PROMPT_OUTPUT_FILE}")


if __name__ == "__main__":
    main()
