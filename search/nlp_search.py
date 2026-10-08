import os
import re
from pathlib import Path

import nltk
import psycopg2
from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parents[1]

load_dotenv(BASE_DIR / ".env")


DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432"),
    "database": "foodiq_main",
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD"),
}


# Download tokenizer data if required
try:
    nltk.data.find("tokenizers/punkt_tab")
except LookupError:
    nltk.download("punkt_tab")


def tokenize_query(query):
    """Convert the user's natural-language query into tokens."""

    tokens = nltk.word_tokenize(query.lower())

    return tokens


def extract_conditions(query):
    """
    Extract useful information from a natural-language query.
    """

    tokens = tokenize_query(query)

    result = {
        "food": None,
        "max_price": None,
        "min_price": None,
        "vegetarian": False,
        "tokens": tokens,
    }

    # Vegetarian detection
    if "veg" in tokens or "vegetarian" in tokens:
        result["vegetarian"] = True

    # Price detection
    query_lower = query.lower()

    max_price_match = re.search(
        r"(?:under|below|less than)\s*₹?\s*(\d+(?:\.\d+)?)",
        query_lower
    )

    if max_price_match:
        result["max_price"] = float(max_price_match.group(1))

    min_price_match = re.search(
        r"(?:above|over|greater than)\s*₹?\s*(\d+(?:\.\d+)?)",
        query_lower
    )

    if min_price_match:
        result["min_price"] = float(min_price_match.group(1))

    # Words that are not food names
    stop_words = {
        "show",
        "me",
        "some",
        "find",
        "give",
        "i",
        "want",
        "a",
        "an",
        "the",
        "that",
        "is",
        "are",
        "which",
        "food",
        "foods",
        "with",
        "under",
        "below",
        "less",
        "than",
        "above",
        "over",
        "greater",
        "cheap",
        "cheaper",
        "expensive",
        "costs",
        "cost",
        "please",
        "for",
        "my",
    }

    food_words = []

    for token in tokens:

        if token.isalpha() and token not in stop_words:
            if token not in {"veg", "vegetarian"}:
                food_words.append(token)

    if food_words:
        result["food"] = " ".join(food_words)

    return result


def search_food(query):

    conditions = extract_conditions(query)

    connection = psycopg2.connect(**DB_CONFIG)
    cursor = connection.cursor()

    sql = """
        SELECT
            food_id,
            food_name,
            category,
            price,
            rating,
            is_vegetarian
        FROM foods
        WHERE 1 = 1
    """

    parameters = []

    # Food search
    if conditions["food"]:

        sql += """
            AND (
                LOWER(food_name) LIKE LOWER(%s)
                OR LOWER(category) LIKE LOWER(%s)
            )
        """

        search_pattern = f"%{conditions['food']}%"

        parameters.extend([
            search_pattern,
            search_pattern
        ])

    # Maximum price
    if conditions["max_price"] is not None:

        sql += " AND price <= %s"

        parameters.append(
            conditions["max_price"]
        )

    # Minimum price
    if conditions["min_price"] is not None:

        sql += " AND price >= %s"

        parameters.append(
            conditions["min_price"]
        )

    # Vegetarian
    if conditions["vegetarian"]:

        sql += " AND is_vegetarian = TRUE"

    sql += " ORDER BY food_name"

    cursor.execute(
        sql,
        parameters
    )

    results = cursor.fetchall()

    cursor.close()
    connection.close()

    return conditions, results


if __name__ == "__main__":

    print("FOODIQ NLP Search")
    print("=" * 50)

    query = input("Enter your search: ")

    try:

        conditions, results = search_food(query)

        print("\nNLP Analysis")
        print("-" * 50)

        print(f"Tokens       : {conditions['tokens']}")
        print(f"Food         : {conditions['food']}")
        print(f"Max Price    : {conditions['max_price']}")
        print(f"Min Price    : {conditions['min_price']}")
        print(f"Vegetarian   : {conditions['vegetarian']}")

        print("\nSearch Results")
        print("-" * 50)

        if not results:

            print("No food found.")

        else:

            for food in results:

                (
                    food_id,
                    food_name,
                    category,
                    price,
                    rating,
                    is_vegetarian
                ) = food

                print(f"ID          : {food_id}")
                print(f"Food        : {food_name}")
                print(f"Category    : {category}")
                print(f"Price       : ₹{price}")
                print(f"Rating      : {rating}")
                print(f"Vegetarian  : {is_vegetarian}")
                print("-" * 50)

            print(f"Total results: {len(results)}")

    except Exception as e:

        print("\nError:")
        print(e)