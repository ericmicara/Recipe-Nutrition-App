# ===== Imports =====
import os
import time
import requests
import json
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from dotenv import load_dotenv

# ===== Load Environment Variables =====
load_dotenv()
SPOONACULAR_API_KEY = os.getenv('SPOONACULAR_API_KEY')
USDA_API_KEY = os.getenv('USDA_API_KEY')

# ===== Selenium Browser Options =====
browser_options = Options()
browser_options.add_argument('--headless=new')

# ===== Tkinter App Setup =====
root = tk.Tk()
root.geometry("1300x900")
root.title("Recipe Finder and Nutrition Analyzer")
root.configure(background="#f0f0f0")

frame = ttk.Frame(root)
frame.grid(row=0, column=0, rowspan=4, columnspan=4, sticky="nsew")

canvas = tk.Canvas(frame, background="#f0f0f0")
scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
content_frame = ttk.Frame(canvas)

def on_frame_configure(event):
    canvas.configure(scrollregion=canvas.bbox("all"))

content_frame.bind("<Configure>", on_frame_configure)

canvas.create_window((0, 0), window=content_frame, anchor="nw", width=1200)
canvas.configure(yscrollcommand=scrollbar.set)

canvas.grid(row=0, column=0, sticky="nsew")
scrollbar.grid(row=0, column=1, sticky="ns")

root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)
frame.columnconfigure(0, weight=1)
frame.rowconfigure(0, weight=1)

def _on_mousewheel(event):
    canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

canvas.bind_all("<MouseWheel>", _on_mousewheel)

# ===== Global Variables =====
recipe_have_foods = []
conversion_factors = []
wide_search_input = []
Single_Nutrition_Input = []
wide_search_index = 0

calorie_t = []
protein_t = []
fat_t = []
Carbs_t = []
Fiber_t = []
Calci_t = []

clicked = tk.StringVar()

def apply_theme():
    root.configure(background=current_theme["bg"])
    frame.configure(style="TFrame")
    canvas.configure(background=current_theme["bg"])
    content_frame.configure(style="TFrame")

def style_widget(widget):
    if isinstance(widget, (tk.Label, ttk.Label)):
        widget.configure(bg=current_theme["bg"], fg=current_theme["fg"])
    elif isinstance(widget, (tk.Button, ttk.Button)):
        widget.configure(bg=current_theme["button_bg"], fg=current_theme["fg"])
    elif isinstance(widget, (tk.Entry, ttk.Entry)):
        widget.configure(bg=current_theme["entry_bg"], fg=current_theme["fg"], insertbackground=current_theme["fg"])
    elif isinstance(widget, (tk.Text, scrolledtext.ScrolledText)):
        widget.configure(bg=current_theme["text_bg"], fg=current_theme["fg"], insertbackground=current_theme["fg"])
    elif isinstance(widget, tk.Frame):
        widget.configure(bg=current_theme["bg"])
        for child in widget.winfo_children():
            style_widget(child)

# ===== Theme Colors =====
current_theme = {
    "bg": "#f7f7f7",         # soft light grey background
    "fg": "#222222",         # dark gray text (easier on eyes)
    "button_bg": "#4CAF50",  # soft green buttons (professional look)
    "entry_bg": "#ffffff",   # pure white entries
    "text_bg": "#ffffff"     # pure white text boxes
}

# ===== Frames and Layout =====

# Top Introduction Section
intro_frame = tk.Frame(content_frame, bg=current_theme["bg"])
intro_frame.pack(fill="x", pady=10)

intro_label = tk.Label(
    intro_frame,
    text="Recipe Finder and Nutrition Analyzer",
    font=("Segoe UI", 24, "bold"),
    bg=current_theme["bg"],
    fg=current_theme["fg"]
)
intro_label.pack(pady=(10, 0))

intro_subtitle = tk.Label(
    intro_frame,
    text="Input ingredients or build your own custom meal and analyze nutrition facts.",
    font=("Segoe UI", 14),
    bg=current_theme["bg"],
    fg=current_theme["fg"]
)
intro_subtitle.pack(pady=(0, 10))

# ===== Center Frame (NEW!) =====
center_frame = tk.Frame(content_frame, bg=current_theme["bg"])
center_frame.pack(pady=10)

# ===== Left: Find Recipes Section =====
recipe_frame = tk.Frame(center_frame, bg=current_theme["bg"], bd=2, relief="groove")
recipe_frame.pack(side="left", padx=20, pady=10)

recipe_title = tk.Label(
    recipe_frame,
    text="Find Recipes by Ingredients",
    font=("Segoe UI", 16, "bold"),
    bg=current_theme["bg"],
    fg=current_theme["fg"]
)
recipe_title.pack(pady=10)

instructions_label = tk.Label(
    recipe_frame,
    text="Separate ingredients by commas",
    font=("Segoe UI", 10, "italic"),
    bg=current_theme["bg"],
    fg=current_theme["fg"]
)
instructions_label.pack(pady=(0, 5))

entry = tk.Entry(recipe_frame, width=40, font=("Segoe UI", 12))
entry.pack(pady=(0, 10))

fetch_button = tk.Button(
    recipe_frame,
    text="Fetch Recipes",
    command=lambda: display_recipes(),
    font=("Segoe UI", 12, "bold"),
    bg=current_theme["button_bg"],
    fg="white"
)
fetch_button.pack(pady=(0, 10))

output_text = scrolledtext.ScrolledText(recipe_frame, width=50, height=20, wrap=tk.WORD, font=("Segoe UI", 11))
output_text.pack(padx=10, pady=10)

# ===== Middle: Build Your Own Meal Section =====
custom_frame = tk.Frame(center_frame, bg=current_theme["bg"], bd=2, relief="groove")
custom_frame.pack(side="left", padx=20, pady=10)

custom_title = tk.Label(
    custom_frame,
    text="Build Your Own Meal",
    font=("Segoe UI", 16, "bold"),
    bg=current_theme["bg"],
    fg=current_theme["fg"]
)
custom_title.pack(pady=10)

f_label = tk.Label(custom_frame, text="Enter Food Name:", font=("Segoe UI", 12), bg=current_theme["bg"], fg=current_theme["fg"])
f_label.pack()
F_Entry = tk.Entry(custom_frame, font=("Segoe UI", 12))
F_Entry.pack(pady=(0, 10))

g_label = tk.Label(custom_frame, text="Enter Weight in Grams:", font=("Segoe UI", 12), bg=current_theme["bg"], fg=current_theme["fg"])
g_label.pack()
G_Entry = tk.Entry(custom_frame, font=("Segoe UI", 12))
G_Entry.pack(pady=(0, 10))

select_button = tk.Button(
    custom_frame,
    text="Add Ingredient",
    command=lambda: Recipe_Maker(recipe_have_foods),
    font=("Segoe UI", 12, "bold"),
    bg=current_theme["button_bg"],
    fg="white"
)
select_button.pack(pady=(0, 10))

get_nutrition_button = tk.Button(
    custom_frame,
    text="Get Nutrition Info",
    command=lambda: run_conversion_and_wide(recipe_have_foods, wide_search_input, wide_search_index),
    font=("Segoe UI", 12, "bold"),
    bg=current_theme["button_bg"],
    fg="white"
)
get_nutrition_button.pack(pady=(0, 10))

Get_Nutrients_Text = tk.Text(custom_frame, width=40, height=3, wrap=tk.WORD, font=("Segoe UI", 11))
Get_Nutrients_Text.pack(pady=5)

# ===== Right: Nutrition Summary Section =====
summary_frame = tk.Frame(center_frame, bg=current_theme["bg"], bd=2, relief="groove")
summary_frame.pack(side="left", padx=20, pady=10)

summary_title = tk.Label(
    summary_frame,
    text="Nutrition Summary",
    font=("Segoe UI", 16, "bold"),
    bg=current_theme["bg"],
    fg=current_theme["fg"]
)
summary_title.pack(pady=10)

nut_text = tk.Text(summary_frame, font=("Segoe UI", 12), height=10, width=30)
nut_text.pack(pady=10)

recipeT = tk.Text(summary_frame, font=("Segoe UI", 12), height=10, width=30)
recipeT.pack(pady=10)

reset_button = tk.Button(
    summary_frame,
    text="Reset",
    command=lambda: Recipe_Maker_Reset(recipe_have_foods, conversion_factors, wide_search_input, Single_Nutrition_Input, wide_search_index),
    font=("Segoe UI", 12, "bold"),
    bg=current_theme["button_bg"],
    fg="white"
)
reset_button.pack(pady=10)

# ===== Core Functions =====

def Recipe_Maker(recipe_have_foods):
    fname = F_Entry.get()
    gnum = G_Entry.get()

    if not fname or not gnum:
        messagebox.showwarning("Missing Input", "Please enter both a food name and a weight!")
        return

    try:
        gnum = int(gnum)
        recipe_have_foods.append({fname: gnum})
        Get_Nutrients_Text.insert(tk.END, fname + ", ")
    except ValueError:
        messagebox.showerror("Value Error", "Weight must be an integer.")

    F_Entry.delete(0, tk.END)
    G_Entry.delete(0, tk.END)

def run_conversion_and_wide(recipe_have_foods, wide_search_input, wide_search_index):
    conversion(recipe_have_foods)
    wide_search(wide_search_input, wide_search_index)

def conversion(recipe_have_foods):
    for pair in recipe_have_foods:
        for key, value in pair.items():
            if isinstance(value, int):
                wide_search_input.append(key)
                conversion_factors.append(value / 100)
            else:
                wide_search_input.append(key)
                conversion_factors.append(0.1)

def wide_search(wide_search_input, wide_search_index):
    if wide_search_index >= len(wide_search_input):
        recipe_total()
        return

    try:
        USDA_response = requests.get(f"https://api.nal.usda.gov/fdc/v1/foods/search?api_key={USDA_API_KEY}&query={wide_search_input[wide_search_index]}&dataType=SR Legacy")
        USDA_response.raise_for_status()
        USDA_json = USDA_response.json()
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Error", f"Failed to search USDA database: {e}")
        return

    selection(USDA_json, wide_search_input, wide_search_index)

def selection(USDA_json, wide_search_input, wide_search_index):
    food_choices = USDA_json.get("foods", [])[:10]
    choice_list = [i["description"] for i in food_choices]
    ID_list = [i["fdcId"] for i in food_choices]
    food_and_id = dict(zip(choice_list, ID_list))

    if not choice_list:
        messagebox.showwarning("Warning", "No foods found for your input.")
        return

    selected_food = tk.StringVar()
    selected_food.set(choice_list[0])

    dropdown = tk.OptionMenu(content_frame, selected_food, *choice_list)
    dropdown.pack(pady=10)


    def Choice_Swapper():
        choice = selected_food.get()
        Single_Nutrition_Input.append(food_and_id[choice])
        dropdown.destroy()
        choose_button.destroy()
        food_search_narrow(Single_Nutrition_Input)
        wide_search(wide_search_input, wide_search_index + 1)

    choose_button = tk.Button(content_frame, text="Select", command=Choice_Swapper)
    choose_button.pack(pady=10)

def food_search_narrow(Single_Nutrition_Input):
    if not Single_Nutrition_Input:
        return

    f_ID = Single_Nutrition_Input.pop(0)

    try:
        USDA_response = requests.get(f"https://api.nal.usda.gov/fdc/v1/food/{f_ID}?api_key={USDA_API_KEY}")
        USDA_response.raise_for_status()
        USDA_json = USDA_response.json()
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Error", f"Failed to fetch nutrition data: {e}")
        return

    nutrition(USDA_json)

def nutrition(USDA_json):
    if nut_text is None:
        return

    nut_text.delete("1.0", "end")
    nutrients = USDA_json.get("foodNutrients", [])

    # Extract and calculate values
    try:
        calories = next(n for n in nutrients if n["nutrient"]["name"] == "Energy")["amount"]
        protein = next(n for n in nutrients if n["nutrient"]["name"] == "Protein")["amount"]
        fat = next(n for n in nutrients if n["nutrient"]["name"] == "Total lipid (fat)")["amount"]
        carbs = next(n for n in nutrients if n["nutrient"]["name"] == "Carbohydrate, by difference")["amount"]
        fiber = next((n["amount"] for n in nutrients if n["nutrient"]["name"] == "Fiber, total dietary"), 0)
        calcium = next((n["amount"] for n in nutrients if n["nutrient"]["name"] == "Calcium, Ca"), 0)
    except StopIteration:
        messagebox.showwarning("Warning", "Incomplete nutrition info.")
        return

    # Insert into Text widget
    nut_text.insert(tk.END, f"Calories: {round(calories * conversion_factors[0], 2)} kcal\n")
    nut_text.insert(tk.END, f"Protein: {round(protein * conversion_factors[0], 2)} g\n")
    nut_text.insert(tk.END, f"Fat: {round(fat * conversion_factors[0], 2)} g\n")
    nut_text.insert(tk.END, f"Carbs: {round(carbs * conversion_factors[0], 2)} g\n")
    nut_text.insert(tk.END, f"Fiber: {round(fiber * conversion_factors[0], 2)} g\n")
    nut_text.insert(tk.END, f"Calcium: {round(calcium * conversion_factors[0], 2)} mg\n")

    # Store totals
    calorie_t.append(calories * conversion_factors[0])
    protein_t.append(protein * conversion_factors[0])
    fat_t.append(fat * conversion_factors[0])
    Carbs_t.append(carbs * conversion_factors[0])
    Fiber_t.append(fiber * conversion_factors[0])
    Calci_t.append(calcium * conversion_factors[0])

    conversion_factors.pop(0)

def recipe_total():
    recipeT.delete("1.0", "end")
    recipeT.insert(tk.END, f"Calories: {round(sum(calorie_t), 2)} kcal\n")
    recipeT.insert(tk.END, f"Protein: {round(sum(protein_t), 2)} g\n")
    recipeT.insert(tk.END, f"Fat: {round(sum(fat_t), 2)} g\n")
    recipeT.insert(tk.END, f"Carbs: {round(sum(Carbs_t), 2)} g\n")
    recipeT.insert(tk.END, f"Fiber: {round(sum(Fiber_t), 2)} g\n")
    recipeT.insert(tk.END, f"Calcium: {round(sum(Calci_t), 2)} mg\n")
    
def Recipe_Maker_Reset(recipe_have_foods, conversion_factors, wide_search_input, Single_Nutrition_Input, wide_search_index):
    recipe_have_foods.clear()
    conversion_factors.clear()
    wide_search_input.clear()
    Single_Nutrition_Input.clear()
    wide_search_index = 0

    Get_Nutrients_Text.delete("1.0", tk.END)
    nut_text.delete("1.0", tk.END)
    recipeT.delete("1.0", tk.END)
    output_text.delete("1.0", tk.END)

    return recipe_have_foods, conversion_factors, wide_search_input, Single_Nutrition_Input, wide_search_index
    
# ===== Recipe Finding and Scraping =====

missed_dict = {}
nutrientDict = {}
choices = []

def display_recipes():
    food_list = entry.get().split(",")

    if not food_list:
        messagebox.showwarning("Warning", "Please enter at least one ingredient!")
        return

    recipe_urls = fetch_recipe_data(food_list)
    recipe_list = scrape_recipe_details(recipe_urls)

    output_text.delete(1.0, tk.END)

    for recipe in recipe_list:
        output_text.insert(tk.END, f"{recipe['name']}:\n")
        for ingredient, measure in recipe['ingredients'].items():
            output_text.insert(tk.END, f"- {ingredient}: {measure}\n")
        output_text.insert(tk.END, f"Ingredients Missing: {missed_dict.get(recipe['name'], [])}\n")
        output_text.insert(tk.END, f"Price: {recipe['price']}\n")
        output_text.insert(tk.END, "\n--------------------------\n")

    more_recipe()

def fetch_recipe_data(food_list):
    sep = ',+'
    food = sep.join(food_list)
    url = f"https://api.spoonacular.com/recipes/findByIngredients?ingredients={food}&number=2&apiKey={SPOONACULAR_API_KEY}"

    try:
        response = requests.get(url)
        response.raise_for_status()
        json_file = response.json()
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Error", f"Failed to fetch recipes: {e}")
        return []

    url_list = []
    global missed_dict
    missed_dict = {}

    for item in json_file:
        id = item["id"]
        price_url = f"https://api.spoonacular.com/recipes/{id}/information?apiKey={SPOONACULAR_API_KEY}"

        try:
            price_response = requests.get(price_url)
            price_response.raise_for_status()
            price_data = price_response.json()
            url_list.append(price_data["spoonacularSourceUrl"])
        except requests.exceptions.RequestException:
            continue

        missed_ingredients = [i["name"] for i in item.get("missedIngredients", [])]
        missed_dict[item["title"]] = missed_ingredients

    return url_list

def scrape_recipe_details(recipe_urls):
    recipe_list = []
    global nutrientDict
    nutrientDict = {}
    global choices
    choices = []

    driver = webdriver.Chrome(options=browser_options)

    try:
        for url in recipe_urls:
            driver.get(url)
            time.sleep(1)

            try:
                WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, "spoonacular-metric")))
                metric_button = driver.find_element(By.XPATH, "//*[@id='spoonacularMeasure']/label[1]")
                metric_button.click()

                WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.stepper-wrap")))
                serving_input = driver.find_element(By.XPATH, "//*[@id='spoonacular-serving-stepper']")
                serving_input.clear()
                serving_input.send_keys("0" + Keys.ENTER)
            except Exception:
                pass

            measures = []
            ingredients = []
            price = []
            nutrientName = []
            nutrientValue = []

            try:
                for element in driver.find_elements(By.CSS_SELECTOR, "div.spoonacular-ingredient"):
                    measure = element.find_element(By.CSS_SELECTOR, "div.spoonacular-amount.t12.spoonacular-metric").text
                    measures.append(measure)

                for idx, element in enumerate(driver.find_elements(By.CSS_SELECTOR, "div.spoonacular-image-wrapper"), start=1):
                    try:
                        ingredient = driver.find_element(By.XPATH, f'//*[@id=\"spoonacular-ingredient-vis-grid\"]/div[{idx}]/div/div[4]').text
                        ingredients.append(ingredient)
                    except NoSuchElementException:
                        break

                recipe_name = driver.find_element(By.XPATH, '//*[@id="wrapper"]/div/div[3]/h1').text
            except Exception:
                recipe_name = "Unknown Recipe"

            try:
                for element in driver.find_elements(By.CSS_SELECTOR, "div.spoonacular-nutrient-name"):
                    nutrientName.append(element.text)
                for element in driver.find_elements(By.CSS_SELECTOR, "div.spoonacular-nutrient-value"):
                    nutrientValue.append(element.text)
            except Exception:
                pass

            try:
                for element in driver.find_elements(By.ID, "spoonacularPriceBreakdownTable"):
                    prices = element.find_element(By.CSS_SELECTOR, "div.spoonacular-quickview").text
                    price.append(prices)
            except Exception:
                pass

            recipe_details = {
                "name": recipe_name,
                "ingredients": dict(zip(ingredients, measures)),
                "price": price
            }

            nutrientDictItems = {
                "Calories": nutrientValue[nutrientName.index("Calories")] if "Calories" in nutrientName else "N/A",
                "Protein": nutrientValue[nutrientName.index("Protein")] if "Protein" in nutrientName else "N/A",
                "Fat": nutrientValue[nutrientName.index("Fat")] if "Fat" in nutrientName else "N/A",
                "Carbs": nutrientValue[nutrientName.index("Carbohydrates")] if "Carbohydrates" in nutrientName else "N/A",
                "Fiber": nutrientValue[nutrientName.index("Fiber")] if "Fiber" in nutrientName else "N/A",
                "Calcium": nutrientValue[nutrientName.index("Calcium")] if "Calcium" in nutrientName else "N/A"
            }

            nutrientDict[recipe_name] = nutrientDictItems
            recipe_list.append(recipe_details)
            choices.append(recipe_name)
    finally:
        driver.quit()

    return recipe_list

def insert_nutrition():
    pick = nutrientDict.get(clicked.get())
    More_Spoonacular_text.delete(1.0, tk.END)

    if not pick:
        More_Spoonacular_text.insert(tk.END, "No nutrition information available.")
    else:
        for key, value in pick.items():
            More_Spoonacular_text.insert(tk.END, f"{key}: {value}\n")

def more_recipe():
    More_Spoonacular_Frame = tk.Frame(content_frame, background=current_theme["bg"])
    More_Spoonacular_Frame.pack(pady=10)

    More_Spoonacular_Label = tk.Label(More_Spoonacular_Frame, text="Choose a Recipe for Nutrition Info", font=("Arial", 18), bg=current_theme["bg"], fg=current_theme["fg"])
    More_Spoonacular_Label.pack(pady=10)

    clicked.set("Choose a Recipe")
    dropp = tk.OptionMenu(More_Spoonacular_Frame, clicked, *choices)
    dropp.pack()

    global More_Spoonacular_text
    More_Spoonacular_text = scrolledtext.ScrolledText(More_Spoonacular_Frame, width=60, height=10, wrap=tk.WORD)
    More_Spoonacular_text.pack(padx=10, pady=10)

    fetch_nutrition_button = tk.Button(More_Spoonacular_Frame, text="Fetch Nutrition", command=insert_nutrition, font=("Arial", 14))
    fetch_nutrition_button.pack(pady=5)

apply_theme()
root.mainloop()