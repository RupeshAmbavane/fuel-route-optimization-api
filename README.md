# 🚛 Fuel Route Optimization API

A Django REST API that calculates optimal fuel-efficient routes with cost-optimized refueling stops based on real fuel prices from 6,738+ truck stops across the USA.

## 🎯 Demo Video

**[Loom Video Demo (5 min)](YOUR_LOOM_LINK_HERE)**

## ✨ Features

- ✅ Smart route planning between any two US locations
- ✅ Cost-optimized fuel stops based on real pricing data
- ✅ Respects 500-mile vehicle range constraint
- ✅ Calculates total trip fuel cost at 10 MPG
- ✅ Fast response times (2-4 seconds)
- ✅ Minimal external API calls (exactly 1 per request)

## 🛠️ Tech Stack

- **Backend**: Django 5.1 (latest stable)
- **API Framework**: Django REST Framework 3.14
- **Routing API**: OSRM (Open Source Routing Machine)
- **Database**: SQLite with indexed queries
- **Geocoding**: Geopy/Nominatim

## 🚀 Quick Start

### Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Load fuel price data (300 stations, ~5 minutes)
python manage.py load_fuel_data csv_file.csv --limit 300

# Start server
python manage.py runserver
```

### API Usage
```bash
POST http://127.0.0.1:8000/api/optimize-route/
Content-Type: application/json

{
    "start": "Los Angeles, CA",
    "finish": "Chicago, IL"
}
```

### Sample Response
```json
{
    "start_location": "Los Angeles, CA",
    "end_location": "Chicago, IL",
    "total_distance_miles": 2019.47,
    "total_fuel_cost": "615.42",
    "total_gallons": 201.95,
    "fuel_stops": [
        {
            "station_name": "PILOT TRAVEL CENTER",
            "city": "Flagstaff",
            "state": "AZ",
            "price_per_gallon": "3.299",
            "gallons_needed": 46.52,
            "cost": "153.47"
        }
    ]
}
```

## 📊 Technical Highlights

- **Performance**: 2-4 second response times with caching
- **Efficiency**: Exactly 1 OSRM API call per request
- **Data**: 6,738 real fuel stations, 300+ geocoded
- **Optimization**: Database indexes on price and state for fast queries
- **Algorithm**: Divides routes into 450-mile segments, finds cheapest station within 50-mile radius

## 📋 Assignment Requirements Met

✅ Takes start/finish locations in USA  
✅ Returns route map with geometry  
✅ Finds optimal (cheapest) fuel stops  
✅ Respects 500-mile vehicle range  
✅ Calculates total fuel cost at 10 MPG  
✅ Uses provided CSV fuel price data  
✅ Uses free routing API (OSRM)  
✅ Built with Django 5.1  
✅ Fast response times  
✅ Minimal external API calls (1 per request)  

## 👨‍💻 Author

Created as part of a technical assessment. Built with Django, OSRM, and real fuel price data.

## 📄 License

This project was created for educational and assessment purposes.
