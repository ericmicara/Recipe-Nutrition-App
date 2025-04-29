# Recipe Finder and Nutrition App

## Overview
This application allows users to:
- Input a list of ingredients and find recipes using the Spoonacular API.
- Fetch nutritional information based on custom foods and weights using the USDA API.
- View recipe ingredient breakdowns, costs, and nutrition facts interactively through a custom Tkinter GUI.

Built as a final project for a coding course at Binghamton University.

## Features
- Ingredient-based recipe search.
- Nutritional facts retrieval per custom ingredients (calories, protein, carbs, fat, fiber, calcium).
- Interactive and scrollable graphical user interface (GUI) built with Tkinter.
- Automation of web scraping to fetch additional recipe data using Selenium.

## Technologies Used
- Python 3.10+
- Tkinter (GUI Development)
- Requests (API Requests)
- Selenium (Web Scraping Automation)
- USDA Food Data Central API
- Spoonacular Recipe API

## Project Structure
- `/src/presentation.py` — Main executable file to launch the application.
- `/notebooks/Presentation.ipynb` — Full project development code and logic.
- `/screenshots/` — Example screenshots of the working application.

## Installation Instructions
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/Recipe-Finder-App.git
   cd Recipe-Finder-App