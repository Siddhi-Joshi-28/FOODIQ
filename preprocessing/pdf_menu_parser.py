from pathlib import Path
import re
import pandas as pd
from pypdf import PdfReader


# --------------------------------------------------
# Project paths
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[1]

PDF_PATH = (
    BASE_DIR
    / "data"
    / "raw"
    / "menus"
    / "sample_menu.pdf"
)
OUTPUT_PATH = BASE_DIR / "data" / "processed" / "menu_extracted.csv"


# --------------------------------------------------
# 1. Extract text from PDF
# --------------------------------------------------

def extract_text_from_pdf(pdf_path):

    reader = PdfReader(pdf_path)

    pages = []

    for page_number, page in enumerate(reader.pages, start=1):

        text = page.extract_text()

        if text:
            pages.append(text)

    return "\n".join(pages)


# --------------------------------------------------
# 2. Clean extracted text
# --------------------------------------------------

def clean_text(text):

    lines = text.splitlines()

    cleaned_lines = []

    for line in lines:

        line = line.strip()

        if not line:
            continue

        cleaned_lines.append(line)

    return cleaned_lines


# --------------------------------------------------
# 3. Check whether a line is a price
# --------------------------------------------------

def extract_price(line):

    pattern = r"(?:₹|Rs\.?|INR)?\s*(\d+(?:\.\d+)?)"

    match = re.search(pattern, line, re.IGNORECASE)

    if match:
        return float(match.group(1))

    return None


# --------------------------------------------------
# 4. Detect category
# --------------------------------------------------

def is_category(line):

    categories = [
        "pizza",
        "burgers",
        "burger",
        "biryani",
        "desserts",
        "drinks",
        "beverages",
        "starters",
        "main course",
        "salads",
        "pasta",
        "sandwiches"
    ]

    return line.lower() in categories


# --------------------------------------------------
# 5. Parse menu
# --------------------------------------------------

def parse_menu(lines):

    foods = []

    current_category = "Unknown"

    i = 0

    while i < len(lines):

        line = lines[i]

        # Skip title
        if "foodiq restaurant menu" in line.lower():
            i += 1
            continue

        # Detect category
        if is_category(line):

            current_category = line

            i += 1
            continue

        # Check whether next line is a price
        if i + 1 < len(lines):

            price = extract_price(lines[i + 1])

            if price is not None:

                food_name = line

                ingredients = ""

                # Check next line for ingredients
                if i + 2 < len(lines):

                    next_line = lines[i + 2]

                    if extract_price(next_line) is None:
                        ingredients = next_line

                foods.append(
                    {
                        "food_name": food_name,
                        "category": current_category,
                        "price": price,
                        "ingredients": ingredients
                    }
                )

                i += 3
                continue

        i += 1

    return foods


# --------------------------------------------------
# 6. Main
# --------------------------------------------------

if __name__ == "__main__":

    print("FOODIQ PDF Menu Parser")
    print("=" * 50)

    if not PDF_PATH.exists():

        print(f"PDF not found: {PDF_PATH}")

    else:

        raw_text = extract_text_from_pdf(PDF_PATH)

        lines = clean_text(raw_text)

        foods = parse_menu(lines)

        print("\nExtracted Food Data")
        print("-" * 50)

        for food in foods:

            print(f"Food       : {food['food_name']}")
            print(f"Category   : {food['category']}")
            print(f"Price      : ₹{food['price']}")
            print(f"Ingredients: {food['ingredients']}")
            print("-" * 50)

        print(f"\nTotal foods extracted: {len(foods)}")

        foods = parse_menu(lines)
        if foods:
           df = pd.DataFrame(foods)

           OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

           df.to_csv(OUTPUT_PATH, index=False)

           print(f"\nMenu data saved to:")
           print(OUTPUT_PATH)