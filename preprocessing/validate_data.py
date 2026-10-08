import pandas as pd
from pathlib import Path


# -----------------------------
# PATH
# -----------------------------

DATA_DIR = Path("data/processed")


# -----------------------------
# LOAD DATA
# -----------------------------

def load_data():

    restaurants = pd.read_csv(
        DATA_DIR / "restaurants_clean.csv"
    )

    customers = pd.read_csv(
        DATA_DIR / "customers_clean.csv"
    )

    foods = pd.read_csv(
        DATA_DIR / "foods_clean.csv"
    )

    orders = pd.read_csv(
        DATA_DIR / "orders_clean.csv"
    )

    order_items = pd.read_csv(
        DATA_DIR / "order_items_clean.csv"
    )

    reviews = pd.read_csv(
        DATA_DIR / "reviews_clean.csv"
    )

    return (
        restaurants,
        customers,
        foods,
        orders,
        order_items,
        reviews
    )


# -----------------------------
# BASIC VALIDATION
# -----------------------------

def check_missing_values(name, df):

    missing = df.isnull().sum().sum()

    if missing == 0:
        print(f"✅ {name}: No missing values")
    else:
        print(f"⚠️ {name}: {missing} missing values")


def check_duplicates(name, df):

    duplicates = df.duplicated().sum()

    if duplicates == 0:
        print(f"✅ {name}: No duplicate rows")
    else:
        print(f"⚠️ {name}: {duplicates} duplicate rows")


# -----------------------------
# FOREIGN KEY VALIDATION
# -----------------------------

def check_foreign_keys(
    orders,
    order_items,
    reviews,
    customers,
    restaurants,
    foods
):

    print("\nFOREIGN KEY VALIDATION")
    print("----------------------")

    # Orders → Customers

    invalid_customers = orders[
        ~orders["customer_id"].isin(
            customers["customer_id"]
        )
    ]

    if len(invalid_customers) == 0:
        print("✅ Orders → Customers")
    else:
        print(
            f"❌ Orders → Customers: "
            f"{len(invalid_customers)} invalid records"
        )

    # Orders → Restaurants

    invalid_restaurants = orders[
        ~orders["restaurant_id"].isin(
            restaurants["restaurant_id"]
        )
    ]

    if len(invalid_restaurants) == 0:
        print("✅ Orders → Restaurants")
    else:
        print(
            f"❌ Orders → Restaurants: "
            f"{len(invalid_restaurants)} invalid records"
        )

    # Order Items → Orders

    invalid_orders = order_items[
        ~order_items["order_id"].isin(
            orders["order_id"]
        )
    ]

    if len(invalid_orders) == 0:
        print("✅ Order Items → Orders")
    else:
        print(
            f"❌ Order Items → Orders: "
            f"{len(invalid_orders)} invalid records"
        )

    # Order Items → Foods

    invalid_foods = order_items[
        ~order_items["food_id"].isin(
            foods["food_id"]
        )
    ]

    if len(invalid_foods) == 0:
        print("✅ Order Items → Foods")
    else:
        print(
            f"❌ Order Items → Foods: "
            f"{len(invalid_foods)} invalid records"
        )

    # Reviews → Customers

    invalid_review_customers = reviews[
        ~reviews["customer_id"].isin(
            customers["customer_id"]
        )
    ]

    if len(invalid_review_customers) == 0:
        print("✅ Reviews → Customers")
    else:
        print(
            f"❌ Reviews → Customers: "
            f"{len(invalid_review_customers)} invalid records"
        )

    # Reviews → Restaurants

    invalid_review_restaurants = reviews[
        ~reviews["restaurant_id"].isin(
            restaurants["restaurant_id"]
        )
    ]

    if len(invalid_review_restaurants) == 0:
        print("✅ Reviews → Restaurants")
    else:
        print(
            f"❌ Reviews → Restaurants: "
            f"{len(invalid_review_restaurants)} invalid records"
        )


# -----------------------------
# BUSINESS RULE VALIDATION
# -----------------------------

def check_business_rules(
    restaurants,
    customers,
    foods,
    orders,
    order_items,
    reviews
):

    print("\nBUSINESS RULE VALIDATION")
    print("------------------------")

    # Restaurant ratings

    invalid = restaurants[
        (restaurants["rating"] < 0) |
        (restaurants["rating"] > 5)
    ]

    print(
        "✅ Restaurant ratings"
        if len(invalid) == 0
        else "❌ Invalid restaurant ratings"
    )

    # Food prices

    invalid = foods[
        foods["price"] <= 0
    ]

    print(
        "✅ Food prices"
        if len(invalid) == 0
        else "❌ Invalid food prices"
    )

    # Food ratings

    invalid = foods[
        (foods["rating"] < 0) |
        (foods["rating"] > 5)
    ]

    print(
        "✅ Food ratings"
        if len(invalid) == 0
        else "❌ Invalid food ratings"
    )

    # Customer ages

    invalid = customers[
        (customers["age"] < 18) |
        (customers["age"] > 100)
    ]

    print(
        "✅ Customer ages"
        if len(invalid) == 0
        else "❌ Invalid customer ages"
    )

    # Review ratings

    invalid = reviews[
        (reviews["rating"] < 1) |
        (reviews["rating"] > 5)
    ]

    print(
        "✅ Review ratings"
        if len(invalid) == 0
        else "❌ Invalid review ratings"
    )

    # Order item quantity

    invalid = order_items[
        order_items["quantity"] <= 0
    ]

    print(
        "✅ Order quantities"
        if len(invalid) == 0
        else "❌ Invalid order quantities"
    )


# -----------------------------
# MAIN
# -----------------------------

if __name__ == "__main__":

    print("Loading processed FOODIQ data...\n")

    (
        restaurants,
        customers,
        foods,
        orders,
        order_items,
        reviews
    ) = load_data()

    # Basic checks

    print("BASIC DATA VALIDATION")
    print("---------------------")

    datasets = {
        "Restaurants": restaurants,
        "Customers": customers,
        "Foods": foods,
        "Orders": orders,
        "Order Items": order_items,
        "Reviews": reviews
    }

    for name, df in datasets.items():

        check_missing_values(name, df)
        check_duplicates(name, df)

    # Foreign keys

    check_foreign_keys(
        orders,
        order_items,
        reviews,
        customers,
        restaurants,
        foods
    )

    # Business rules

    check_business_rules(
        restaurants,
        customers,
        foods,
        orders,
        order_items,
        reviews
    )

    print("\n==============================")
    print("DATA VALIDATION COMPLETED")
    print("==============================")