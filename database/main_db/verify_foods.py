import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, text


# Load environment variables
load_dotenv()

# Create database connection
engine = create_engine(
    "postgresql+psycopg2://"
    f"{os.getenv('DB_USER')}:"
    f"{os.getenv('DB_PASSWORD')}@"
    f"{os.getenv('DB_HOST')}:"
    f"{os.getenv('DB_PORT')}/"
    f"{os.getenv('DB_NAME')}"
)


# Query foods
with engine.connect() as connection:

    result = connection.execute(
        text("""
            SELECT
                food_id,
                food_name,
                category,
                is_vegetarian
            FROM foods
            ORDER BY food_id
        """)
    )

    print("\nFOOD DATA FROM POSTGRESQL")
    print("=" * 70)

    for row in result:
        print(
            f"{row.food_id:2} | "
            f"{row.food_name:25} | "
            f"{row.category:15} | "
            f"Vegetarian: {row.is_vegetarian}"
        )

    print("=" * 70)