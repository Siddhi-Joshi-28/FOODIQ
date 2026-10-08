import re
from pathlib import Path

import psycopg2
from dotenv import load_dotenv
import os


BASE_DIR = Path(__file__).resolve().parents[1]

load_dotenv(BASE_DIR / ".env")


DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432"),
    "database": "foodiq_main",
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD"),
}


def parse_query(query):
    """
    Extract useful patterns from the user's search query.
    """

    query_lower = query.lower().strip()

    result = {
        "food": None,
        "max_price": None,
        "min_price": None,
        "vegetarian": False
    }

    # Detect price: under / below / less than
    price_match = re.search(
        r"(?:under|below|less than)\s*₹?\s*(\d+(?:\.\d+)?)",
        query_lower
    )

    if price_match:
        result["max_price"] = float(price_match.group(1))

    # Detect price: above / over / greater than
    min_price_match = re.search(
        r"(?:above|over|greater than)\s*₹?\s*(\d+(?:\.\d+)?)",
        query_lower
    )

    if min_price_match:
        result["min_price"] = float(min_price_match.group(1))

    # Detect vegetarian
    if re.search(r"\b(veg|vegetarian)\b", query_lower):
        result["vegetarian"] = True

    # Remove known keywords to find food term
    food_query = re.sub(
        r"\b(veg|vegetarian|under|below|less than|above|over|greater than)\b",
        "",
        query_lower
    )

    food_query = re.sub(r"₹?\s*\d+(?:\.\d+)?", "", food_query)

    food_query = food_query.strip()

    if food_query:
        result["food"] = food_query

    return result


def search_food(query):
    """
    Search PostgreSQL using conditions extracted with Regex.
    """

    filters = parse_query(query)

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

    # Food name/category search
    if filters["food"]:
        sql += """
            AND (
                LOWER(food_name) LIKE LOWER(%s)
                OR LOWER(category) LIKE LOWER(%s)
            )
        """

        search_pattern = f"%{filters['food']}%"

        parameters.extend([
            search_pattern,
            search_pattern
        ])

    # Maximum price
    if filters["max_price"] is not None:
        sql += " AND price <= %s"
        parameters.append(filters["max_price"])

    # Minimum price
    if filters["min_price"] is not None:
        sql += " AND price >= %s"
        parameters.append(filters["min_price"])

    # Vegetarian
    if filters["vegetarian"]:
        sql += " AND is_vegetarian = TRUE"

    sql += " ORDER BY food_name"

    cursor.execute(sql, parameters)

    results = cursor.fetchall()

    cursor.close()
    connection.close()

    return filters, results


if __name__ == "__main__":

    print("FOODIQ Regex Search")
    print("=" * 50)

    query = input("Enter your search: ")

    try:

        filters, results = search_food(query)

        print("\nDetected Query")
        print("-" * 50)

        print(f"Food          : {filters['food']}")
        print(f"Maximum Price : {filters['max_price']}")
        print(f"Minimum Price : {filters['min_price']}")
        print(f"Vegetarian    : {filters['vegetarian']}")

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

        print("\nDatabase error:")
        print(e)