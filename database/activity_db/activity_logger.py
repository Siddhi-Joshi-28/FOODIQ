import os
from urllib.parse import quote_plus

from dotenv import load_dotenv
from sqlalchemy import create_engine, text


# --------------------------------------------------
# Load environment variables
# --------------------------------------------------

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

# Activity database is different from main database
DB_NAME = "foodiq_activity"

encoded_password = quote_plus(DB_PASSWORD)

DATABASE_URL = (
    f"postgresql+psycopg2://"
    f"{DB_USER}:{encoded_password}@"
    f"{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

engine = create_engine(DATABASE_URL)


# --------------------------------------------------
# 1. Log a search
# --------------------------------------------------

def log_search(
    customer_id,
    search_query,
    search_type="general"
):
    query = text("""
        INSERT INTO search_logs
        (
            customer_id,
            search_query,
            search_type
        )
        VALUES
        (
            :customer_id,
            :search_query,
            :search_type
        )
    """)

    with engine.begin() as connection:
        connection.execute(
            query,
            {
                "customer_id": customer_id,
                "search_query": search_query,
                "search_type": search_type
            }
        )


# --------------------------------------------------
# 2. Log a food / restaurant view
# --------------------------------------------------

def log_view(
    customer_id,
    restaurant_id=None,
    food_id=None
):
    query = text("""
        INSERT INTO view_logs
        (
            customer_id,
            restaurant_id,
            food_id
        )
        VALUES
        (
            :customer_id,
            :restaurant_id,
            :food_id
        )
    """)

    with engine.begin() as connection:
        connection.execute(
            query,
            {
                "customer_id": customer_id,
                "restaurant_id": restaurant_id,
                "food_id": food_id
            }
        )


# --------------------------------------------------
# 3. Log a click
# --------------------------------------------------

def log_click(
    customer_id,
    click_type,
    restaurant_id=None,
    food_id=None
):
    query = text("""
        INSERT INTO click_logs
        (
            customer_id,
            restaurant_id,
            food_id,
            click_type
        )
        VALUES
        (
            :customer_id,
            :restaurant_id,
            :food_id,
            :click_type
        )
    """)

    with engine.begin() as connection:
        connection.execute(
            query,
            {
                "customer_id": customer_id,
                "restaurant_id": restaurant_id,
                "food_id": food_id,
                "click_type": click_type
            }
        )


# --------------------------------------------------
# 4. Log recommendation interaction
# --------------------------------------------------

def log_recommendation(
    customer_id,
    recommendation_type,
    action,
    food_id=None,
    restaurant_id=None
):
    query = text("""
        INSERT INTO recommendation_logs
        (
            customer_id,
            food_id,
            restaurant_id,
            recommendation_type,
            action
        )
        VALUES
        (
            :customer_id,
            :food_id,
            :restaurant_id,
            :recommendation_type,
            :action
        )
    """)

    with engine.begin() as connection:
        connection.execute(
            query,
            {
                "customer_id": customer_id,
                "food_id": food_id,
                "restaurant_id": restaurant_id,
                "recommendation_type": recommendation_type,
                "action": action
            }
        )


# --------------------------------------------------
# Test
# --------------------------------------------------

if __name__ == "__main__":

    print("FOODIQ Activity Logger")
    print("=" * 40)

    log_search(
        customer_id=1,
        search_query="pizza",
        search_type="food"
    )

    log_view(
        customer_id=1,
        restaurant_id=2,
        food_id=5
    )

    log_click(
        customer_id=1,
        click_type="food",
        restaurant_id=2,
        food_id=5
    )

    log_recommendation(
        customer_id=1,
        food_id=5,
        recommendation_type="content_based",
        action="view"
    )

    print("Test activity logs inserted successfully.")