import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DATASET_FILE = BASE_DIR / "dataset" / "evaluation_questions.json"


def load_questions():
    with open(DATASET_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def main():
    questions = load_questions()

    print("=" * 60)
    print("OmniBrain Evaluation Dataset")
    print("=" * 60)
    print(f"Total evaluation questions: {len(questions)}")
    print()

    for item in questions:
        print(
            f"{item['id']} | "
            f"{item['category']} | "
            f"{item['question']}"
        )

    print()
    print("Evaluation dataset loaded successfully.")


if __name__ == "__main__":
    main()