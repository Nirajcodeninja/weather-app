import requests
from datetime import datetime, timezone, timedelta
from django.shortcuts import render, redirect
from django.http import JsonResponse

API_KEY = '6d749ae876837f56461127e4ff3fcc9c'  # Your OpenWeatherMap API key

def get_weather_emoji(icon_code):
    mapping = {
        '01d': '☀️', '01n': '🌙',
        '02d': '⛅', '02n': '☁️',
        '03d': '☁️', '03n': '☁️',
        '04d': '☁️', '04n': '☁️',
        '09d': '🌧️', '09n': '🌧️',
        '10d': '🌦️', '10n': '🌧️',
        '11d': '🌩️️', '11n': '🌩️',
        '13d': '🌨️', '13n': '🌨️',
        '50d': '🌫️', '50n': '🌫️',
    }
    return mapping.get(icon_code, '☀️' if icon_code and icon_code.endswith('d') else '🌙')

def city_autocomplete(request):
    query = request.GET.get('q', '').strip()
    suggestions = []

    if len(query) >= 2:
        geo_url = f'http://api.openweathermap.org/geo/1.0/direct?q={query}&limit=5&appid={API_KEY}'
        try:
            res = requests.get(geo_url)
            if res.status_code == 200:
                data = res.json()
                for item in data:
                    city_label = item.get('name')
                    country = item.get('country', '')
                    state = item.get('state', '')
                    if state:
                        label = f"{city_label}, {state}, {country}"
                    else:
                        label = f"{city_label}, {country}"
                    suggestions.append({'name': city_label, 'label': label})
        except Exception:
            pass

    return JsonResponse(suggestions, safe=False)


def pin_location(request):
    if request.method == 'POST':
        city_name = request.POST.get('city_name')
        if city_name:
            pinned_locations = request.session.get('pinned_locations', [])
            is_already_pinned = any(loc['city_name'].lower() == city_name.lower() for loc in pinned_locations)
            
            if is_already_pinned:
                pinned_locations = [loc for loc in pinned_locations if loc['city_name'].lower() != city_name.lower()]
            else:
                pinned_locations.append({'city_name': city_name})
                
            request.session['pinned_locations'] = pinned_locations

    return redirect('index')


def index(request):
    weather_data = None
    error_message = None

    recent_searches = request.session.get('recent_searches', [])
    pinned_locations = request.session.get('pinned_locations', [])
    
    nav_locations_detailed = []
    for loc in pinned_locations:
        c_name = loc['city_name']
        try:
            url = f'https://api.openweathermap.org/data/2.5/weather?q={c_name}&units=metric&appid={API_KEY}'
            r = requests.get(url)
            if r.status_code == 200:
                d = r.json()
                nav_locations_detailed.append({
                    'city_name': d['name'],
                    'temperature': round(d['main']['temp']),
                    'temp_min': round(d['main']['temp_min']),
                    'temp_max': round(d['main']['temp_max']),
                    'description': d['weather'][0]['main'],
                })
        except Exception:
            pass

    nav_locations = pinned_locations 
    is_pinned = False
    is_local = False

    query_city = request.GET.get('city')
    query_lat = request.GET.get('lat')
    query_lon = request.GET.get('lon')

    if request.method == 'POST' or query_city or query_lat:
        city = request.POST.get('city') or query_city
        lat = request.POST.get('lat') or query_lat
        lon = request.POST.get('lon') or query_lon

        if lat and lon and not query_city:
            weather_url = f'https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units=metric&appid={API_KEY}'
            is_local = True
        elif city:
            weather_url = f'https://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&appid={API_KEY}'
        else:
            return render(request, 'wapp/index.html', {
                'recent_searches': recent_searches, 
                'pinned_locations': pinned_locations, 
                'nav_locations': nav_locations,
                'nav_locations_detailed': nav_locations_detailed
            })

        res = requests.get(weather_url)
        data = res.json()

        if res.status_code == 200:
            api_lat = data['coord']['lat']
            api_lon = data['coord']['lon']
            timezone_offset = data['timezone']
            city_name = data['name']

            utc_now = datetime.now(timezone.utc)
            local_dt = utc_now + timedelta(seconds=timezone_offset)
            formatted_date_time = local_dt.strftime('%A, %b %d, %Y | %I:%M %p')

            # Calculate precise local sunrise and sunset
            sunrise_utc = datetime.fromtimestamp(data['sys']['sunrise'], timezone.utc)
            sunset_utc = datetime.fromtimestamp(data['sys']['sunset'], timezone.utc)
            sunrise_local = sunrise_utc + timedelta(seconds=timezone_offset)
            sunset_local = sunset_utc + timedelta(seconds=timezone_offset)
            sunrise_str = sunrise_local.strftime('%I:%M %p').lstrip('0')
            sunset_str = sunset_local.strftime('%I:%M %p').lstrip('0')

            # Air Pollution API
            aqi_url = f'http://api.openweathermap.org/data/2.5/air_pollution?lat={api_lat}&lon={api_lon}&appid={API_KEY}'
            aqi_res = requests.get(aqi_url).json()
            aqi_levels = {1: 'Good', 2: 'Fair', 3: 'Moderate', 4: 'Poor', 5: 'Very Poor'}
            aqi_val = aqi_res.get('list', [{}])[0].get('main', {}).get('aqi', 1)
            aqi_desc = aqi_levels.get(aqi_val, 'Unknown')

            # Forecast API
            forecast_url = f'https://api.openweathermap.org/data/2.5/forecast?lat={api_lat}&lon={api_lon}&units=metric&appid={API_KEY}'
            forecast_res = requests.get(forecast_url).json()
            
            pop = forecast_res.get('list', [{}])[0].get('pop', 0)
            precipitation_chance = round(pop * 100)

            hourly_forecast = []
            daily_dict = {}

            if 'list' in forecast_res:
                for item in forecast_res['list']:
                    dt_txt = item['dt_txt']
                    item_dt = datetime.strptime(dt_txt, '%Y-%m-%d %H:%M:%S')
                    item_local_dt = item_dt + timedelta(seconds=timezone_offset)
                    time_str = item_local_dt.strftime('%I %p').lstrip('0')
                    temp = round(item['main']['temp'])
                    icon_c = item['weather'][0]['icon']
                    
                    if len(hourly_forecast) < 8:
                        hourly_forecast.append({
                            'time': time_str,
                            'temp': temp,
                            'icon': get_weather_emoji(icon_c)
                        })
                        
                    day_key = item_local_dt.strftime('%A')
                    if day_key not in daily_dict:
                        daily_dict[day_key] = {
                            'day_name': item_local_dt.strftime('%a'),
                            'temp_min': temp,
                            'temp_max': temp,
                            'icon': get_weather_emoji(icon_c)
                        }
                    else:
                        daily_dict[day_key]['temp_min'] = min(daily_dict[day_key]['temp_min'], temp)
                        daily_dict[day_key]['temp_max'] = max(daily_dict[day_key]['temp_max'], temp)

            daily_list = list(daily_dict.values())[:10]
            if daily_list:
                all_mins = [d['temp_min'] for d in daily_list]
                all_maxs = [d['temp_max'] for d in daily_list]
                global_min = min(all_mins)
                global_max = max(all_maxs)
                span = global_max - global_min if global_max != global_min else 1

                for d in daily_list:
                    left_pct = max(0, min(100, ((d['temp_min'] - global_min) / span) * 100))
                    width_pct = max(15, min(100 - left_pct, ((d['temp_max'] - d['temp_min']) / span) * 100))
                    d['bar_left'] = round(left_pct)
                    d['bar_width'] = round(width_pct)

            daily_forecast = daily_list

            icon_code = data['weather'][0]['icon']
            is_day = icon_code.endswith('d')

            weather_data = {
                'city': city_name,
                'temperature': round(data['main']['temp']),
                'temp_min': round(data['main']['temp_min']),
                'temp_max': round(data['main']['temp_max']),
                'description': data['weather'][0]['main'],
                'wind_speed': round(data['wind']['speed'] * 3.6),
                'is_day': is_day,
                'date_time': formatted_date_time,
                'sunrise': sunrise_str,
                'sunset': sunset_str,
                'aqi': f"{aqi_val} - {aqi_desc}",
                'precipitation': precipitation_chance,
                'hourly_forecast': hourly_forecast,
                'daily_forecast': daily_forecast,
            }

            if not is_local and city:
                new_entry = {
                    'city_name': city_name,
                    'temperature': round(data['main']['temp'])
                }
                recent_searches = [s for s in recent_searches if s['city_name'].lower() != city_name.lower()]
                recent_searches.insert(0, new_entry)
                recent_searches = recent_searches[:5]
                request.session['recent_searches'] = recent_searches
            
            is_pinned = any(loc['city_name'].lower() == city_name.lower() for loc in pinned_locations)

        else:
            error_message = data.get('message', 'Location not found. Please try again.').capitalize()

    context = {
        'weather': weather_data,
        'error': error_message,
        'recent_searches': recent_searches,
        'pinned_locations': pinned_locations,
        'nav_locations': nav_locations,
        'nav_locations_detailed': nav_locations_detailed,
        'is_pinned': is_pinned,
        'is_local': is_local,
    }

    return render(request, 'wapp/index.html', context)