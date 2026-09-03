import re
import pandas as pd
import streamlit as st

from models import (
    Recipe,
    MealDBClient,
    GeminiHelper,
    MealPlanner,
    ShoppingListGenerator
)


# ============================================================
# SETUP
# ============================================================

st.set_page_config(
    page_title="Smart Recipe & Meal Planner",
    page_icon="🍽️",
    layout="wide"
)

client = st.session_state.setdefault("client", MealDBClient())
planner = st.session_state.setdefault("planner", MealPlanner())
st.session_state.setdefault("search_results", [])
st.session_state.setdefault("ai_results", {})

if "meal_plan" not in st.session_state:
    st.session_state.meal_plan = planner.load_plan()[0]

if "favourites" not in st.session_state:
    st.session_state.favourites = planner.load_favourites()

meal_plan = st.session_state.meal_plan
favourites = st.session_state.favourites
results = st.session_state.search_results
ai_results = st.session_state.ai_results


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("🍽️ Smart Meal Planner")

st.sidebar.write(
    "Explore Nigerian and international recipes, "
    "plan your meals, manage favourites and create "
    "shopping lists."
)

st.sidebar.header("🤖 AI Settings")

api_key = st.sidebar.text_input(
    "Gemini API Key",
    type="password"
)

ai = GeminiHelper(api_key)

if api_key:
    if ai.is_available():
        st.sidebar.success("Gemini AI connected.")
    else:
        st.sidebar.error("Gemini could not be initialized.")
else:
    st.sidebar.info("AI features are optional.")


# ============================================================
# TITLE & STATISTICS
# ============================================================

st.title("🍽️ Smart Recipe & Meal Planner")

st.write(
    "Discover recipes from Nigeria and around the world, "
    "plan your meals and create your shopping list."
)

recipes = client.get_all_local_recipes()

c1, c2, c3, c4 = st.columns(4)

c1.metric("🍽️ Available Recipes", len(recipes))
c2.metric("🗓️ Planned Meals", len(meal_plan))
c3.metric("❤️ Favourites", len(favourites))
c4.metric("📁 Saved Data", "JSON")


# ============================================================
# TABS
# ============================================================

search_tab, planner_tab, shopping_tab, favourite_tab = st.tabs([
    "🔍 Search Recipes",
    "🗓️ Weekly Planner",
    "🛒 Shopping List",
    "❤️ Favourites"
])


# ============================================================
# SEARCH
# ============================================================

with search_tab:

    st.header("🔍 Search Recipes")

    st.write(
        "Search by meal name, main ingredient or category."
    )

    c1, c2 = st.columns([3, 2])

    query = c1.text_input(
        "Search",
        placeholder="Jollof Rice, Pasta, Chicken, Beans..."
    )

    search_type = c2.selectbox(
        "Search By",
        ["Meal Name", "Main Ingredient", "Category"]
    )

    if st.button("🔎 Search", type="primary"):

        if not query.strip():

            st.warning("Please enter a search term.")

        else:

            try:

                if search_type == "Meal Name":
                    found = client.search_by_name(query)

                elif search_type == "Main Ingredient":
                    found = client.filter_by_ingredient(query)

                else:
                    found = client.filter_by_category(query)

                st.session_state.search_results = found
                results = found

            except Exception as e:
                st.error(f"Search error: {e}")

    # --------------------------------------------------------
    # Popular Recipes
    # --------------------------------------------------------

    st.subheader("🌍 Popular Recipes")

    popular_foods = [
        "Jollof Rice",
        "Pasta",
        "Pizza",
        "Chicken Curry",
        "Fried Rice",
        "Tacos",
        "Sushi",
        "Lasagna",
        "Burgers",
        "Pancakes",
        "Biryani",
        "Chicken Teriyaki"
    ]

    cols = st.columns(4)

    for i, food in enumerate(popular_foods):

        if cols[i % 4].button(
            food,
            key=f"popular_{i}",
            use_container_width=True
        ):

            st.session_state.search_results = (
                client.search_by_name(food)
            )

            st.rerun()

    st.divider()

    # --------------------------------------------------------
    # Results
    # --------------------------------------------------------

    if not results:

        st.info(
            "Search for a recipe or choose a popular recipe."
        )

    else:

        st.subheader(
            f"🍽️ Recipe Results ({len(results)})"
        )

        for recipe in results:
