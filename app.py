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

            with st.expander(
                f"🍲 {recipe.name} | "
                f"{recipe.cuisine} | "
                f"{recipe.category}"
            ):

                c1, c2 = st.columns([1, 2])

                with c1:

                    if recipe.thumbnail:
                        st.image(
                            recipe.thumbnail,
                            use_container_width=True
                        )
                    else:
                        st.write("🍲")

                with c2:

                    st.write(
                        f"**Cuisine:** {recipe.cuisine}"
                    )

                    st.write(
                        f"**Category:** {recipe.category}"
                    )

                    st.write(
                        f"**Source:** {recipe.source}"
                    )

                    st.subheader("🥕 Ingredients")

                    for item in recipe.ingredients:

                        st.write(
                            f"- {item.get('measure', '')} "
                            f"{item.get('item', '')}"
                        )

                st.subheader("👨‍🍳 Cooking Instructions")

                st.write(recipe.instructions)

                # ------------------------------------------------
                # Add to planner
                # ------------------------------------------------

                st.subheader("🗓️ Add To Meal Plan")

                c1, c2, c3 = st.columns([2, 2, 1])

                day = c1.selectbox(
                    "Day",
                    [
                        "Monday",
                        "Tuesday",
                        "Wednesday",
                        "Thursday",
                        "Friday",
                        "Saturday",
                        "Sunday"
                    ],
                    key=f"day_{recipe.id}"
                )

                meal = c2.selectbox(
                    "Meal",
                    [
                        "Breakfast",
                        "Lunch",
                        "Dinner"
                    ],
                    key=f"meal_{recipe.id}"
                )

                if c3.button(
                    "➕ Add",
                    key=f"add_{recipe.id}"
                ):

                    meal_plan.append({
                        "day": day,
                        "meal_type": meal,
                        "recipe": recipe.to_dict()
                    })

                    st.success(
                        f"{recipe.name} added to {day}."
                    )

                st.divider()

                # ------------------------------------------------
                # Favourite
                # ------------------------------------------------

                favourite_ids = [
                    str(x.get("id"))
                    for x in favourites
                ]

                if str(recipe.id) in favourite_ids:

                    if st.button(
                        "💔 Remove Favourite",
                        key=f"remove_fav_{recipe.id}"
                    ):

                        st.session_state.favourites = [
                            x for x in favourites
                            if str(x.get("id"))
                            != str(recipe.id)
                        ]

                        planner.save_favourites(
                            st.session_state.favourites
                        )

                        st.rerun()

                else:

                    if st.button(
                        "❤️ Add Favourite",
                        key=f"fav_{recipe.id}"
                    ):

                        favourites.append(
                            recipe.to_dict()
                        )

                        planner.save_favourites(
                            favourites
                        )

                        st.success(
                            "Added to favourites."
                        )

                # ------------------------------------------------
                # Gemini
                # ------------------------------------------------

                st.divider()

                st.subheader("🤖 AI Recipe Help")

                if st.button(
                    "✨ Simplify Recipe",
                    key=f"ai_{recipe.id}"
                ):

                    if not api_key:

                        st.warning(
                            "Enter your Gemini API key first."
                        )

                    else:

                        with st.spinner(
                            "Gemini is working..."
                        ):

                            ai_results[recipe.id] = (
                                ai.enhance_recipe(recipe)
                            )

                if recipe.id in ai_results:

                    info = ai_results[recipe.id]

                    st.success(
                        f"Difficulty: "
                        f"{info.get('difficulty', 'Unknown')}"
                    )

                    st.write("**📝 Simple Steps**")

                    for i, step in enumerate(
                        info.get("simple_steps", []),
                        1
                    ):
                        st.write(
                            f"{i}. {step}"
                        )

                    st.write(
                        "**💰 Local Substitutes**"
                    )

                    for item in info.get(
                        "substitutions",
                        []
                    ):
                        st.write(
                            f"- {item}"
                        )
