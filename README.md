# Real-Time Weather Application

Unit-3 Django Practical Project  
Student: Niraj Patel  
Course: B.Tech CSE / IT (Practical Assignment)  
Live Demo: [nirajpatel2278.pythonanywhere.com](https://nirajpatel2278.pythonanywhere.com)

---

## Project Overview

This is a real-time weather forecasting web application built using Django. It connects with the **OpenWeatherMap API** suite to fetch and display live weather conditions, geocoding autocomplete, air quality indices, and multi-day forecasts through a clean web interface.  
Reference: [OpenWeatherMap API Documentation](https://openweathermap.org/api)

---

## Features

* **City Search & Autocomplete:** Search for any city worldwide with instant geocoding suggestions.
* **Current Location Weather:** Automatically detects and displays weather data based on device GPS coordinates.
* **Comprehensive Forecasts:**
  * Current temperature, humidity, wind speed, and weather descriptions.
  * Hourly weather progression breakdown.
  * 10-day daily temperature range bar charts.
* **Environmental & Astronomical Data:**
  * Air Quality Index (AQI) levels.
  * Precise local sunrise and sunset timings.
* **Quick Access & History:** Save pinned favorite locations and view recent searches using Django session storage.

---

## Technologies Used

* Python
* Django
* OpenWeatherMap API
* SQLite
* HTML
* CSS
* JavaScript
* PythonAnywhere (Hosting)

---

## Project Structure

```text
weather-app/
├── manage.py
├── requirements.txt
├── README.md
├── .gitignore
├── weather/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── wapp/
    ├── admin.py
    ├── apps.py
    ├── models.py
    ├── urls.py
    ├── views.py
    ├── static/
    │   └── wapp/
    └── templates/
        └── wapp/
            └── index.html
