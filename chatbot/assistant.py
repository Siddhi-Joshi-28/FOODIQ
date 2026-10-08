from search.semantic_search import (
    semantic_search,
    load_foods,
    MODEL_NAME
)

from sentence_transformers import SentenceTransformer


def ask_assistant(user_query, foods, model):
    """
    Process a user's food request and return recommendations.
    """

    results, conditions = semantic_search(
        user_query,
        foods,
        model,
        top_k=5
    )

    print("\n" + "=" * 60)
    print("FOODIQ AI ASSISTANT")
    print("=" * 60)

    print(f"\nUser: {user_query}")

    print("\nDetected Conditions:")
    print(f"Vegetarian     : {conditions['vegetarian']}")
    print(f"Non-Vegetarian : {conditions['non_vegetarian']}")
    print(f"Category       : {conditions['category']}")
    print(f"Max Price      : {conditions['max_price']}")
    print(f"Min Price      : {conditions['min_price']}")

    print("\nRecommendations:")
    print("-" * 60)

    if not results:
        print("Sorry, I couldn't find matching food items.")
        return

    for rank, result in enumerate(results, start=1):

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
            f"{rank}. {food_name} | "
            f"{category} | "
            f"₹{price} | "
            f"Rating: {rating} | "
            f"Vegetarian: {is_vegetarian} | "
            f"Similarity: {similarity:.4f}"
        )


if __name__ == "__main__":

    print("Loading Sentence Transformer model...")

    model = SentenceTransformer(MODEL_NAME)

    print("Model loaded successfully.")

    print("Loading foods from PostgreSQL...")

    foods = load_foods()

    print(f"Foods loaded: {len(foods)}")

    print("\n" + "=" * 60)
    print("FOODIQ AI ASSISTANT")
    print("=" * 60)
    print("Type 'exit' to stop.")

    while True:

        query = input("\nYou: ")

        if query.lower().strip() == "exit":
            print("Goodbye!")
            break

        if not query.strip():
            continue

        ask_assistant(
            query,
            foods,
            model
        )