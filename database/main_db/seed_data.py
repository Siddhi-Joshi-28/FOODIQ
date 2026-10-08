import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from urllib.parse import quote_plus


# --------------------------------------------------
# 1. Load environment variables
# --------------------------------------------------

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")


# --------------------------------------------------
# 2. Create PostgreSQL connection
# --------------------------------------------------

encoded_password = quote_plus(DB_PASSWORD)

DATABASE_URL = (
    f"postgresql+psycopg2://"
    f"{DB_USER}:{encoded_password}@"
    f"{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

engine = create_engine(DATABASE_URL)


# --------------------------------------------------
# 3. Project paths
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[2]

DATA_DIR = BASE_DIR / "data" / "processed"


# --------------------------------------------------
# 4. CSV files
# --------------------------------------------------

files = {
    "customers": DATA_DIR / "customers_clean.csv",
    "restaurants": DATA_DIR / "restaurants_clean.csv",
    "foods": DATA_DIR / "foods_clean.csv",
    "orders": DATA_DIR / "orders_clean.csv",
    "order_items": DATA_DIR / "order_items_clean.csv",
    "reviews": DATA_DIR / "reviews_clean.csv",
}


# --------------------------------------------------
# 5. Clear existing synthetic data
# --------------------------------------------------

def clear_database():

    print("Clearing existing data...")

    query = text("""
        TRUNCATE TABLE
            order_items,
            orders,
            reviews,
            ratings,
            demand_history,
            revenue_history,
            foods,
            restaurants,
            customers
        RESTART IDENTITY CASCADE;
    """)

    with engine.begin() as connection:
        connection.execute(query)

    print("Existing data cleared.")


# --------------------------------------------------
# 6. Load CSV into PostgreSQL
# --------------------------------------------------

def load_data():

    for table_name, file_path in files.items():

        print(f"Loading {table_name}...")

        df = pd.read_csv(file_path)

        df.to_sql(
            table_name,
            engine,
            if_exists="append",
            index=False
        )

        print(f"{len(df)} records inserted into {table_name}.")


# --------------------------------------------------
# 7. Verify database
# --------------------------------------------------

def verify_data():

    print("\nDatabase record counts:")
    print("-" * 40)

    tables = [
        "customers",
        "restaurants",
        "foods",
        "orders",
        "order_items",
        "reviews",
        "ratings",
        "demand_history",
        "revenue_history",
    ]

    with engine.connect() as connection:

        for table in tables:

            result = connection.execute(
                text(f"SELECT COUNT(*) FROM {table}")
            )

            count = result.scalar()

            print(f"{table:20} : {count}")


# --------------------------------------------------
# 8. Main
# --------------------------------------------------

if __name__ == "__main__":

    print("FOODIQ Main Database Seeder")
    print("=" * 40)

    clear_database()

    load_data()

    verify_data()

    print("\nData loading completed successfully.")