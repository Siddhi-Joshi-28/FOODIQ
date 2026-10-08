import pandas as pd
from pathlib import Path


# -----------------------------
# PATHS
# -----------------------------

RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


# -----------------------------
# LOAD DATA
# -----------------------------

def load_data():

    restaurants = pd.read_csv(RAW_DIR / "restaurants.csv")
    customers = pd.read_csv(RAW_DIR / "customers.csv")
    foods = pd.read_csv(RAW_DIR / "foods.csv")
    orders = pd.read_csv(RAW_DIR / "orders.csv")
    order_items = pd.read_csv(RAW_DIR / "order_items.csv")
    reviews = pd.read_csv(RAW_DIR / "reviews.csv")

    return (
        restaurants,
        customers,
        foods,
        orders,
        order_items,
        reviews
    )


# -----------------------------
# CLEAN RESTAURANTS
# -----------------------------

def clean_restaurants(df):

    # Remove duplicate records
    df = df.drop_duplicates()

    # Make sure rating is numeric
    df["rating"] = pd.to_numeric(
        df["rating"],
        errors="coerce"
    )

    # Keep ratings between 0 and 5
    df["rating"] = df["rating"].clip(0, 5)

    # Make sure delivery time is numeric
    df["delivery_time_minutes"] = pd.to_numeric(
        df["delivery_time_minutes"],
        errors="coerce"
    )

    # Fill missing delivery time with median
    df["delivery_time_minutes"] = df[
        "delivery_time_minutes"
    ].fillna(
        df["delivery_time_minutes"].median()
    )

    return df


# -----------------------------
# CLEAN CUSTOMERS
# -----------------------------

def clean_customers(df):

    df = df.drop_duplicates()

    # Convert age to numeric
    df["age"] = pd.to_numeric(
        df["age"],
        errors="coerce"
    )

    # Keep realistic age range
    df["age"] = df["age"].clip(18, 100)

    return df


# -----------------------------
# CLEAN FOODS
# -----------------------------

def clean_foods(df):

    df = df.drop_duplicates()

    # Convert price to numeric
    df["price"] = pd.to_numeric(
        df["price"],
        errors="coerce"
    )

    # Invalid prices become NaN
    df.loc[df["price"] <= 0, "price"] = None

    # Fill missing prices with median
    df["price"] = df["price"].fillna(
        df["price"].median()
    )

    # Rating
    df["rating"] = pd.to_numeric(
        df["rating"],
        errors="coerce"
    )

    df["rating"] = df["rating"].clip(0, 5)

    return df


# -----------------------------
# CLEAN ORDERS
# -----------------------------

def clean_orders(df):

    df = df.drop_duplicates()

    # Convert date
    df["order_date"] = pd.to_datetime(
        df["order_date"],
        errors="coerce"
    )

    # Remove rows without valid date
    df = df.dropna(
        subset=["order_date"]
    )

    return df


# -----------------------------
# CLEAN ORDER ITEMS
# -----------------------------

def clean_order_items(df):

    df = df.drop_duplicates()

    df["quantity"] = pd.to_numeric(
        df["quantity"],
        errors="coerce"
    )

    df["price"] = pd.to_numeric(
        df["price"],
        errors="coerce"
    )

    df["total_price"] = pd.to_numeric(
        df["total_price"],
        errors="coerce"
    )

    # Quantity must be at least 1
    df = df[df["quantity"] > 0]

    # Price must be positive
    df = df[df["price"] > 0]

    # Recalculate total price
    df["total_price"] = (
        df["quantity"] * df["price"]
    )

    return df


# -----------------------------
# CLEAN REVIEWS
# -----------------------------

def clean_reviews(df):

    df = df.drop_duplicates()

    # Rating must be numeric
    df["rating"] = pd.to_numeric(
        df["rating"],
        errors="coerce"
    )

    # Keep rating between 1 and 5
    df["rating"] = df["rating"].clip(1, 5)

    # Convert review date
    df["review_date"] = pd.to_datetime(
        df["review_date"],
        errors="coerce"
    )

    # Remove reviews without text
    df["review_text"] = df[
        "review_text"
    ].fillna("")

    return df


# -----------------------------
# SAVE DATA
# -----------------------------

def save_data(
    restaurants,
    customers,
    foods,
    orders,
    order_items,
    reviews
):

    restaurants.to_csv(
        PROCESSED_DIR / "restaurants_clean.csv",
        index=False
    )

    customers.to_csv(
        PROCESSED_DIR / "customers_clean.csv",
        index=False
    )

    foods.to_csv(
        PROCESSED_DIR / "foods_clean.csv",
        index=False
    )

    orders.to_csv(
        PROCESSED_DIR / "orders_clean.csv",
        index=False
    )

    order_items.to_csv(
        PROCESSED_DIR / "order_items_clean.csv",
        index=False
    )

    reviews.to_csv(
        PROCESSED_DIR / "reviews_clean.csv",
        index=False
    )


# -----------------------------
# MAIN
# -----------------------------

if __name__ == "__main__":

    print("Loading raw FOODIQ data...\n")

    (
        restaurants,
        customers,
        foods,
        orders,
        order_items,
        reviews
    ) = load_data()

    print("Cleaning data...")

    restaurants = clean_restaurants(restaurants)
    customers = clean_customers(customers)
    foods = clean_foods(foods)
    orders = clean_orders(orders)
    order_items = clean_order_items(order_items)
    reviews = clean_reviews(reviews)

    save_data(
        restaurants,
        customers,
        foods,
        orders,
        order_items,
        reviews
    )

    print("\nDATA CLEANING COMPLETED!")
    print("------------------------")

    print(f"Restaurants : {len(restaurants)}")
    print(f"Customers   : {len(customers)}")
    print(f"Foods       : {len(foods)}")
    print(f"Orders      : {len(orders)}")
    print(f"Order Items : {len(order_items)}")
    print(f"Reviews     : {len(reviews)}")

    print("\nClean data saved in:")
    print("data/processed/")
