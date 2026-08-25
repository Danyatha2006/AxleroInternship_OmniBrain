from src.pdf_loader import load_pdf
import json

pdf_path = "data/input/finance.pdf"

output_path = "data/output/finance.txt"
json_output_path = "data/output/extracted_content.json"
visual_output_path = "data/output/visual_pages.json"

pages = load_pdf(pdf_path)

# Save extracted text
with open(output_path, "w", encoding="utf-8") as file:
    for page in pages:
        file.write(f"\n--- Page {page['page_number']} ---\n")
        file.write(page["text"])
        file.write("\n")

# Save structured extracted content for Member 2
with open(json_output_path, "w", encoding="utf-8") as file:
    json.dump(pages, file, indent=4, ensure_ascii=False)

# Save possible visual pages for Member 3
visual_pages = []

for page in pages:
    if page["is_low_text"]:
        visual_pages.append({
            "page_number": page["page_number"],
            "reason": "Very little extracted text",
            "character_count": page["character_count"]
        })

with open(visual_output_path, "w", encoding="utf-8") as file:
    json.dump(visual_pages, file, indent=4)

print("Number of pages:", len(pages))
print("Extracted content saved to:", json_output_path)
print("Potential visual pages saved to:", visual_output_path)

# Your old testing section
for page in pages:
    if page["page_number"] in [279, 389, 390, 391, 394, 395, 396]:
        print(f"\n--- Page {page['page_number']} ---")
        print(page["text"])