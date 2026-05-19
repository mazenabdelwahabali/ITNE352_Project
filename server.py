from datetime import datetime
import socket
import threading
import json
import urllib.request
import urllib.parse
import urllib.error

# settings for network configuration.
host = "127.0.0.1" # the host ip address for the server to bind to.
port = 5000 # host port for the server to listen to.
group_id = "Group_15"

max_list = 15 # maximum number of recipes returned in a list
max_inger = 50 # maximum number of ingredients displayed per recipe

api_base_url = "https://www.themealdb.com/api/json/v1/1/" # base URL for TheMealDB API.

class APIClient:
   
     # fetches, parses, and returns recipe data from the TheMealDB API.
   
    def __init__(self, base_url): # stores the base URL for all API requests.
        
        self.base_url = base_url
    
    def fetch(self, endpoint): # sends an HTTP GET request to the given endpoint and returns parsed JSON.
        
       
        url = self.base_url + endpoint # handles network or DNS connection errors.
        try:
            # establish an HTTP connection with a 10-second timeout.
            with urllib.request.urlopen(url, timeout=10) as response:
                    # read the response bytes and decode into a string.
                    raw_text = response.read().decode()
                    # turns raw string into a Python dictionary/list.
                    return json.loads(raw_text)
            
        except urllib.error.URLError as e:
            # handles network or DNS connection errors.
            print(f"Error: {e.reason}")

            return None
        
        except json.JSONDecodeError as e:
            # handles invalid or malformed JSON responses
            print(f"Error decoding JSON: {e.msg}")

            return None

    def search_by_name(self, keyword): # searches meals by name keyword.

        # to handle spaces and special characters, URL-encode the search query.
        endpoint = "search.php?s=" + urllib.parse.quote(keyword)
        data = self.fetch(endpoint)

       
        if data and data.get("meals"): # structure payload if valid results are found.
            results = []

            for meal in data["meals"]:
                results.append({

                    "idMeal": meal["idMeal"],
                    "name": meal["strMeal"],
                    "thumbnail": meal["strMealThumb"]

                })

            return results
        
        return [] # if there are no matches return an empty list.
    
    def filter_by(self, filter_key, value): # filter meals by the given filter key and value.
        
        # create the filtered query string using the encoded parameters.
        endpoint = f"filter.php?{filter_key}=" + urllib.parse.quote(value)

        data = self.fetch(endpoint)
        # structure payload and enforce max list limit
        if data and data.get("meals"):
            results = []

            # Slice the list to respect maximum result constraints
            for meal in data["meals"][:max_list]:
                results.append({

                    "idMeal": meal["idMeal"],
                    "name": meal["strMeal"],
                    "thumbnail": meal["strMealThumb"]

                })

            return results
        
        return [] # return empty list if no matches exist
    
    def get_recipe_by_detail(self, meal_id): # get detailed recipe information by meal ID.
       
       # create the API lookup query using the specific meal ID
        endpoint = f"lookup.php?i={meal_id}"
        data = self.fetch(endpoint)

        # If data is found pass the meal data dictionary to the parser
        if data and data.get("meals"):
            return self.parse_meal(data["meals"][0])
        return None       

    def get_random_recipe(self): # get a single random recipe from the API.
        
       # call the random target endpoint
        data = self.fetch("random.php")

        # parse and return the random meal object if successfully retrieved
        if data and data.get("meals"):
            return self.parse_meal(data["meals"][0])
        return None      
     
    def parse_meal(self, meal): # method for organizing and cleaning raw meal data payloads and combines the divided ingredients and measurements from the API into a single list.

        ingreadients = []

        # theMealDB uses 20 numbered fields for ingredients and matching measurements
        for i in range(1, 21):

            # extract values falling back to an empty string if fields are null
            ing = meal.get(f"strIngredient{i}", "") or ""
            meas= meal.get(f"strMeasure{i}", "") or ""

            # only proceed if ingredient text is not empty.
            if ing.strip():
                # combine measurement and ingredient text 
                combined = f"{meas.strip()} {ing.strip()}".strip()
                ingreadients.append(combined)

                # return a organized dictionary of item fields.
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

    def get_categories(self): #List meal categories.

        # request the endpoint for static categories
        data = self.fetch("categories.php")

        if data and data.get("categories"):
            results = []

            # extract and format the name and description details for each category
            for cat in data["categories"]:
                results.append({

                    "name": cat["strCategory"],
                    "description": cat["strCategoryDescription"]

                })

            return results
        
        return []

    def get_areas(self): # list available meal areas.

        #  request the database area list endpoint (such as American, Japanese, or Italian).
        data = self.fetch("list.php?a=list")

        # use a list comprehension to extract non-empty geographic area strings
        if data and data.get("meals"):
            return [m["strArea"] for m in data["meals"] if m.get("strArea")]
        return []
    
    def get_ingredients(self): # get a list of all recognized ingredient names from the database.

        # call the ingredient master list endpoint
        data = self.fetch("list.php?i=list")

        # map out just the text name of every available ingredient
        if data and data.get("meals"):
            return [m["strIngredient"]for m in data["meals"]]
        
        return []



class Cache: # manages in-memory storage and reduces unnecessary external API network queries by managing the static reference data (such as categories, places, and ingredients).
    def __init__(self):
        self.categories = [] # holds list of structured meal categories
        self.areas = [] # holds list of available meal areas
        self.recipes = {} # holds cached meal recipes
        self.ingredients = [] # holds list of recognized ingredient names
        self.is_loaded = False # flag to indicate state initialization status

    def load(self, api_client):# loads the reference data from the API client and stores it in memory for quick access.

        print("[info] Loading reference cache from TheMealDB...")

        # request category list from client and log execution state
        self.categories = api_client.get_categories()
        if self.categories:
            print(f"  OK - Loaded {len(self.categories)} categories")
        else:
            print("  Warning - Failed to load categories")

        # request global culinary areas list and log execution state
        self.areas = api_client.get_areas()
        if self.areas:
            print(f"  OK - Loaded {len(self.areas)} areas")
        else:
            print("  Warning - Failed to load areas")

             # request global meal components list and log execution state
        self.ingredients = api_client.get_ingredients()
        if self.ingredients:
            print(f"  OK - Loaded {len(self.ingredients)} ingredients")
        else:
            print("  Warning - Failed to load ingredients")

        self.is_loaded = True
    
    def save_to_file(self, filename): # saves the reference cache data to a local JSON file for persistence across server restarts and to provide a snapshot of the reference data at startup.
        data_to_save = {
             "categories": self.categories,
             "areas": self.areas,
             "ingredients": self.ingredients[:max_inger], # Slices the master list using max limit
        }
        try:
             # open local file path with UTF-8 encoding support
            with open(filename, "w",encoding="utf-8") as f:
                json.dump(data_to_save, f, indent=2, ensure_ascii=False)
                print(f"[Info] Reference cache saved to {filename}")

        except OSError as e:# handles unexpected low-level operational file write hazards
            print(f"[Warning] Could not write file {filename}: {e}")

class Clienhandler: # manages an isolated connected socket user client's network life cycles, request processing, framing protocols, and transaction logs
    def __init__(self, conn, addr, cache, api_client):
        self.conn = conn
        self.addr = addr
        self.cache = cache
        self.api_client = api_client
        self.client_name = "Unkonwn"


    def start(self): # to isolate client tasks without interfering with main execution cycles and a background listener daemon thread is spawned and executed.
        thread = threading.Thread(target=self.handle, daemon=True)
        thread.start()

    def handle(self):# monitors socket traffic channels prior to forwarding application command payloads, identity validation handshakes are implemented.
        try:
           msg = self._recv()
           # Enforce HELLO validation frame structure check
           if not msg or msg.get("type") != "HELLO":
            print(f"[Warning] Bad handshake from {self.addr}. Closing")
            self.conn.close()
            return
           
            # extract client identity string metadata
           self.client_name = msg.get("name", "unknown").strip() or "unknown"
           self._log(f"Connected from {self.addr[0]}:{self.addr[1]}")

            # send Handshake response acknowledge with welcome message
           self._send({"type": "HELLO_ACK","message": f"welcome, {self.client_name}!"})

           # enter persistent request polling traffic control cycle loop
           while True:
               request = self._recv()

               # intercept channel teardown or disconnections
               if request is None:
                   break
               
               req_type = request.get("type", "")
               params = request.get("params", {})

               self._log(f"Received : {req_type} params = {params}")
               self._process_request(req_type, params)

        except (ConnectionResetError, BrokenPipeError, OSError) as e: # capture unpredictable standard host platform connection crashes
            self._log(f"Connection error : {e}")

        finally:
            # always make sure that file descriptor connection lifecycle teardowns are always clean.
            self.conn.close()
            self._log("Connection closed")

    def _process_request(self, req_type, params):# switchboard for internal request routing and writes transaction files, maps proxy connections, and retrieves metadata arrays locally.

        # server-side Cache Dispatch Routines
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

            # web Database Core Gateway Queries
        elif req_type == "SEARCH_NAME":
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

            # system session Controls
        elif req_type == "QUIT":
            self._send({"type": "BYE"})
            self._log("Client sent QUIT.")

            # error / fallback routing
        else:
            self._send({"type": "ERROR", "message": f"Unknown request type: {req_type}"})
            self._log(f"Unknown request type: '{req_type}'")

    def _send(self, obj):# converts JSON wire strings from Python data dictionaries and creates a header block with a 4-byte big-endian framing length.
        
        data = json.dumps(obj).encode()
        length = len(data).to_bytes(4, "big")

        self.conn.sendall(length + data)

    def _recv(self): # reads length the predictable 4-byte message block prefix header
        length_bytes = self._recv_exact(4)

        if length_bytes is None:
            return None
        
        # calculate dynamic remaining network stream content segment size
        msg_len = int.from_bytes(length_bytes, "big")

        raw = self._recv_exact(msg_len)

        if raw is None:
            return None
        
        return json.loads(raw.decode())
        

    def _recv_exact(self, n):# Guarantees extraction of exactly 'n' bytes from TCP socket buffers.
    
        buf = b""
        while len(buf) < n:
            chunk = self.conn.recv(n - len(buf))
            if not chunk: # detect early socket channel disconnections
                return None
            buf += chunk
        return buf
    
    def _save_file(self, option, data):# saves transaction state results into isolated tracking JSON documents 

        filename = f"{self.client_name}_{option}_{group_id}.json"
        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except OSError as e:
            self._log(f"Could not write {filename}: {e}")

    def _log(self, msg):# formats console status notifications with current system wall timestamps.
       
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] [{self.client_name}] {msg}", flush=True)

class Server:# main controller engine managing port assignments, cache bindings, and multi-threaded socket listener infrastructure loops

    def __init__(self, host, port):
        self.host    = host # assigned local listening network adapter interface
        self.port    = port # network application bind access port channel
        self.api     = APIClient(api_base_url) # main web client instance for API connectivity
        self.cache = Cache() # shared data access memory cache engine
        self.server_socket = None # socket binding placeholder variable

    def start(self):# main ignition framework method. Loads core data dependencies into memory, persists a local cache file snapshot, and configures the incoming TCP socket connection point.

        # use the Web API to fill the shared cache component array structures.
        self.cache.load(self.api)

        # create a tracking local JSON file by serializing operational cache results.
        ref_filename = f"reference_cache_{group_id}.json"
        self.cache.save_to_file(ref_filename)

        # create a standard IPv4 streaming TCP network communication socket
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # enable immediate socket address re-use to bypass operating system port locks on crash
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)

        print(f"[Info] Server listening on {self.host}:{self.port}")
        print(f"[Info] Group: {group_id}")
        print(f"[Info] Ready for clients. Press Ctrl+C to stop the server.")

        # switch the execution control context to the primary blocking acceptance procedure.
        self._accept_loop()

    def _accept_loop(self):# loops infinitely on the listening socket interface accepts incoming remote clients and maps them to clean handler tracking threads.
        try:
            while True:
                
                # block thread operation until a remote user hits the listening address channel
                conn, addr = self.server_socket.accept()

                # gauge system usage metrics, discarding the primary script main runner context thread
                active = threading.active_count() - 1
                print(f"[Info] New connection from {addr[0]}:{addr[1]}"
                      f"(Active clients: {active})")
                
                # construct client handler tracking instance and delegate payload process management
                handler = Clienhandler(conn, addr, self.cache, self.api)
                handler.start()

                # handle terminal interrupt exceptions (Ctrl+C) smoothly
        except KeyboardInterrupt:
            print("\n[Info] Server shutting down...")

        finally:
            # safely release networking hook binds upon server termination lifecycles
            if self.server_socket:
                self.server_socket.close()
                print("[Info] Server socket closed.")


if __name__ == "__main__":
    # program driver point. Spin up and activate the complete server instance topology.
    server = Server(host, port)
    server.start()
