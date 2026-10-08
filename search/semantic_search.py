import os
import re
from pathlib import Path

import psycopg2
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


BASE_DIR = Path(__file__).resolve().parents[1]

load_dotenv(BASE_DIR / ".env")


DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432"),
    "database": "foodiq_main",
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD"),
}


MODEL_NAME = "all-MiniLM-L6-v2"


# --------------------------------------------------
# LOAD FOODS
# --------------------------------------------------

def load_foods():
    """Load food data from PostgreSQL."""

    connection = psycopg2.connect(**DB_CONFIG)

    cursor = connection.cursor()

    query = """
        SELECT
            food_id,
            food_name,
            category,
            price,
            rating,
            is_vegetarian
        FROM foods
        ORDER BY food_id;
    """

    cursor.execute(query)

    foods = cursor.fetchall()

    cursor.close()
    connection.close()

    return foods


# --------------------------------------------------
# EXTRACT SEARCH CONDITIONS
# --------------------------------------------------

def extract_conditions(query):
    """
    Extract hard constraints from the user's query.

    Examples:

    vegetarian pizza
    vegetarian biryani under 300
    chicken biryani
    pizza below 400
    """

    query_lower = query.lower()

    conditions = {
        "vegetarian": None,
        "non_vegetarian": None,
        "category": None,
        "food_name": None,
        "max_price": None,
        "min_price": None,
    }

    # ----------------------------------------------
    # VEGETARIAN
    # ----------------------------------------------

    vegetarian_words = [
        "vegetarian",
        "veg",
        "veggie",
    ]

    non_vegetarian_words = [
        "non vegetarian",
        "non-vegetarian",
        "nonveg",
        "non veg",
        "non-veg",
        "chicken",
        "mutton",
        "fish",
        "egg",
    ]

    if any(word in query_lower for word in non_vegetarian_words):
        conditions["non_vegetarian"] = True

    elif any(word in query_lower for word in vegetarian_words):
        conditions["vegetarian"] = True


    # ----------------------------------------------
    # PRICE
    # ----------------------------------------------

    max_price_match = re.search(
        r"(?:under|below|less than|upto|up to)\s*(?:₹|rs\.?|inr)?\s*(\d+)",
        query_lower
    )

    if max_price_match:
        conditions["max_price"] = float(
            max_price_match.group(1)
        )


    min_price_match = re.search(
        r"(?:above|over|greater than|more than)\s*(?:₹|rs\.?|inr)?\s*(\d+)",
        query_lower
    )

    if min_price_match:
        conditions["min_price"] = float(
            min_price_match.group(1)
        )


    # ----------------------------------------------
    # FOOD/CATEGORY KEYWORDS
    # ----------------------------------------------

    food_keywords = {
        "pizza": "Pizza",
        "burger": "Burger",
        "biryani": "Biryani",
        "pasta": "Pasta",
        "noodles": "Chinese",
        "manchurian": "Chinese",
        "dosa": "South Indian",
        "sandwich": "Sandwich",
        "dessert": "Dessert",
        "brownie": "Dessert",
        "gulab jamun": "Dessert",
        "fries": "Fast Food",
        "wrap": "Healthy",
        "thali": "Gujarati",
        "paneer": "Indian",
    }

    for keyword, category in food_keywords.items():

        if keyword in query_lower:

            conditions["category"] = category

            # If the query contains a specific food name,
            # preserve it for semantic ranking.
            if keyword in [
                "pizza",
                "burger",
                "biryani",
                "pasta",
                "manchurian",
                "dosa",
                "sandwich",
                "brownie",
                "gulab jamun",
                "fries",
                "wrap",
                "thali",
            ]:
                conditions["food_name"] = keyword

            break


    return conditions


# --------------------------------------------------
# HARD FILTERING
# --------------------------------------------------

def filter_foods(foods, conditions):
    """
    Apply hard constraints before semantic ranking.

    Semantic similarity is NOT allowed to violate
    these constraints.
    """

    filtered_foods = []

    for food in foods:

        (
            food_id,
            food_name,
            category,
            price,
            rating,
            is_vegetarian
        ) = food


        # ------------------------------------------
        # VEGETARIAN FILTER
        # ------------------------------------------

        if conditions["vegetarian"] is True:

            if not is_vegetarian:
                continue


        # ------------------------------------------
        # NON-VEGETARIAN FILTER
        # ------------------------------------------

        if conditions["non_vegetarian"] is True:

            if is_vegetarian:
                continue


        # ------------------------------------------
        # CATEGORY FILTER
        # ------------------------------------------

        if conditions["category"] is not None:

            if category.lower() != conditions["category"].lower():
                continue


        # ------------------------------------------
        # MAX PRICE
        # ------------------------------------------

        if conditions["max_price"] is not None:

            if float(price) > conditions["max_price"]:
                continue


        # ------------------------------------------
        # MIN PRICE
        # ------------------------------------------

        if conditions["min_price"] is not None:

            if float(price) < conditions["min_price"]:
                continue


        filtered_foods.append(food)


    return filtered_foods


# --------------------------------------------------
# CREATE FOOD TEXT
# --------------------------------------------------

def create_food_text(food):

    (
        food_id,
        food_name,
        category,
        price,
        rating,
        is_vegetarian
    ) = food

    vegetarian_text = (
        "vegetarian"
        if is_vegetarian
        else "non vegetarian"
    )

    return (
        f"{food_name}. "
        f"Category: {category}. "
        f"Price: {price}. "
        f"Rating: {rating}. "
        f"{vegetarian_text}."
    )


# --------------------------------------------------
# SEMANTIC SEARCH
# --------------------------------------------------

def semantic_search(query, foods, model, top_k=5):

    # ----------------------------------------------
    # EXTRACT CONDITIONS
    # ----------------------------------------------

    conditions = extract_conditions(query)


    # ----------------------------------------------
    # HARD FILTER
    # ----------------------------------------------

    filtered_foods = filter_foods(
        foods,
        conditions
    )


    # ----------------------------------------------
    # NO RESULTS
    # ----------------------------------------------

    if not filtered_foods:
        return [], conditions


    # ----------------------------------------------
    # CREATE FOOD TEXT
    # ----------------------------------------------

    food_texts = [
        create_food_text(food)
        for food in filtered_foods
    ]


    # ----------------------------------------------
    # FOOD EMBEDDINGS
    # ----------------------------------------------

    food_embeddings = model.encode(
        food_texts,
        convert_to_numpy=True
    )


    # ----------------------------------------------
    # QUERY EMBEDDING
    # ----------------------------------------------

    query_embedding = model.encode(
        [query],
        convert_to_numpy=True
    )


    # ----------------------------------------------
    # COSINE SIMILARITY
    # ----------------------------------------------

    similarities = cosine_similarity(
        query_embedding,
        food_embeddings
    )[0]


    # ----------------------------------------------
    # RANK RESULTS
    # ----------------------------------------------

    ranked_indices = similarities.argsort()[::-1]


    results = []

    for index in ranked_indices[:top_k]:

        food = filtered_foods[index]

        results.append({
            "food": food,
            "similarity": float(
                similarities[index]
            )
        })


    return results, conditions


# --------------------------------------------------
# MAIN PROGRAM
# --------------------------------------------------

if __name__ == "__main__":

    print("FOODIQ Semantic Search")
    print("=" * 50)

    print("\nLoading Sentence Transformer model...")

    model = SentenceTransformer(MODEL_NAME)

    print("Model loaded successfully.")

    foods = load_foods()

    print(
        f"Foods loaded from PostgreSQL: "
        f"{len(foods)}"
    )


    query = input(
        "\nEnter your search: "
    )


    results, conditions = semantic_search(
        query,
        foods,
        model,
        top_k=5
    )


    # ----------------------------------------------
    # SHOW DETECTED CONDITIONS
    # ----------------------------------------------

    print("\nDetected Search Conditions")
    print("-" * 50)

    print(
        f"Vegetarian     : "
        f"{conditions['vegetarian']}"
    )

    print(
        f"Non-Vegetarian : "
        f"{conditions['non_vegetarian']}"
    )

    print(
        f"Category       : "
        f"{conditions['category']}"
    )

    print(
        f"Max Price      : "
        f"{conditions['max_price']}"
    )

    print(
        f"Min Price      : "
        f"{conditions['min_price']}"
    )


    # ----------------------------------------------
    # SHOW RESULTS
    # ----------------------------------------------

    print("\nSemantic Search Results")
    print("-" * 50)


    if not results:

        print(
            "No foods matched the requested conditions."
        )

    else:

        for rank, result in enumerate(
            results,
            start=1
        ):

            (
                food_id,
                food_name,
                category,
                price,
                rating,
                is_vegetarian
            ) = result["food"]

            similarity = result["similarity"]


            print(
                f"Rank        : {rank}"
            )

            print(
                f"Food        : {food_name}"
            )

            print(
                f"Category    : {category}"
            )

            print(
                f"Price       : ₹{price}"
            )

            print(
                f"Rating      : {rating}"
            )

            print(
                f"Vegetarian  : {is_vegetarian}"
            )

            print(
                f"Similarity  : "
                f"{similarity:.4f}"
            )

            print("-" * 50)