import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import requests
from io import BytesIO
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import datetime

class WeatherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🌤 Weather App with Auto-Detect & Chart")
        self.root.geometry("600x650")
        self.root.resizable(False, False)

        self.api_key = "46d6a24bf5aa38dc4995a4ca08881b88"
        self.search_history = []

        tk.Label(root, text="Enter City Name:", font=("Arial", 12)).pack(pady=10)
        self.city_entry = tk.Entry(root, font=("Arial", 12), width=30)
        self.city_entry.pack()

        button_frame = tk.Frame(root)
        button_frame.pack(pady=10)

        tk.Button(button_frame, text="🔍 Get Weather", font=("Arial", 12), command=self.fetch_weather).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="📍 Use My Location", font=("Arial", 12), command=self.auto_detect_city).pack(side=tk.LEFT, padx=5)

        self.icon_label = tk.Label(root)
        self.icon_label.pack()

        self.result_label = tk.Label(root, text="", font=("Arial", 11), justify="left")
        self.result_label.pack(pady=10)

        self.history_label = tk.Label(root, text="🕘 Recent Searches:", font=("Arial", 10, "bold"))
        self.history_label.pack()
        self.history_box = tk.Label(root, text="", font=("Arial", 10), justify="left")
        self.history_box.pack()

        self.chart_frame = tk.Frame(root)
        self.chart_frame.pack(pady=10)

    def auto_detect_city(self):
        try:
            ipinfo = requests.get("https://ipinfo.io/json").json()
            city = ipinfo.get("city")
            if city:
                self.city_entry.delete(0, tk.END)
                self.city_entry.insert(0, city)
                self.fetch_weather()
            else:
                messagebox.showerror("Error", "Could not detect city.")
        except Exception as e:
            messagebox.showerror("Error", f"Auto-detect failed:\n{e}")

    def fetch_weather(self):
        city = self.city_entry.get().strip()
        if not city:
            messagebox.showwarning("Input Error", "Please enter a city name.")
            return

        try:
            # Current weather
            url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={self.api_key}&units=metric"
            response = requests.get(url)
            data = response.json()

            if data.get("cod") != 200:
                messagebox.showerror("Error", f"City not found: {city}")
                return

            weather = data["weather"][0]["description"].title()
            temp = data["main"]["temp"]
            feels_like = data["main"]["feels_like"]
            humidity = data["main"]["humidity"]
            wind = data["wind"]["speed"]
            country = data["sys"]["country"]
            icon_code = data["weather"][0]["icon"]
            lat = data["coord"]["lat"]
            lon = data["coord"]["lon"]

            # Fetch and display icon
            icon_url = f"http://openweathermap.org/img/wn/{icon_code}@2x.png"
            icon_response = requests.get(icon_url)
            img_data = Image.open(BytesIO(icon_response.content))
            img = ImageTk.PhotoImage(img_data)
            self.icon_label.config(image=img)
            self.icon_label.image = img

            # Display weather
            output = f"""
📍 {city.title()}, {country}
🌡 {temp}°C (Feels like {feels_like}°C)
🌤 {weather}
💧 Humidity: {humidity}%
💨 Wind: {wind} m/s
            """.strip()
            self.result_label.config(text=output)

            # Update history
            if city.title() not in self.search_history:
                self.search_history.insert(0, city.title())
                self.search_history = self.search_history[:5]
                self.update_history_display()

            # Fetch and show temperature chart
            self.plot_temperature_chart(lat, lon)

        except Exception as e:
            messagebox.showerror("Error", f"Something went wrong:\n{e}")

    def plot_temperature_chart(self, lat, lon):
        try:
            today = datetime.date.today()
            temps = []
            dates = []

            for i in range(5):
                date = today - datetime.timedelta(days=i)
                timestamp = int(datetime.datetime.combine(date, datetime.datetime.min.time()).timestamp())
                url = f"https://api.openweathermap.org/data/2.5/onecall/timemachine?lat={lat}&lon={lon}&dt={timestamp}&appid={self.api_key}&units=metric"
                response = requests.get(url)
                data = response.json()

                if "current" in data:
                    temp = data["current"]["temp"]
                    temps.append(temp)
                    dates.append(date.strftime("%b %d"))

            temps.reverse()
            dates.reverse()

            for widget in self.chart_frame.winfo_children():
                widget.destroy()

            fig, ax = plt.subplots(figsize=(5, 3), dpi=100)
            ax.plot(dates, temps, marker='o')
            ax.set_title("Last 5 Days Temp (°C)")
            ax.set_ylabel("Temperature")
            ax.grid(True)

            canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack()

        except Exception as e:
            messagebox.showerror("Chart Error", f"Failed to load chart:\n{e}")

    def update_history_display(self):
        self.history_box.config(text="\n".join(self.search_history))


# Run the App
if __name__ == "__main__":
    root = tk.Tk()
    WeatherApp(root)
    root.mainloop()
