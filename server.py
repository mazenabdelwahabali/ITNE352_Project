import socket
import json
import sys
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime


host = "127.0.0.1"
port = 5000

valid_categories = ["Beef","Chiken","Seafood","Vegetarian","Dessert","Pasta","Breakfast"]

valid_areas = ["Italian","Indian","Mexican","Japanese","Moroccan","British","American","Thai"]

# These are just for making the menus and result look nice on screen.

line = "-" * 60 # A thick line (60 dashes) for section titles.

thin_line = "." * 60 # A thin line (60 dots) to separator rows.

# Class: Display 
# This class handles all the text you see on the secreen. By keeping all print commands here,
# the rest of the code stays neat, and if we ever want to change how things look, we only have
# to edit this one.

class Display: 
    def header(self,title):
        print(f"\n{line}")
        print(f"  >> {title}")
        print(line)

def recipe_list(self, meals):
    """"
    This print out a numbered table of recipe summaries.
    if the server doesn't find any result, it'll tell
    the user that. Otherwise, you'll see a fromatted
    table with each recipe's ID,name,and a link to
    the thumbnail picture. The number on the left 
    is what the user use to pick a recipe to see
    its full deatils.

    """

    # If the server returend no reaults, tell the user

    if not meals :
        print("  (No results found)")
        return
    
    # Print the column headers

    print(f"\n  {"No.":<5} {"Meal ID":<10} {"Recipe Name":<35} Thumbnail URL" )
    print(f"  {thin_line}")

# We start numbering from 1 so its easier to choose.

for i, meal in enumerate(meals, 1):
    name = (meal.get("name")   or"")[:33]
    thumb = (meal.get("thumbnail")  or"")[:44]
    print(f"  {i<5} {meal.get("idMeal", ""):<10} {name:<35} {thumb}")

def recipe_detail(self, recipe):
    """

    """

    if not recipe:
        print("  (No details available)")
        return
    
    print(f"\n Name       : {recipe.get("name")}")
    print(f" Category   : {recipe.get("category")}")
    print(f" Area       : {recipe.get("area")}")
    print(f" Tags       : {recipe.get("tags")    or "N/A"}")
    print(f" YouTube    : {recipe.get("youtube") or "N/A"}")
    print(f" Source     : {recipe.get("source")  or "N/A"}")

    print(f"\n Ingredients :")
    for ing in (recipe.get("ingredients") or {}):
        print(f"   - {ing}")

        print(f"\n  Instructions:") or ""
        instructions = recipe.get("instuctions") or ""

        for line in instructions.splitlines():
            line = line.strip()
            if line:
                while len(line) > 70:
                    print(f"   {linr [:70]}")
                    line = line [70:]
                print(f"   {line}")

def categories_list(sefl, cats):
    """

    """
    print(f"\n  {"No":<5} {"Category":<20} Description")
    print(f"  {thin_line}")
    for i, cat in enumerate(cats, 1):
        name = cat.get("name", "")
        desc = (cat.get("decription") or "").replace("\r", "").replace("\n", " ")

        desc = desc[:55]
        print(f"  {i:<5} {name:<20} {desc}")


def error(se)