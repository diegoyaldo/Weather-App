import tkinter as tk
from tkinter import messagebox, font
from PIL import Image, ImageTk
import python_weather
from python_weather.enums import Kind
import asyncio
import geocoder
from timezonefinder import TimezoneFinder
from datetime import datetime
import pytz
import os

if os.name == 'nt':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

async def fetch_weather_and_display(city_name=None):
    try:
        if not city_name:
            g = geocoder.ip('me')
            city_name = g.city
            city_entry.insert(0, city_name)
        else:
            g = geocoder.osm(city_name)
            #Using OpenStreetMap provider, which can at times be inaccurate

        if not g.ok:
            raise ValueError("Failed to geocode city")

        tz_finder = TimezoneFinder()
        local_timezone = tz_finder.timezone_at(lat=g.lat, lng=g.lng)
        timezone = pytz.timezone(local_timezone)
        local_time = datetime.now(timezone).strftime("%H:%M:%S")
        canvas.itemconfigure(local_time_text, text=f"Local Time: {local_time}")
        
        async with python_weather.Client(unit=python_weather.METRIC) as client:
            weather = await client.get(city_name)
            update_weather_display(weather)

    except Exception as e:
        messagebox.showerror("Error", str(e))

def update_weather_display(weather):
    temperature = f"Temperature: {weather.temperature}°C"
    forecast_text = "Weekly Forecast:\n" + "\n".join(f"{daily.date}: {daily.temperature}°C" for daily in weather.daily_forecasts)
    canvas.itemconfigure(temp_text, text=temperature)
    canvas.itemconfigure(forecast_text_item, text=forecast_text)
    update_background(get_background(weather))

def get_background(weather):
    kind_map = {
        Kind.HEAVY_SNOW: "assets/snow.gif",
        Kind.LIGHT_SNOW: "assets/snow.gif",
        Kind.HEAVY_SNOW_SHOWERS: "assets/snow.gif",
        Kind.LIGHT_SNOW_SHOWERS: "assets/snow.gif",
        Kind.THUNDERY_HEAVY_RAIN: "assets/thunder.gif",
        Kind.THUNDERY_SHOWERS: "assets/thunder.gif",
        Kind.CLOUDY: "assets/cloud.gif",
        Kind.PARTLY_CLOUDY: "assets/cloud.gif",
        Kind.VERY_CLOUDY: "assets/cloud.gif",
        Kind.SUNNY: "assets/sun.gif",
    }
    return kind_map.get(weather.kind, "assets/sun.gif")

def update_background(image_path):
    global bg_image
    img = Image.open(image_path)
    img = img.resize((800, 600), Image.Resampling.LANCZOS)
    bg_image = ImageTk.PhotoImage(img)
    canvas.itemconfig(bg, image=bg_image)

def on_search():
    city_name = city_entry.get().strip()
    if city_name:
        city_entry.delete(0, tk.END)
        city_entry.insert(0, city_name)
        asyncio.run(fetch_weather_and_display(city_name))
    elif not city_name:
        asyncio.run(fetch_weather_and_display())
        
root = tk.Tk()
root.title("Weather App")
root.geometry("800x600")
root.resizable(False, False)

canvas = tk.Canvas(root)
canvas.pack(fill="both", expand=True)

bg = canvas.create_image(0, 0, anchor="nw")
large_font = font.Font(size=16)
local_time_text = canvas.create_text(400, 250, anchor="center", font=large_font, fill="black")
temp_text = canvas.create_text(400, 300, anchor="center", font=large_font, fill="black")
forecast_text_item = canvas.create_text(400, 400, anchor="center", font=large_font, fill="black", width=780)

city_entry = tk.Entry(root, font=large_font)
search_button = tk.Button(root, text="Search", command=on_search, font=large_font)
entry_window = canvas.create_window(400 - city_entry.winfo_reqwidth() / 2, 10, anchor="nw", window=city_entry)
button_window = canvas.create_window(400 - search_button.winfo_reqwidth() / 2, 60, anchor="nw", window=search_button)

asyncio.run(fetch_weather_and_display())
root.mainloop()