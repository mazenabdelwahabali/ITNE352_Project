from datetime import datetime
import socket
import threading
import json
import urllib.request
import urllib.parse
import urllib.error

host = "127.0.0.1"
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
     
    def parse_meal(self, meal):
        """
        """

        ingreadients = []

        for i in range(1, 21):
            ing = meal.get(f"strIngredient{i}", "") or ""
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
           if not msg or msg.get("type") != "HELLO":
            print(f"[Warning] Bad handshake from {self.addr}. Closing")
            self.conn.close()
            return
           
           self.client_name = msg.get("name", "unknown").strip() or "unknown"
           self._log(f"Connected from {self.addr[0]}:{self.addr[1]}")

           self._send({"type": "HELLO_ACK","message": f"welcome, {self.client_name}!"})

           while True:
               request = self._recv()

               if request is None:
                   break
               
               req_type = request.get("type", "")
               params = request.get("params", {})

               self._log(f"Received : {req_type} params = {params}")
               self._process_request(req_type, params)

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


        elif req_type == "FILTER_AREA":
            value = params.get("value", "")
            results = self.api_client.filter_by("a", value)
            payload = {"type": "RECIPE_LIST", "source": "TheMealDB", "data": results}
            self._send(payload)
            self._save_file("filter_area", payload)
            self._log(f"Filter by area '{value}' --> {len(results)} results from TheMealDB.")


        elif req_type == "FILTER_CATEGORY":
            value = params.get("value", "")
            results = self.api_client.filter_by("c", value)
            payload = {"type": "RECIPE_LIST", "source": "TheMealDB", "data": results}
            self._send(payload)
            self._save_file("filter_category", payload)
            self._log(f"Filter by category '{value}' --> {len(results)} results from TheMealDB.")


        elif req_type == "FILTER_INGREDIENT":
             value = params.get("value", "")
             results = self.api_client.filter_by("i", value)
             payload = {"type": "RECIPE_LIST", "source": "TheMealDB", "data": results}
             self._send(payload)
             self._save_file("filter_ingredient", payload)
             self._log(f"Filter by ingredient '{value}' --> {len(results)} results from TheMealDB.")


        elif req_type == "RANDOM_RECIPE":
            recipe = self.api_client.get_random_recipe()
            payload = {"type": "RECIPE_DETAIL", "source": "TheMealDB", "data": recipe}
            self._send(payload)
            self._save_file("random", payload)
            recipe_name = recipe["name"] if recipe else "None"
            self._log(f"Random recipe --> '{recipe_name}' from TheMealDB.")

        elif req_type == "GET_RECIPE_DETAIL":
            meal_id = params.get("id", "")
            recipe = self.api_client.get_recipe_by_detail(meal_id)
            payload = {"type": "RECIPE_DETAIL", "source": "TheMealDB", "data": recipe}
            self._send(payload)
            self._save_file("detail", payload)
            recipe_name = recipe["name"] if recipe else "Not Found"
            self._log(f"Detail for ID = '{meal_id}' --> '{recipe_name}' from TheMealDB.")

        elif req_type == "QUIT":
            self._send({"type": "BYE"})
            self._log("Client sent QUIT.")

        else:
            self._send({"type": "ERROR", "message": f"Unknown request type: {req_type}"})
            self._log(f"Unknown request type: '{req_type}'")

    def _send(self, obj):
        """
        """
        
        data = json.dumps(obj).encode()

        length = len(data).to_bytes(4, "big")

        self.conn.sendall(length + data)

    def _recv(self):
        """
        """

        length_bytes = self._recv_exact(4)

        if length_bytes is None:
            return None
        
        msg_len = int.from_bytes(length_bytes, "big")

        raw = self._recv_exact(msg_len)

        if raw is None:
            return None
        
        return json.loads(raw.decode())
        

    def _recv_exact(self, n):
        """
        """
        buf = b""
        while len(buf) < n:
            chunk = self.conn.recv(n - len(buf))
            if not chunk:
                return None
            buf += chunk
        return buf
    
    def _save_file(self, option, data):
        """
        """
        filename = f"{self.client_name}_{option}_{group_id}.json"
        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except OSError as e:
            self._log(f"Could not write {filename}: {e}")

    def _log(self, msg):
        """
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] [{self.client_name}] {msg}", flush=True)

class Server:

    def __init__(self, host, port):
        self.host    = host
        self.port    = port
        self.api     = APIClient(api_base_url)
        self.cache = Cache()
        self.server_socket = None

    def start(self):
        """
        """

        self.cache.load(self.api)

        ref_filename = f"reference_cache_{group_id}.json"
        self.cache.save_to_file(ref_filename)

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)

        print(f"[Info] Server listening on {self.host}:{self.port}")
        print(f"[Info] Group: {group_id}")
        print(f"[Info] Ready for clients. Press Ctrl+C to stop the server.")

        self._accept_loop()

    def _accept_loop(self):
        """
        """
        try:
            while True:

                conn, addr = self.server_socket.accept()
                
                active = threading.active_count() - 1
                print(f"[Info] New connection from {addr[0]}:{addr[1]}"
                      f"(Active clients: {active})")
                
                handler = Clienhandler(conn, addr, self.cache, self.api)
                handler.start()

        except KeyboardInterrupt:
            print("\n[Info] Server shutting down...")

        finally:

            if self.server_socket:
                self.server_socket.close()
                print("[Info] Server socket closed.")


if __name__ == "__main__":
    server = Server(host, port)
    server.start()