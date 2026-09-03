import os
import re
import json
import requests
from typing import List, Dict, Optional, Any

try:
    from google import genai
except ImportError:
    genai = None
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
