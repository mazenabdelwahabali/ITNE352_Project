## Project Description

The project's main idea was a Recipe Discovery System, and it is a network application built using Python.

There is a server that connects to TheMealDB using an API to fetch real recipe data, and the server can handle multiple clients or users at the same time using multithreading.

Each client connects to the server using a TCP socket and interacts with an organized terminal menu to search for recipes by name, category, area, or ingredients. The client can also discover random recipes and view the full details, including ingredients and instructions.

The full communication between the client and the server uses JSON files to store cached data, and the TCP protocol is used for communication with a 4-byte length header to ensure that messages are delivered properly.

---

## Semester

Semester 2 — 2025/2026
Semester 2 2025-2026

---

@@ -23,7 +20,7 @@ Semester 2 — 2025/2026
| Student Name | Student ID |
|---|---|
| Mazen Abdelwahab | 202203839 |
| Amar Ali | 202204881 |

---

@@ -32,8 +29,6 @@ Semester 2 — 2025/2026
- [Requirements](#requirements)
- [How To Run](#how-to-run)
- [The Scripts](#the-scripts)
  - [client.py](#clientpy)
  - [server.py](#serverpy)
- [Additional Concepts](#additional-concepts)
- [Acknowledgments](#acknowledgments)
- [Conclusion](#conclusion)
@@ -42,21 +37,17 @@ Semester 2 — 2025/2026

## Requirements

First, we need to download Python 3.8. No external libraries are needed — the project will work on the standard library modules.
First we need to download the Python 3.8, without any external libraries needed, the project will work on the standard library modules.

| Package | Purpose |
|---|---|
| `socket` | Used for the TCP connection and data transmission |
| `threading` | Used on the server side to handle multiple clients at the same time |
| `json` | Used for saving the data in cache and encoding/decoding messages |
| `urllib.request` | Used to request data from the TheMealDB API |
| `urllib.parse` | Used to encode the URL query strings |
| `urllib.error` | Used to handle HTTP and any network errors that happen in the connection |
| `datetime` | Used for timestamps in the server log output |
- socket package to use the TCP connection and data transmission
- threading package that will be used in the server code side, to handle multiple clients at the same time
- json for saving the data in cache and encode and decode the messages
- urllib.request the package that will be used to request the data from the TheMealDB API
- urllib.parse the package will encode the URL query strings
- urllib.error will use this package to handle the HTTP and any network error happen in the connection
- datetime will need this package in timestamp in the server log output

Note: All of the packages above are part of Python's standard library. No pip install is needed.

To clone the repository, use:
Then we need to clone the repository by using:

```bash
git clone https://github.com/mazenabdelwahabali/ITNE352_Project
@@ -67,15 +58,13 @@ cd ITNE352_Project

## How To Run

### Step 1 - Start the Server

Run the server using the following command:
First need to run the server by using command:

```bash
python server.py
```

After running, you will see:
And will show after running:

```
[info] Loading reference cache from TheMealDB...
@@ -88,15 +77,13 @@ After running, you will see:
[Info] Ready for clients. Press Ctrl+C to stop the server.
```

### Step 2 - Start the Client

Open a new terminal window and run the client to connect to the server:
Then will need to run the client to connect to the server:

```bash
python client.py
```

After running, you will see:
And will show:

```
------------------------------------------------------------
@@ -113,38 +100,32 @@ Enter your name: Mazen

### client.py

The client will provide a terminal user interface that will provide the user with the needed information to guide them to get the needed data from the server.
The client will provide a terminal user interface that will provide the user with the needed information to guide him to get the needed data from the server.

---

#### Class: Connection

This class manages the raw TCP socket — it is responsible for sending and receiving all data between the client and the server.
#### Class Connection

```python
class Connection:

    # Creates the socket and connects to the server
    # the first function is used to create the socket and connect to the server
    def connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))

    # Sends data to the server, encoded into JSON
    # the second function is used to send the data to the server and will encode it into json
    def send(self, obj):
        data   = json.dumps(obj).encode()
        length = len(data).to_bytes(4, "big")
        self.sock.sendall(length + data)

    # Receives data coming from the server
    # the receive function will receive the data that is coming from the server
    def receive(self):
        length_bytes = self._recv_exact(4)
        msg_length   = int.from_bytes(length_bytes, "big")
        raw          = self._recv_exact(msg_length)
        return json.loads(raw.decode())

    # Used because received data from the server will not arrive all at once,
    # so we receive each chunk and merge them together,
    # since there is no recv_all like sendall
    # this function will be used because the received data from the server will not sent all once
    # so we will need to receive each chunk of the data and merge them together, because we does not have receive all like the sendall function
    def _recv_exact(self, n):
        buf = b""
        while len(buf) < n:
@@ -153,16 +134,13 @@ class Connection:
        return buf
```

---

#### Class: Client
#### Class Client

This class provides a top-level controller. It connects to the server, is responsible for the TCP handshake, and starts the main menu loop that is shown to the user.
This class will provide a top level controller, connects to the server, and will be responsible for the TCP handshake and will start the main menu loop that will be shown to the user.

```python
class Client:

    # Runs the program, takes the name of the user, and performs the TCP handshake
    # this function will be used to run the program and take the name of the user and make the handshake of the TCP protocol
    def run(self):
        self.conn.connect()
        name = input("Enter your name: ").strip()
@@ -172,7 +150,7 @@ class Client:
        reference_menu = ReferenceMenu(self.conn, self.display)
        self.MainMenu(recipe_menu, reference_menu)

    # Shows the user the options they can choose to browse the system
    # this function will show to the user the options that he can choose to browse into the system
    def MainMenu(self, recipe_menu, reference_menu):
        running = True
        while running:
@@ -193,16 +171,13 @@ class Client:
                print("Invalid choice. Please enter 1, 2, or 3.")
```

---

#### Class: RecipeMenu
#### Class RecipeMenu

This class is used to handle all recipe-related user interactions.
This class is used to handle all the recipe related user interactions.

```python
class RecipeMenu:

    # Allows the user to search for recipes by name
    # this function allow the user to search for the recipes by the name of it
    def SearchByName(self):
        name = input("Enter recipe name to search: ").strip()
        self.conn.send({"type": "SEARCH_BY_NAME", "params": {"keyword": name}})
@@ -211,7 +186,7 @@ class RecipeMenu:
        self.display.recipe_list(meals)
        self.AskForDetail(meals)

    # Used if the user wants details about a specific recipe from the results
    # this function will be used if the user wants any details, can ask about it by using this function
    def AskForDetail(self, meals):
        raw = input(f"Enter number for details (1-{len(meals)}, 0=back): ").strip()
        if raw.isdigit() and 1 <= int(raw) <= len(meals):
@@ -221,68 +196,56 @@ class RecipeMenu:
            self.display.recipe_detail(response.get("data"))
```

---
#### Class ReferenceMenu

#### Class: ReferenceMenu

This class handles browsing the reference lists, like categories, areas, and ingredients.
This class handles browsing the reference list, like categories and area and ingredients.

```python
class ReferenceMenu:

    # Responsible for showing the available categories
    # this function is responsible to show the categories available
    def ShowCategories(self):
        self.conn.send({"type": "GET_CATEGORIES"})
        response = self.conn.receive()
        self.display.categories_list(response.get("data", []))

    # Responsible for showing the recipe areas
    # this function is responsible to show the recipes area
    def ShowAreas(self):
        self.conn.send({"type": "GET_AREAS"})
        response = self.conn.receive()
        self.display.flat_list(response.get("data", []), label="Area")
```

---

### server.py

The server is responsible for managing API connections, caching reference data, and handling multiple clients simultaneously using multithreading.

#### Class APIClient

This class connects to TheMealDB API and fetches all recipe-related data. It handles URL encoding, HTTP requests, error handling, and parses raw API responses into clean structured dictionaries.

```python
class APIClient:
    # Sends an HTTP GET request to the given endpoint with a 10-second timeout
    def fetch(self, endpoint):
        url = self.base_url + endpoint
        with urllib.request.urlopen(url, timeout=10) as response:
            return json.loads(response.read().decode())

    # URL-encodes the search keyword and returns a list of matching meals
    def search_by_name(self, keyword):
        endpoint = "search.php?s=" + urllib.parse.quote(keyword)
        data = self.fetch(endpoint)
        if data and data.get("meals"):
            results = []
            for meal in data["meals"]:
                results.append({
                    "idMeal":    meal["idMeal"],
                    "name":      meal["strMeal"],
                    "thumbnail": meal["strMealThumb"]
                })
            return results
        return []

    # Filters meals by category (c=), area (a=), or ingredient (i=), enforcing the max_list limit
    def filter_by(self, filter_key, value):
        endpoint = f"filter.php?{filter_key}=" + urllib.parse.quote(value)
        data = self.fetch(endpoint)
        if data and data.get("meals"):
            results = []
            for meal in data["meals"][:max_list]:
                results.append({
                    "idMeal":    meal["idMeal"],
                    "name":      meal["strMeal"],
                    "thumbnail": meal["strMealThumb"]
                })
            return results
        return []

    # Fetches full recipe details for a specific meal ID using the lookup endpoint
    def get_recipe_by_detail(self, meal_id):
        endpoint = f"lookup.php?i={meal_id}"
        data = self.fetch(endpoint)
        if data and data.get("meals"):
            return self.parse_meal(data["meals"][0])
        return None

    # Calls the random.php endpoint and returns one fully parsed random recipe
    def get_random_recipe(self):
        data = self.fetch("random.php")
        if data and data.get("meals"):
            return self.parse_meal(data["meals"][0])
        return None

    # Combines the 20 numbered ingredient and measure fields from TheMealDB into one clean list
    def parse_meal(self, meal):
        ingredients = []
        for i in range(1, 21):
            ing  = meal.get(f"strIngredient{i}", "") or ""
            meas = meal.get(f"strMeasure{i}",   "") or ""
            if ing.strip():
                combined = f"{meas.strip()} {ing.strip()}".strip()
                ingredients.append(combined)
        return {
            "idMeal":       meal.get("idMeal"),
            "name":         meal.get("strMeal"),
            "category":     meal.get("strCategory"),
            "area":         meal.get("strArea"),
            "instructions": meal.get("strInstructions"),
            "ingredients":  ingredients,
            "youtube":      meal.get("strYoutube"),
            "source":       meal.get("strSource"),
            "tags":         meal.get("strTags"),
            "thumbnail":    meal.get("strMealThumb")
        }
```

#### Class Cache

This class manages in-memory storage of static reference data (categories, areas, and ingredients) loaded at server startup, avoiding repeated API calls for each client request. The cache is additionally saved to a local JSON file for persistence.

```python
class Cache:
    # Calls the APIClient to load categories, areas, and ingredients into memory at startup
    def load(self, api_client):
        print("[info] Loading reference cache from TheMealDB...")
        self.categories  = api_client.get_categories()
        self.areas       = api_client.get_areas()
        self.ingredients = api_client.get_ingredients()
        self.is_loaded   = True

    # Writes the in-memory reference data to a local JSON file for persistence
    def save_to_file(self, filename):
        data_to_save = {
            "categories":  self.categories,
            "areas":       self.areas,
            "ingredients": self.ingredients[:max_inger],
        }
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data_to_save, f, indent=2, ensure_ascii=False)
            print(f"[Info] Reference cache saved to {filename}")
```
#### Class Clienhandler

This class operates on a separate thread for each connected client, initiating a HELLO handshake to identify the user. It then maintains a persistent loop to receive and route requests, fetching recipe-related data, sending responses back to the client, and saving a JSON log file to disk.

```python
class Clienhandler:
    # Spawns a background daemon thread so each client runs independently
    def start(self):
        thread = threading.Thread(target=self.handle, daemon=True)
        thread.start()

    # Validates the HELLO handshake then enters the main request processing loop
    def handle(self):
        msg = self._recv()
        if not msg or msg.get("type") != "HELLO":
            print(f"[Warning] Bad handshake from {self.addr}. Closing")
            self.conn.close()
            return
        self.client_name = msg.get("name", "unknown").strip() or "unknown"
        self._log(f"Connected from {self.addr[0]}:{self.addr[1]}")
        self._send({"type": "HELLO_ACK", "message": f"welcome, {self.client_name}!"})
        while True:
            request = self._recv()
            if request is None:
                break
            req_type = request.get("type", "")
            params   = request.get("params", {})
            self._log(f"Received: {req_type} params={params}")
            self._process_request(req_type, params)

    # Routes each request type to the correct data source, either cache or the live API
    def _process_request(self, req_type, params):
        if req_type == "GET_CATEGORIES":
            self._send({"type": "CATEGORIES", "source": "cache", "data": self.cache.categories})

        elif req_type == "GET_AREAS":
            self._send({"type": "AREAS", "source": "cache", "data": self.cache.areas})

        elif req_type == "GET_INGREDIENTS":
            ingredients_slice = self.cache.ingredients[:max_inger]
            self._send({"type": "INGREDIENTS", "source": "cache", "data": ingredients_slice})

        elif req_type == "SEARCH_BY_NAME":
            keyword = params.get("keyword", "")
            results = self.api_client.search_by_name(keyword)
            payload = {"type": "RECIPE_LIST", "source": "TheMealDB", "data": results}
            self._send(payload)
            self._save_file("search", payload)

        elif req_type == "FILTER_AREA":
            value   = params.get("value", "")
            results = self.api_client.filter_by("a", value)
            payload = {"type": "RECIPE_LIST", "source": "TheMealDB", "data": results}
            self._send(payload)
            self._save_file("filter_area", payload)

        elif req_type == "FILTER_CATEGORY":
            value   = params.get("value", "")
            results = self.api_client.filter_by("c", value)
            payload = {"type": "RECIPE_LIST", "source": "TheMealDB", "data": results}
            self._send(payload)
            self._save_file("filter_category", payload)

        elif req_type == "FILTER_INGREDIENT":
            value   = params.get("value", "")
            results = self.api_client.filter_by("i", value)
            payload = {"type": "RECIPE_LIST", "source": "TheMealDB", "data": results}
            self._send(payload)
            self._save_file("filter_ingredient", payload)

        elif req_type == "RANDOM_RECIPE":
            recipe  = self.api_client.get_random_recipe()
            payload = {"type": "RECIPE_DETAIL", "source": "TheMealDB", "data": recipe}
            self._send(payload)
            self._save_file("random", payload)

        elif req_type == "GET_RECIPE_DETAIL":
            meal_id = params.get("id", "")
            recipe  = self.api_client.get_recipe_by_detail(meal_id)
            payload = {"type": "RECIPE_DETAIL", "source": "TheMealDB", "data": recipe}
            self._send(payload)
            self._save_file("detail", payload)

        elif req_type == "QUIT":
            self._send({"type": "BYE"})
            self._log("Client sent QUIT.")

        else:
            self._send({"type": "ERROR", "message": f"Unknown request type: {req_type}"})

    # Serializes the object to JSON, prepends a 4-byte big-endian length header, and sends it
    def _send(self, obj):
        data   = json.dumps(obj).encode()
        length = len(data).to_bytes(4, "big")
        self.conn.sendall(length + data)

    # Reads the 4-byte header to determine message size, then reads exactly that many bytes
    def _recv(self):
        length_bytes = self._recv_exact(4)
        if length_bytes is None:
            return None
        msg_len = int.from_bytes(length_bytes, "big")
        raw     = self._recv_exact(msg_len)
        if raw is None:
            return None
        return json.loads(raw.decode())

    # Guarantees exactly n bytes are read from the TCP stream, handling chunked delivery
    def _recv_exact(self, n):
        buf = b""
        while len(buf) < n:
            chunk = self.conn.recv(n - len(buf))
            if not chunk:
                return None
            buf += chunk
        return buf

    # Saves the server response to a JSON file named: {client_name}_{operation}_{group_id}.json
    def _save_file(self, option, data):
        filename = f"{self.client_name}_{option}_{group_id}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    # Prints a timestamped log message to the server console
    def _log(self, msg):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] [{self.client_name}] {msg}", flush=True)
```
#### Class Server

This class is the main server controller manages startup tasks such as loading the cache, saving the reference file, binding the TCP socket, and running the accept loop, which spawns a new Clienthandler thread for each incoming connection.

```python
class Server:
    # Loads the cache, saves the reference file, binds the socket, and begins accepting clients
    def start(self):
        self.cache.load(self.api)
        self.cache.save_to_file(f"reference_cache_{group_id}.json")
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        print(f"[Info] Server listening on {self.host}:{self.port}")
        print(f"[Info] Group: {group_id}")
        print(f"[Info] Ready for clients. Press Ctrl+C to stop the server.")
        self._accept_loop()

    # Blocks waiting for new connections and delegates each one to a Clienhandler thread
    def _accept_loop(self):
        try:
            while True:
                conn, addr = self.server_socket.accept()
                active     = threading.active_count() - 1
                print(f"[Info] New connection from {addr[0]}:{addr[1]} (Active clients: {active})")
                handler = Clienhandler(conn, addr, self.cache, self.api)
                handler.start()
        except KeyboardInterrupt:
            print("\n[Info] Server shutting down...")
        finally:
            if self.server_socket:
                self.server_socket.close()
                print("[Info] Server socket closed.")

---

## Additional Concepts

### 1. Length-Prefix Framing Protocol

While using the TCP protocol, TCP is a stream protocol — it does not preserve message boundaries on its own. To solve this, both the server and client use a 4-byte length prefix before every JSON message. The receiver first reads exactly 4 bytes to know the message size, then reads exactly that many bytes for the content. This ensures that even large messages are received completely and correctly.

### 2. Multithreading for Handling Multiple Clients

The server uses the threading module to handle multiple clients at the same time without blocking other clients.
1. Length-Prefix Framing Protocol

### 3. Server-Side Caching
2. Multithreading for handling multiple clients:
   the server using the threading module to handle multiple clients at the same time, without blocking other clients

When the server starts, it saves the data coming from the API into a cache to be reused for each client request, so there is no need to request it again from the API each time.
3. Server side caching:
   when the server once get started it will save the data that is coming from the API into the cache to be reused for each client request

### 4. Automatic JSON File Logging

Every time the server responds to a recipe-related request (search, filter, detail, or random), it saves the response to a .json file on disk, named after the client and the type of request.
4. Automatic JSON file logging:
   Every time the server responds to a recipe-related request (search, filter, detail, random), it saves the response to a .json file on disk, named after the client and the type of request

---

## Acknowledgments

1. We learned that TheMealDB provides a free-to-use API for recipes, which was used in the project.
2. We learned how to use Python in a proper way, and we learned how to make a fully organized connection between the client and the server. We also learned how we can save the user's data in cache so there is no need to request it again if needed later.
3. We learned how to handle multiple clients at the same time using multithreading, how to handle errors using urllib.error, and the main thing — how to use sockets without needing extra packages. We also learned how to use the json package.
1. we learned that the TheMealDB is used to provide a free to use API for the recipes that been used in the project
2. we learned how to use the python in proper way and we learned how to make a full organized connection between the client and the server, also learned how we can save the data of the user in cache so no need to request it again if needed after
3. learned how to program and how to handle multiple clients at the same time by using multithreading, also how to handle the error by using the urllib.error, and the main thing is how to use the sockets without needing for extra packages, also know how to use the json package

---

## Conclusion

The Recipe Discovery System demonstrates very important ideas in network programming: TCP socket communication is a useful message framing protocol, and it can make a multithreaded server design along with the REST API.

The entire project was created using only Python's standard library, proving that you can build powerful networked applications without needing any external frameworks or libraries. By organizing the code into classes (APIClient, Cache, ClientHandler, Connection, Display), it made the code organized, easy to read, and easy to maintain.

This project offered us practical experience with real-world issues in network programming, like handling multiple users at once, and making a reliable communication protocol from scratch.
the recipe discovery system case shows very important idea in the network programming: that the TCP socket communication, is a useful message framing protocol, and can make a multithreaded server design, and the REST API
The entire project was created using only Python's standard library, proving that you can build powerful networked applications without needing any external frameworks or libraries. and by making the classes (APIClient, Cache, ClientHandler, Connection, Display), it made the code organized, and easy to read, also made it easy to maintain it
This project offered for us a practical experience in the real world issues in network programming, like handling multiple users at once, and making a reliable communication protocol from the scratch
