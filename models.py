import os
import re
import json
import requests
from typing import List, Dict, Optional, Any

try:
    from google import genai
except ImportError:
    genai = None


# ============================================================
# RECIPE
# ============================================================

class Recipe:

    def __init__(
        self,
        recipe_id,
        name,
        category,
        cuisine,
        instructions,
        ingredients,
        thumbnail="",
        source="Local Recipe Database"
    ):
        self.id = str(recipe_id)
        self.name = name
        self.category = category
        self.cuisine = cuisine
        self.instructions = instructions
        self.ingredients = ingredients
        self.thumbnail = thumbnail
        self.source = source

    @staticmethod
    def _parse_quantity(text):

        if not text:
            return None

        text = text.strip()

        try:
            mixed = re.match(
                r"^(\d+)\s+(\d+)\s*/\s*(\d+)$",
                text
            )

            if mixed:
                whole, num, den = map(float, mixed.groups())
                return None if den == 0 else whole + num / den

            fraction = re.match(
                r"^(\d+)\s*/\s*(\d+)$",
                text
            )

            if fraction:
                num, den = map(float, fraction.groups())
                return None if den == 0 else num / den

            return float(text)

        except ValueError:
            return None

    @staticmethod
    def _format_quantity(value):

        value = round(value, 2)

        return str(int(value)) if value.is_integer() else str(value)

    def scale_ingredients(self, servings, base_servings=4):

        if servings < 1:
            raise ValueError("Serving size must be at least 1.")

        multiplier = servings / max(base_servings, 1)
        scaled = []

        pattern = (
            r"^\s*("
            r"\d+\s+\d+\s*/\s*\d+|"
            r"\d+\s*/\s*\d+|"
            r"\d+\.\d+|"
            r"\d+"
            r")\s*(.*)$"
        )

        for ingredient in self.ingredients:

            item = ingredient.get("item", "").strip()
            measure = re.sub(
                r"\s+",
                " ",
                ingredient.get("measure", "").strip()
            )

            if not item:
                continue

            if not measure:
                scaled.append(item)
                continue

            match = re.match(pattern, measure)

            if not match:
                scaled.append(f"{measure} {item}")
                continue

            quantity = self._parse_quantity(match.group(1))

            if quantity is None:
                scaled.append(f"{measure} {item}")
                continue

            quantity *= multiplier
            unit = match.group(2).strip()
            quantity = self._format_quantity(quantity)

            scaled.append(
                f"{quantity} {unit} {item}".strip()
            )

        return scaled

    def to_dict(self):

        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "cuisine": self.cuisine,
            "instructions": self.instructions,
            "ingredients": self.ingredients,
            "thumbnail": self.thumbnail,
            "source": self.source
        }

    @classmethod
    def from_dict(cls, data):

        return cls(
            data.get("id", ""),
            data.get("name", "Unknown Recipe"),
            data.get("category", "General"),
            data.get("cuisine", "International"),
            data.get("instructions", "No instructions available."),
            data.get("ingredients", []),
            data.get("thumbnail", ""),
            data.get("source", "Local Recipe Database")
        )
 # ============================================================
# LOCAL RECIPE DATABASE
# ============================================================       
class LocalRecipeDatabase:

    @staticmethod
    def get_recipes():

        return [

            Recipe(
                "NG001",
                "Nigerian Jollof Rice",
                "Rice Dishes",
                "Nigerian",
                (
                    "Blend tomatoes, peppers and onions. Fry the mixture "
                    "with tomato paste and oil until thick. Add stock, "
                    "seasoning and rice. Cover and cook on low heat until "
                    "the rice is tender."
                ),
                [
                    {"item": "Long grain rice", "measure": "4 cups"},
                    {"item": "Fresh tomatoes", "measure": "6"},
                    {"item": "Red bell pepper", "measure": "3"},
                    {"item": "Scotch bonnet pepper", "measure": "2"},
                    {"item": "Onion", "measure": "2"},
                    {"item": "Tomato paste", "measure": "3 tbsp"},
                    {"item": "Vegetable oil", "measure": "1/2 cup"},
                    {"item": "Chicken stock", "measure": "4 cups"},
                    {"item": "Curry powder", "measure": "1 tsp"},
                    {"item": "Thyme", "measure": "1 tsp"},
                    {"item": "Salt", "measure": "1 tsp"}
                ]
            ),

            Recipe(
                "NG002",
                "Nigerian Fried Rice",
                "Rice Dishes",
                "Nigerian",
                (
                    "Cook the rice until almost tender. Stir-fry carrots, "
                    "green beans, peas and sweet corn in oil. Add chicken "
                    "and cooked rice, then season and stir-fry until hot."
                ),
                [
                    {"item": "Long grain rice", "measure": "4 cups"},
                    {"item": "Carrot", "measure": "2"},
                    {"item": "Green beans", "measure": "1 cup"},
                    {"item": "Green peas", "measure": "1 cup"},
                    {"item": "Sweet corn", "measure": "1 cup"},
                    {"item": "Chicken", "measure": "500 g"},
                    {"item": "Vegetable oil", "measure": "1/2 cup"},
                    {"item": "Curry powder", "measure": "1 tsp"},
                    {"item": "Salt", "measure": "1 tsp"}
                ]
            ),

            Recipe(
                "NG003",
                "Egusi Soup",
                "Soups",
                "Nigerian",
                (
                    "Fry onions in palm oil. Add ground egusi and stir. "
                    "Add stock, peppers and meat. Cook until the soup "
                    "thickens, then add spinach or ugu and simmer briefly."
                ),
                [
                    {"item": "Ground egusi", "measure": "2 cups"},
                    {"item": "Palm oil", "measure": "1 cup"},
                    {"item": "Beef", "measure": "500 g"},
                    {"item": "Spinach or ugu", "measure": "3 cups"},
                    {"item": "Fresh tomatoes", "measure": "3"},
                    {"item": "Red bell pepper", "measure": "2"},
                    {"item": "Scotch bonnet pepper", "measure": "2"},
                    {"item": "Onion", "measure": "1"},
                    {"item": "Salt", "measure": "1 tsp"}
                ]
            ),

            Recipe(
                "NG004",
                "Efo Riro",
                "Soups",
                "Nigerian",
                (
                    "Blend tomatoes, peppers and onions. Fry the mixture "
                    "in palm oil until thick. Add meat and seasoning, then "
                    "add chopped spinach or ugu. Simmer until cooked."
                ),
                [
                    {"item": "Ugu or spinach", "measure": "5 cups"},
                    {"item": "Palm oil", "measure": "3/4 cup"},
                    {"item": "Beef", "measure": "400 g"},
                    {"item": "Assorted meat", "measure": "300 g"},
                    {"item": "Tomatoes", "measure": "4"},
                    {"item": "Red bell pepper", "measure": "2"},
                    {"item": "Scotch bonnet pepper", "measure": "2"},
                    {"item": "Onion", "measure": "1"}
                ]
            ),

            Recipe(
                "NG005",
                "Okro Soup",
                "Soups",
                "Nigerian",
                (
                    "Cook the meat with onions and seasoning until tender. "
                    "Add palm oil, chopped okra, pepper and crayfish. "
                    "Cook briefly and add vegetables if desired."
                ),
                [
                    {"item": "Fresh okra", "measure": "500 g"},
                    {"item": "Beef", "measure": "400 g"},
                    {"item": "Palm oil", "measure": "1/2 cup"},
                    {"item": "Ground crayfish", "measure": "2 tbsp"},
                    {"item": "Scotch bonnet pepper", "measure": "2"},
                    {"item": "Spinach", "measure": "2 cups"},
                    {"item": "Onion", "measure": "1"}
                ]
            ),

            Recipe(
                "NG006",
                "Beans Porridge",
                "Bean Dishes",
                "Nigerian",
                (
                    "Cook beans in water until soft. Add onions, palm oil, "
                    "pepper and seasoning. Cook until thick and creamy."
                ),
                [
                    {"item": "Brown beans", "measure": "3 cups"},
                    {"item": "Palm oil", "measure": "1/2 cup"},
                    {"item": "Onion", "measure": "2"},
                    {"item": "Scotch bonnet pepper", "measure": "2"},
                    {"item": "Salt", "measure": "1 tsp"}
                ]
            ),

            Recipe(
                "NG007",
                "Moi Moi",
                "Bean Dishes",
                "Nigerian",
                (
                    "Soak and remove the skins from the beans. Blend with "
                    "pepper and onions. Add oil and seasoning. Pour into "
                    "containers and steam until firm."
                ),
                [
                    {"item": "Beans", "measure": "3 cups"},
                    {"item": "Red bell pepper", "measure": "2"},
                    {"item": "Scotch bonnet pepper", "measure": "2"},
                    {"item": "Onion", "measure": "1"},
                    {"item": "Vegetable oil", "measure": "1/2 cup"},
                    {"item": "Eggs", "measure": "4"},
                    {"item": "Salt", "measure": "1 tsp"}
                ]
            ),

            Recipe(
                "NG008",
                "Akara",
                "Bean Dishes",
                "Nigerian",
                (
                    "Soak and peel the beans. Blend with onions and pepper. "
                    "Beat the batter, add salt and fry spoonfuls in hot oil "
                    "until golden brown."
                ),
                [
                    {"item": "Beans", "measure": "2 cups"},
                    {"item": "Onion", "measure": "1"},
                    {"item": "Scotch bonnet pepper", "measure": "2"},
                    {"item": "Vegetable oil", "measure": "3 cups"},
                    {"item": "Salt", "measure": "1 tsp"}
                ]
            ),

            Recipe(
                "NG009",
                "Yam Porridge",
                "Yam Dishes",
                "Nigerian",
                (
                    "Cut and wash the yam. Add onions, palm oil, pepper, "
                    "seasoning and water. Cook until soft and mash some of "
                    "the yam to thicken the sauce."
                ),
                [
                    {"item": "Yam", "measure": "1 kg"},
                    {"item": "Palm oil", "measure": "1/2 cup"},
                    {"item": "Onion", "measure": "2"},
                    {"item": "Scotch bonnet pepper", "measure": "2"},
                    {"item": "Spinach", "measure": "2 cups"},
                    {"item": "Salt", "measure": "1 tsp"}
                ]
            ),

            Recipe(
                "NG010",
                "Nigerian Beef Suya",
                "Grilled Foods",
                "Nigerian",
                (
                    "Slice beef thinly and coat with ground peanuts, paprika, "
                    "pepper and spices. Put on skewers and grill until cooked "
                    "and slightly charred. Serve with onions and tomatoes."
                ),
                [
                    {"item": "Beef", "measure": "1 kg"},
                    {"item": "Ground roasted peanuts", "measure": "1 cup"},
                    {"item": "Paprika", "measure": "2 tbsp"},
                    {"item": "Cayenne pepper", "measure": "1 tbsp"},
                    {"item": "Ginger", "measure": "1 tsp"},
                    {"item": "Garlic", "measure": "1 tsp"},
                    {"item": "Onion", "measure": "2"},
                    {"item": "Tomatoes", "measure": "3"}
                ]
            ),

            Recipe(
                "NG011",
                "Nigerian Chicken Pepper Soup",
                "Soups",
                "Nigerian",
                (
                    "Place chicken in a pot with onions, pepper soup spice, "
                    "ginger, garlic, pepper and seasoning. Add water and cook "
                    "until tender. Add fresh herbs and simmer."
                ),
                [
                    {"item": "Chicken", "measure": "1 kg"},
                    {"item": "Pepper soup spice", "measure": "2 tbsp"},
                    {"item": "Onion", "measure": "2"},
                    {"item": "Ginger", "measure": "1 tbsp"},
                    {"item": "Garlic", "measure": "1 tbsp"},
                    {"item": "Scotch bonnet pepper", "measure": "3"},
                    {"item": "Scent leaves", "measure": "1 cup"},
                    {"item": "Salt", "measure": "1 tsp"}
                ]
            ),

            Recipe(
                "NG012",
                "Fried Plantain",
                "Side Dishes",
                "Nigerian",
                (
                    "Peel and slice ripe plantains. Heat oil and fry both "
                    "sides until golden brown. Drain and serve."
                ),
                [
                    {"item": "Ripe plantain", "measure": "4"},
                    {"item": "Vegetable oil", "measure": "2 cups"},
                    {"item": "Salt", "measure": "1/2 tsp"}
                ]
            )
        ]
