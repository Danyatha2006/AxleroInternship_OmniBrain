from src.pdf_loader import load_pdf

pdf_path = "data/input/finance.pdf"
output_path = "data/output/finance.txt"

pages = load_pdf(pdf_path)

with open(output_path, "w", encoding="utf-8") as file:
    for page in pages:
        file.write(f"\n--- Page {page['page_number']} ---\n")
        file.write(page["text"])
        file.write("\n")

print("Number of pages:", len(pages))

for page in pages:
    if page["page_number"] in [279, 389, 390, 391, 394, 395, 396]:
        print(f"\n--- Page {page['page_number']} ---")
        print(page["text"])