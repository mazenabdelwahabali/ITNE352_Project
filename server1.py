from datetime import datetime
import socket
import threading
import json
import urllib.request
import urllib.parse
import urllib.error

host = "0.0.0.0"
port = 5000
group_id = "Group_5"

max_list = 15
max_inger = 50

api_base_url = "https://www.themealdb.com/api/json/v1/1/"

class APIClient:
    def __init__(self, base_url):
        self.base_url = base_url
    
    def fetch(self, endpoint):
        url = self.base_url + endpoint
        try:
            with urllib.request.urlopen(url, timeout=10) as response:
                    raw_text = response.read().decode()
                    return json.loads(raw_text)
        except urllib.error.URLError as e:
            print(f"Error: {e.reason}")
            return None
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e.msg}")
            return None

    def search_by_name(self, keyword):
        """
        Search meals by name.
        """
        endpoint = "search.php?s=" + urllib.parse.quote(keyword)
        data = self.fetch(endpoint)

        if data and data.get("meals"):
            results = []
            for meal in data["meals"]:
                results.append({
                    "idMeal": meal["idMeal"],
                    "name": meal["strMeal"],
                    "thumbnail": meal["strMealThumb"]
                })
            return results
        return []
    
    def get_recipe_by_detail(self, meal_id):
        """
        Get detailed recipe information by meal ID.
        """
        endpoint = f"lookup.php?i={meal_id}"
        data = self.fetch(endpoint)

        if data and data.get("meals"):
            return self.parse_meal(data["meals"][0])
        return None       

    def get_random_meal(self):
        """
        Get a random meal.
        """
        data = self.fetch("random.php")

        if data and data.get("meals"):
            return self.parse_meal(data["meals"][0])
        return None       

def get_categories(self):
        """
        List meal categories.
        """
        data = self.fetch("categories.php")

        if data and data.get("categories"):
            results = []
            for cat in data["categories"]:
                results.append({
                    "name": cat["strCategory"],
                    "thumbnail": cat["strCategoryThumb"]
                })
            return results
        return []

    def get_areas(self):
        """
        List available meal areas.
        """
        data = self.fetch("list.php?a=list")

        if data and data.get("meals"):
            return [m["strArea"] for m in data["meals"] if m.get("strArea")]
        return []

    def parse_meal(self, meal):
        """
        Parse a meal into structured recipe data.
        """
        ingredients = []

        for i in range(1, 21):
            ing = meal.get(f"strIngredient{i}")
            measure = meal.get(f"strMeasure{i}")
            if ing and ing.strip():
                combined = f"{measure.strip()} {ing.strip()}".strip()
                ingredients.append(combined)

        return {
            "idMeal": meal.get("idMeal"),
            "name": meal.get("strMeal"),
            "category": meal.get("strCategory"),
            "area": meal.get("strArea"),
            "instructions": meal.get("strInstructions"),
            "ingredients": ingredients,
            "youtube": meal.get("strYoutube"),
            "source": meal.get("strSource"),
            "tags": meal.get("strTags"),
            "thumbnail": meal.get("strMealThumb")
        }


class Cache:
    def __init__(self):
        self.categories = []
        self.areas = []
        self.recipes = {}
        self.ingredients = []
        self.is_loaded = False

    def load(self, api_client):
        print("[info] Loading reference cache from TheMealDB...")

        self.categories = api_client.get_categories()
        if self.categories:
            print(f"  OK - Loaded {len(self.categories)} categories")
        else:
            print("  Warning - Failed to load categories")

        self.areas = api_client.get_areas()
        if self.areas:
            print(f"  OK - Loaded {len(self.areas)} areas")
        else:
            print("  Warning - Failed to load areas")