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


def search_food(query):
    """Search foods from PostgreSQL using SQL."""

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
        WHERE
            LOWER(food_name) LIKE LOWER(%s)
            OR LOWER(category) LIKE LOWER(%s)
        ORDER BY food_name;
    """

    search_pattern = f"%{query.strip()}%"

    cursor.execute(
        sql,
        (search_pattern, search_pattern)
    )

    results = cursor.fetchall()

    cursor.close()
    connection.close()

    return results


if __name__ == "__main__":

    print("FOODIQ PostgreSQL SQL Search")
    print("=" * 50)

    query = input("Enter food to search: ")

    try:

        results = search_food(query)

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