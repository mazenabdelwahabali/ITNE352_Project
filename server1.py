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
    
    def filter_by(self, filter_key, value):
        """
        Filter meals by the given filter key and value.
        """

        endpoint = f"filter.php?{filter_key}=" + urllib.parse.quote(value)

        data = self.fetch(endpoint)

        if data and data.get("meals"):
            results = []
            for meal in data["meals"][:max_list]:
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

    def get_random_recipe(self):
        """
        
        """
        data = self.fetch("random.php")

        if data and data.get("meals"):
            return self.parse_meal(data["meals"][0])
        return None      
     
    def _prase_full_recipe(self, meal):
        """
        """

        ingreadients = []

        for i in range(1, 21):
            ing = meal.get(f"strIngredinet{i}", "") or ""
            meas= meal.get(f"strMeasure{i}", "") or ""

            if ing.strip():
                combined = f"{meas.strip()} {ing.strip()}".strip()
                ingreadients.append(combined)

        return {
            "idMeal": meal.get("idMeal"),
            "name": meal.get("strMeal"),
            "category": meal.get("strCategory"),
            "area": meal.get("strArea"),
            "instructions": meal.get("strInstructions"),
            "ingredients": ingreadients,
            "youtube": meal.get("strYoutube"),
            "source": meal.get("strSource"),
            "tags": meal.get("strTags"),
            "thumbnail": meal.get("strMealThumb")
        }

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
                    "description": cat["strCategoryDescription"]

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
    
    def get_ingredients(self):
        """
        """

        data = self.fetch("list.php?i=list")

        if data and data.get("meals"):

            return [m["strIngredient"]for m in data["meals"]]
        
        return []



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

        self.ingredients = api_client.get_ingredients()
        if self.ingredients:
            print(f"  OK - Loaded {len(self.ingredients)} ingredients")
        else:
            print("  Warning - Failed to load ingredients")

        self.is_loaded = True
    
    def save_to_file(self, filename):
        """
        """
        data_to_save = {
             "categories": self.categories,
             "areas": self.areas,
             "ingredients": self.ingredients[:max_inger],
        }
        try:
            with open(filename, "w",encoding="utf-8") as f:
                json.dump(data_to_save, f, indent=2, ensure_ascii=False)
                print(f"[Info] Reference cache saved to {filename}")
        except OSError as e:
            print(f"[Warning] Could not write file {filename}: {e}")

class Clienhandler:
    def __init__(self, conn, addr, cache, api_client):
        self.conn = conn
        self.addr = addr
        self.cache = cache
        self.api_client = api_client
        self.client_name = "Unkonwn"


    def start(self):
        """
        """
        thread = threading.Thread(target=self.handle, daemon=True)
        thread.start()

    def handle(self):
        """
        """
        try:
           msg = self._recv()
           if not msg or msg.get("type") != "Hello":
            print(f"[Warning] Bad handshake from {self.addr}. Closing")
            self.conn.close()
            return
           
           self.client_name = msg.get("name", "unknown").strip() or "unknown"
           self._log(f"Connected from {self.addr[0]}:{self.addr[1]}")

           self._send({"type": "Hello_ACK","message": f"welcome, {self.client_name}!"})

           while True:
               request = self._recv()

               if request is None:
                   break
               
               req_type = request.get("type", "")
               params = request.get("params", {})

               self._log(f"Received : {req_type} params = {params}")

        except (ConnectionResetError, BrokenPipeError, OSError) as e:

            self._log(f"Connection error : {e}")

        finally:

            self.conn.close()
            self._log("Connection closed")

    def _process_request(self, req_type, params):
        """
        """

        if req_type == "GET_CATEGORIES":

            self._send({
                "type":  "CATEGORIES",
                "source": "cache",
                "data":   self.cache.categories
            })
            self._log(f"Served {len(self.cache.categories)} categories from cache.")

        elif req_type == "GET_AREAS":

            self._send({
                "type":  "AREAS",
                "source": "cache",
                "data":   self.cache.areas
            })
            self._log(f"Served {len(self.cache.areas)} areas from cache.")

        elif req_type == "GET_INGREDIENTS":
            
            ingredients_slice = self.cache.ingredients[:max_inger]
            self._send({
                "type":  "INGREDIENTS",
                "source": "cache",
                "data":   ingredients_slice
            })
            self._log(f"Served {len(ingredients_slice)} ingredients from cache.")
        elif req_type == "SEARCH_BY_NAME":

            keyword = params.get("keyword", "")

            results = self.api_client.search_by_name(keyword)

            payload = {"type": "RECIPE_LIST", "source": "TheMealDB", "data": results}

            self._send(payload)
            self._save_file("search", payload)
            self._log(f"Search '{keyword}' --> {len(results)} results from TheMealDB.")
            