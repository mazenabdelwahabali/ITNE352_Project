import socket
import json

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 5000

#the valuse of the categories and the areas are used for the user to search for
VALID_CATEGORIES = [
    "Beef", "Chicken", "Seafood", "Vegetarian",
    "Dessert", "Pasta", "Breakfast"
]
VALID_AREAS = [
    "Italian", "Indian", "Mexican", "Japanese",
    "Moroccan", "British", "American", "Thai"
]

# separators
LINE      = "-" * 60
THIN_LINE = "." * 60


#this class used used to control the socket and can handle the lowlevel communication
class Connection:

    def __init__(self, host, port):
        self.host = host #the server id address
        self.port = port #the server port number
        self.sock = None #the socket object that will be used to communicate with the server; initialized to None until we connect

    def connect(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #create a TCP socket using IPv4
            self.sock.connect((self.host, self.port)) #connect the socket to the server using the host and port provided in the constructor
            return True #if the connection is successful, return True
        except ConnectionRefusedError:
            return False #if the connection is refused, if the server is not running or not reachable, return False

    def send(self, obj): #this function is used to send a Python object (usually a dict) to the server; it converts the object to JSON, encodes it to bytes, and sends it with a 4-byte length prefix
        data = json.dumps(obj).encode() #this will convert the Python object to a JSON string and then encode it to bytes, which is the format needed for sending over a socket
        length = len(data).to_bytes(4, "big") #this will calculate the length of the data in bytes and convert it to a 4-byte big-endian integer, which will be sent before the actual data so the server knows how many bytes to expect for this message
        self.sock.sendall(length + data) #this will send the length prefix followed by the actual data to the server; sendall() ensures that all bytes are sent before returning

    def receive(self): #this function is used to receive a response from the server; it reads the 4-byte length prefix to know how many bytes to read for the actual data, then reads that many bytes and decodes it from JSON back to a Python object
        length_bytes = self._recv_exact(4) #this will read the first 4 bytes from the socket, which should contain the length of the incoming message
        if not length_bytes:
            return None #if we receive an empty response, it means the server has closed the connection, so we return None to indicate that
        msg_length = int.from_bytes(length_bytes, "big") #this will convert the 4-byte length prefix from bytes to an integer, which tells us how many bytes we need to read for the actual message
        raw = self._recv_exact(msg_length) #this will call the helper function recv_exact to read exactly msg_length bytes from the socket, which should be the full message from the server
        if raw is None:
            return None #if we receive an empty response while trying to read the message, it means the server has closed the connection, so we return None to indicate that
        return json.loads(raw.decode()) #this will decode the raw bytes to a string and then parse the JSON to convert it back to a Python object, which we return as the response from the server

    #this function will keep reading all the bytes sended from the server
    #and will return the full message once we have received all the expected bytes
    def _recv_exact(self, n):
        buf = b""
        while len(buf) < n:
            chunk = self.sock.recv(n - len(buf)) #this will read up to n - len(buf) bytes from the socket, which is how many bytes we still need to read to reach n
            if not chunk:
                return None
            buf += chunk
        return buf

    def close(self):
        if self.sock:
            self.sock.close() #this will close the socket connection to the server, which is important for cleaning up resources and allowing the server to free up any resources associated with this client


class Client:

    def __init__(self, host, port):
        self.conn = Connection(host, port) #will make an objest of the connection class to can communicate with the server
        self.display = Display() #will use the display class to make an object to use the functions in it

    def run(self):
        print(LINE)
        print("recipe discovery system")
        print(LINE)
        print(f"will connect to the server, ip {SERVER_HOST} and port {SERVER_PORT}")

        if not self.conn.connect():
            print("could not connect to the server. Make sure the server is running and reachable.")
            return
        print("connected to the server successfully!")

        name = input("Enter your name: ").strip() #this will prompt the user to enter their name and remove any leading/trailing whitespace
        while not name:
            name = input("Name cannot be empty, enter your name: ").strip() #if the user enters an empty name, we will keep prompting them until they enter a valid name

        self.conn.send({"type": "HELLO", "name": name})
        ack = self.conn.receive() #that will send ack that is received from the server and the connection working properly
        if ack and ack.get("type") == "HELLO_ACK":  # FIX 1
            print(f"\n {ack.get('message')}\n")
        else:
            print("\n  Did not receive proper acknowledgment from server.")
            return

        recipe_menu    = RecipeMenu(self.conn, self.display) # this will make an object of the class recipe menu, to use the functions in it
        reference_menu = ReferenceMenu(self.conn, self.display) # this will make an object of the class reference menu, to use the functions in it

        try:
            self.MainMenu(recipe_menu, reference_menu) #this will call the main function of the menu class to show the main menu to the user and handle their choices
        except (ConnectionResetError, BrokenPipeError):
            print("\n  there are problem with the connection to the server")
        except KeyboardInterrupt:
            print("\n  the connection got interrupted by user")
        finally:
            self.conn.close() #this will ensure that the connection to the server is closed properly when the client is done, whether it finishes normally or encounters an error
            print("\n  connection is closed")

    def MainMenu(self, recipe_menu, reference_menu):
        running = True

        while running:
            print("==== Main Menu - Recipe Discovery System ====")
            print("1. Browse recipes")
            print("2. Reference lists")
            print("3. Quit")

            choice = input("Enter your choice: ")

            if choice == "1":
                recipe_menu.show()
            elif choice == "2":
                reference_menu.show()
            elif choice == "3":
                print("Goodbye! Disconnecting from server...")
                self.conn.send({"type": "QUIT"})
                running = False
            else:
                print("Invalid choice. Please enter 1, 2, or 3.")


class RecipeMenu:

    def __init__(self, connection, display):
        self.conn = connection #the Connection object that will be used to communicate with the server
        self.display = display #the Display object that will be used to show information to the user

    def show(self):
        while True:
            self.display.header("Recipe Search and Filter Menu") #this will display the menu header using the Display object
            print("  1. Search recipes by name")
            print("  2. Filter recipes by category")
            print("  3. Filter recipes by area")
            print("  4. Filter by ingredient")
            print("  5. Random recipe")
            print("  6. Back")
            choice = input("\n  Enter your choice (1-6): ").strip() #this will prompt the user to enter their choice and remove any leading/trailing whitespace

            if choice == "1":
                self.SearchByName()
            elif choice == "2":
                self.FilterByCategory()
            elif choice == "3":
                self.FilterByArea()
            elif choice == "4":
                self.FilterByIngredient()
            elif choice == "5":
                self.RandomRecipe()
            elif choice == "6":
                break
            else:
                self.display.error("Invalid choice. Please enter a number between 1 and 6.") #if the user enters an invalid choice, we use the Display object to show an error message

    def SearchByName(self):
        name = input("\n  Enter recipe name to search: ").strip() #this will prompt the user to enter a recipe name to search for and remove any leading/trailing whitespace
        if not name:
            self.display.error("Recipe name cannot be empty.") #if the user enters an empty name, we use the Display object to show an error message and return early
            return
        self.conn.send({"type": "SEARCH_BY_NAME", "params": {"keyword": name}}) #if the name is valid, we send a request to the server with the action and the name as a parameter
        response = self.conn.receive() #we then wait for a response from the server, which should contain a list of matching recipes
        if response and response.get("type") == "RECIPE_LIST":
            meals = response.get("data", []) #we extract the list of meals from the response; if there are no meals, we default to an empty list
            self.display.recipe_list(meals) #we then use the Display object to show the list of recipes to the user
            self.AskForDetail(meals) #if there are any meals in the list, we call AskForDetail to allow the user to choose one for more details

    def FilterByCategory(self):
        # show the allowed categories so the user knows what to type
        print(f"\n  Categories: {', '.join(VALID_CATEGORIES)}")
        value = input("  Enter category: ").strip().capitalize()

        # check if the user entered a valid category before sending to the server
        if value not in VALID_CATEGORIES:
            self.display.error("Invalid category.")
            return

        # send the filter request to the server with the chosen category
        self.conn.send({"type": "FILTER_CATEGORY", "params": {"value": value}})

        # wait for the server response
        response = self.conn.receive()

        # if the server returned a list of recipes, display them
        if response and response.get("type") == "RECIPE_LIST":
            meals = response.get("data", [])
            self.display.recipe_list(meals)
            self.AskForDetail(meals) # let the user pick one for full details

    def FilterByArea(self):
        # show the allowed areas so the user knows what to type
        print(f"\n  Areas: {', '.join(VALID_AREAS)}")
        value = input("  Enter area: ").strip().capitalize()

        # check if the user entered a valid area before sending to the server
        if value not in VALID_AREAS:
            self.display.error("Invalid area.")
            return

        # send the filter request to the server with the chosen area
        self.conn.send({"type": "FILTER_AREA", "params": {"value": value}})

        # wait for the server response
        response = self.conn.receive()

        # if the server returned a list of recipes, display them
        if response and response.get("type") == "RECIPE_LIST":
            meals = response.get("data", [])
            self.display.recipe_list(meals)
            self.AskForDetail(meals) # let the user pick one for full details

    def FilterByIngredient(self):
        # ask the user for an ingredient name
        value = input("  Enter ingredient: ").strip()

        # do not send empty ingredient to the server
        if not value:
            self.display.error("Ingredient cannot be empty.")
            return

        # send the filter request to the server with the ingredient
        self.conn.send({"type": "FILTER_INGREDIENT", "params": {"value": value}})

        # wait for the server response
        response = self.conn.receive()

        # if the server returned a list of recipes, display them
        if response and response.get("type") == "RECIPE_LIST":
            meals = response.get("data", [])
            self.display.recipe_list(meals)
            self.AskForDetail(meals) # let the user pick one for full details

    def RandomRecipe(self):
        # send a request to the server to get a random recipe
        self.conn.send({"type": "RANDOM_RECIPE"})

        # wait for the server response
        response = self.conn.receive()

        # if the server returned a recipe, display its full details
        if response and response.get("type") == "RECIPE_DETAIL":
            self.display.header("Random Recipe")
            self.display.recipe_detail(response.get("data"))
            self.display.pause() # wait for the user to press Enter before continuing

    def AskForDetail(self, meals):
        # if the list is empty there is nothing to select
        if not meals:
            return

        # ask the user to pick a recipe number from the list
        raw = input(f"\n  Enter number for details (1-{len(meals)}, 0=back): ").strip()

        # if the user entered 0 or nothing, go back
        if raw == "" or raw == "0":
            return

        # check if the input is a valid number within the list range
        if raw.isdigit() and 1 <= int(raw) <= len(meals):
            # get the meal ID of the chosen recipe; minus 1 because list starts at 0
            meal_id = meals[int(raw) - 1]["idMeal"]

            # send the detail request to the server with the meal ID
            self.conn.send({"type": "GET_RECIPE_DETAIL", "params": {"id": meal_id}})

            # wait for the server response
            response = self.conn.receive()

            # if the server returned the recipe details, display them
            if response and response.get("type") == "RECIPE_DETAIL":
                self.display.recipe_detail(response.get("data"))
            else:
                self.display.error("Could not get details.")

            self.display.pause() # wait for the user to press Enter before continuing
        else:
            self.display.error("Invalid number.")


class ReferenceMenu:

    def __init__(self, connection, display):
        self.conn = connection #the Connection object that will be used to communicate with the server
        self.display = display #the Display object that will be used to show information to the user

    def show(self):
        while True:
            self.display.header("Reference Lists Menu") #this will display the menu header using the Display object
            print("  1. List all categories")
            print("  2. List all areas")
            print("  3. List all ingredients")
            print("  4. Back")
            choice = input("\n  Enter your choice 1-4: ").strip() #this will prompt the user to enter their choice and remove any leading/trailing whitespace

            if choice == "1":
                self.ShowCategories() #if the user chooses option 1, we call ShowCategories to handle that functionality
            elif choice == "2":
                self.ShowAreas() #if the user chooses option 2, we call ShowAreas to handle that functionality
            elif choice == "3":
                self.ShowIngredients() #if the user chooses option 3, we call ShowIngredients to handle that functionality
            elif choice == "4":
                break
            else:
                self.display.error("Invalid choice. Please enter a number between 1 and 4.") #if the user enters an invalid choice, we use the Display object to show an error message

    def ShowCategories(self):
        self.conn.send({"type": "GET_CATEGORIES"})  # FIX 2
        response = self.conn.receive() #we then wait for a response from the server, which should contain a list of categories
        if response and response.get("type") == "CATEGORIES":
            self.display.header("Categories") #if we receive a valid response with the categories, we use the Display object to show a header for the categories list
            self.display.categories_list(response.get("data", [])) #we then use the Display object to show the list of categories to the user; if there are no categories, we default to an empty list
            self.display.pause() #wait for the user to press Enter before continuing

    def ShowAreas(self):
        self.conn.send({"type": "GET_AREAS"})  # FIX 3
        response = self.conn.receive() #we then wait for a response from the server, which should contain a list of areas
        if response and response.get("type") == "AREAS":
            self.display.header("All Areas") #if we receive a valid response with the areas, we use the Display object to show a header for the areas list
            self.display.flat_list(response.get("data", []), label="Area") #we then use the Display object to show the list of areas to the user; if there are no areas, we default to an empty list
            self.display.pause() #wait for the user to press Enter before continuing

    def ShowIngredients(self):
        self.conn.send({"type": "GET_INGREDIENTS"})  # FIX 4
        response = self.conn.receive() #we then wait for a response from the server, which should contain a list of ingredients
        if response and response.get("type") == "INGREDIENTS":
            self.display.header("All Ingredients") #if we receive a valid response with the ingredients, we use the Display object to show a header for the ingredients list
            self.display.flat_list(response.get("data", []), label="Ingredient") #we then use the Display object to show the list of ingredients to the user; if there are no ingredients, we default to an empty list
            self.display.pause() #wait for the user to press Enter before continuing


#the class used to display all the text on the screen
class Display:

    #header function used to display the menu title
    def header(self, title):
        print(LINE)
        print(f"  >> {title}")
        print(LINE)

    #the function used to dispaly the list of recipes after a search or filter; shows ID, name, and thumbnail URL
    def recipe_list(self, meals):
        #this statment will show if there is no result comming from the server after a search or filter
        if not meals:
            print("  (No results found)")
            return
        print(f"  {'No.':<4} {'ID':<8} {'Name':<30} {'Thumbnail URL'}")
        #the :<4, <8, and <30 are used to format the output in a table like structure
        print(f"  {THIN_LINE}")
        for i, meal in enumerate(meals, 1): #we added i and used the function enumerate to number the recipes in the list starting from 1
            name  = meal.get("name")      or "" #used that if there any value will write it, and if there is no value will give it a value of empty string to avoid errors
            thumb = meal.get("thumbnail") or ""
            print(f"  {i:<5} {meal.get('idMeal', ''):<10} {name:<35} {thumb}")

    def recipe_detail(self, recipe):
        if not recipe:
            print("  (No details found)") # the statment will show if there is no details comming from the server after the user select a recipe for details
            return
        #print the details of the recipe in a formatted way; if any value is missing it will show N/A instead of leaving it blank
        print(f"\n  Name        : {recipe.get('name')}")
        print(f"  Category    : {recipe.get('category')}")
        print(f"  Area        : {recipe.get('area')}")
        print(f"  Tags        : {recipe.get('tags')    or 'nothing available'}")
        print(f"  YouTube     : {recipe.get('youtube') or 'nothing available'}")
        print(f"  Source      : {recipe.get('source')  or 'nothing available'}")
        print(f"\n  Ingredients:")
        for ing in (recipe.get("ingredients") or []): #this will loop throw the ingredients list and print each ingredient; if there is no ingredients it will loop in empty list and print nothing to avoid errors
            print(f"    - {ing}")
        instructions = recipe.get("instructions") or ""
        # this loop is used to print the instructions in a formatted way; if the instructions are longer than 70 characters it will wrap it into shorter chunks to avoid long lines in the output
        for line in instructions.splitlines():
            line = line.strip()  # will remove any leading/trailing whitespace from the line
            if line:             # then will skip blank lines
                # if a line is longer than 70 characters, will cut it into shorter chunks
                while len(line) > 70:
                    print(f"    {line[:70]}")  # print first 70 characters
                    line = line[70:]            # keep the rest for the next iteration
                print(f"    {line}")

    def categories_list(self, cats): #this function is used to display the list of categories or areas for the user
        # to choose from when filtering; it takes a list of categories or areas as input
        # and prints them in a numbered format
        print(f"\n {'No.':<5} {'category':<20} description")
        print(f"  {THIN_LINE}")
        for i, cat in enumerate(cats, 1): #we added i and used the function enumerate to number the categories or areas in the list starting from 1
            name = cat.get("name") or "" #used that if there any value will write it, and if there is no value will give it a value of empty string to avoid errors
            desc = cat.get("description") or "nothing available"
            desc = desc[:55] #this will cut the description to 55 characters to avoid long lines in the output; if the description is shorter than 55 characters it will just show the full description
            print(f"  {i:<5} {name:<20} {desc}")

    def flat_list(self, items, label="Item"): #this function is used to display a simple numbered list of items with a label; it takes a list of items and a label as input and prints them in a numbered format
        print(f"\n {'No.':<5} {label}")
        print(f"  {THIN_LINE}")
        for i, item in enumerate(items, 1): #we added i and used the function enumerate to number the items in the list starting from 1
            print(f"  {i:<5} {item}") #this will print the item with the label and the number; if the item is empty it will just show the number and the label without any value

    def error(self, message): #this function is used to display error messages to the user in a consistent format
        print(f"\n  ERROR: {message}\n")

    def pause(self): #this function is used to pause the program and wait for the user to press Enter before continuing; it is used after displaying results or error messages to give the user time to read them before moving on
        input("\n  Press Enter to continue...")


if __name__ == "__main__":
    client = Client(SERVER_HOST, SERVER_PORT)
    client.run()