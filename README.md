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

*(Amar — if you have any changes, just do it or add more if you can)*
*(Amar if you have any changes, just do it or add more if you can)*

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
