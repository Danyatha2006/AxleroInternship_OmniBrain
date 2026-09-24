import pymupdf
import os


PDF_PATH = "data/sample.pdf"
OUTPUT_FOLDER = "data/extracted_images"


def extract_images_from_pdf(pdf_path, output_folder):
    """Extract all embedded images from a PDF."""

    os.makedirs(output_folder, exist_ok=True)

    document = pymupdf.open(pdf_path)

    extracted_images = []

    for page_number, page in enumerate(document, start=1):

        images = page.get_images(full=True)

        print(f"Page {page_number}: {len(images)} image(s) found")

        for image_index, image_info in enumerate(images, start=1):

            xref = image_info[0]

            image_data = document.extract_image(xref)

            image_bytes = image_data["image"]
            image_ext = image_data["ext"]

            image_filename = (
                f"page_{page_number}_image_{image_index}.{image_ext}"
            )

            image_path = os.path.join(
                output_folder,
                image_filename
            )

            with open(image_path, "wb") as image_file:
                image_file.write(image_bytes)

            extracted_images.append({
                "page": page_number,
                "image_id": image_index,
                "path": image_path,
                "format": image_ext
            })

            print(f"  Extracted: {image_filename}")

    document.close()

    return extracted_images


if __name__ == "__main__":

    images = extract_images_from_pdf(
        PDF_PATH,
        OUTPUT_FOLDER
    )

    print("\n" + "=" * 60)
    print("IMAGE EXTRACTION COMPLETE")
    print("=" * 60)

    print("Total images extracted:", len(images))

    for image in images:
        print(image)