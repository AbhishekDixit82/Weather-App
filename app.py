from flask import Flask, render_template, request
import requests
from datetime import datetime, timedelta, timezone

app = Flask(__name__)
API_KEY = "5284389a69ae373601c01507be92a9e0"
BASE_URL = "http://api.openweathermap.org/data/2.5/weather"
FORECAST_URL = "http://api.openweathermap.org/data/2.5/forecast"

def get_weather_data(city):
    weather_params = {"q": city, "appid": API_KEY, "units": "metric"}
    response = requests.get(BASE_URL, params=weather_params)
    weather_data = response.json()
    
    if weather_data.get("cod") != 200:
        return None, f"Error: {weather_data.get('message', 'Invalid city name')}"
    
    timezone_offset = weather_data["timezone"]
    local_time = datetime.fromtimestamp(weather_data["dt"], tz=timezone.utc) + timedelta(seconds=timezone_offset)
    
    current_weather = {
        "city": weather_data["name"],
        "local_time": local_time.strftime('%Y-%m-%d %H:%M:%S'),
        "temperature": weather_data["main"]["temp"],
        "weather": weather_data["weather"][0]["description"].capitalize()
    }
    
    forecast_params = {"q": city, "appid": API_KEY, "units": "metric", "cnt": 40}
    forecast_response = requests.get(FORECAST_URL, params=forecast_params)
    forecast_data = forecast_response.json()
    
    forecast_list = []
    for forecast in forecast_data["list"]:
        timestamp = datetime.fromtimestamp(forecast["dt"], tz=timezone.utc) + timedelta(seconds=timezone_offset)
        forecast_list.append({
            "time": timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            "temperature": forecast["main"]["temp"],
            "weather": forecast["weather"][0]["description"].capitalize()
        })
    
    return current_weather, forecast_list

@app.route("/", methods=["GET", "POST"])  # ✅ Fixed Route
def index():
    weather = None
    forecast = None
    error = None
    if request.method == "POST":
        city = request.form["city"]
        weather, forecast = get_weather_data(city)
        if not weather:
            error = forecast
    
    return render_template("index.html", weather=weather, forecast=forecast, error=error)

if __name__ == "__main__":
    app.run(debug=True)