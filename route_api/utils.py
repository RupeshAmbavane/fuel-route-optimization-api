import requests
import math
from decimal import Decimal
from typing import List, Dict, Tuple
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from django.core.cache import cache
from .models import FuelStation

class RouteOptimizer:
    def __init__(self):
        self.geolocator = Nominatim(user_agent="fuel_route_optimizer")
        self.max_range_miles = 500
        self.mpg = 10
        self.search_radius_miles = 50
        
    def geocode_location(self, location: str) -> Tuple[float, float]:
        """Convert location string to coordinates with caching"""
        cache_key = f"geocode_{location}"
        coords = cache.get(cache_key)
        
        if coords:
            return coords
            
        location_data = self.geolocator.geocode(f"{location}, USA")
        if not location_data:
            raise ValueError(f"Could not find location: {location}")
        
        coords = (location_data.latitude, location_data.longitude)
        cache.set(cache_key, coords, timeout=86400)
        return coords
    
    def get_route(self, start_coords: Tuple[float, float], 
                  end_coords: Tuple[float, float]) -> Dict:
        """Get route from OSRM API"""
        start_lon, start_lat = start_coords[1], start_coords[0]
        end_lon, end_lat = end_coords[1], end_coords[0]
        
        url = f"http://router.project-osrm.org/route/v1/driving/{start_lon},{start_lat};{end_lon},{end_lat}"
        params = {
            'overview': 'full',
            'geometries': 'geojson',
            'steps': 'true'
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data['code'] != 'Ok':
            raise ValueError("Could not find route between locations")
        
        return data['routes'][0]
    
    def decode_geometry(self, geometry: Dict) -> List[Tuple[float, float]]:
        """Extract coordinates from GeoJSON geometry"""
        return [(coord[1], coord[0]) for coord in geometry['coordinates']]
    
    def find_fuel_stops(self, route_coords: List[Tuple[float, float]], 
                       total_distance_miles: float) -> List[Dict]:
        """Find optimal fuel stops along the route"""
        fuel_stops = []
        current_range = self.max_range_miles - 50
        distance_covered = 0
        
        num_stops = math.ceil(total_distance_miles / current_range)
        
        if num_stops == 0:
            return []
        
        segment_length = total_distance_miles / (num_stops + 1)
        
        for stop_num in range(num_stops):
            target_distance = segment_length * (stop_num + 1)
            
            point_index = int((target_distance / total_distance_miles) * len(route_coords))
            point_index = min(point_index, len(route_coords) - 1)
            target_point = route_coords[point_index]
            
            station = self.find_nearest_cheapest_station(
                target_point, 
                self.search_radius_miles
            )
            
            if station:
                if stop_num == 0:
                    distance_since_last = target_distance
                else:
                    distance_since_last = target_distance - (segment_length * stop_num)
                
                gallons_needed = distance_since_last / self.mpg
                cost = float(station.retail_price) * gallons_needed
                
                fuel_stops.append({
                    'station_name': station.name,
                    'address': station.address,
                    'city': station.city,
                    'state': station.state,
                    'price_per_gallon': station.retail_price,
                    'latitude': station.latitude,
                    'longitude': station.longitude,
                    'distance_from_start': target_distance,
                    'gallons_needed': round(gallons_needed, 2),
                    'cost': round(Decimal(str(cost)), 2)
                })
        
        if fuel_stops:
            last_stop_distance = fuel_stops[-1]['distance_from_start']
            remaining_distance = total_distance_miles - last_stop_distance
        else:
            remaining_distance = total_distance_miles
        
        if remaining_distance > 0:
            final_gallons = remaining_distance / self.mpg
            if fuel_stops:
                fuel_stops[-1]['gallons_needed'] += round(final_gallons, 2)
                fuel_stops[-1]['cost'] += round(
                    Decimal(str(float(fuel_stops[-1]['price_per_gallon']) * final_gallons)), 2
                )
        
        return fuel_stops
    
    def find_nearest_cheapest_station(self, point: Tuple[float, float], 
                                     radius_miles: float) -> FuelStation:
        """Find cheapest fuel station within radius of point"""
        stations = FuelStation.objects.filter(
            latitude__isnull=False,
            longitude__isnull=False
        ).order_by('retail_price')[:500]
        
        best_station = None
        best_score = float('inf')
        
        for station in stations:
            station_point = (station.latitude, station.longitude)
            distance = geodesic(point, station_point).miles
            
            if distance <= radius_miles:
                score = float(station.retail_price) + (distance / radius_miles) * 0.5
                
                if score < best_score:
                    best_score = score
                    best_station = station
        
        return best_station
    
    def optimize_route(self, start: str, finish: str) -> Dict:
        """Main function to optimize route with fuel stops"""
        start_coords = self.geocode_location(start)
        end_coords = self.geocode_location(finish)
        
        route = self.get_route(start_coords, end_coords)
        
        distance_meters = route['distance']
        distance_miles = distance_meters * 0.000621371
        route_geometry = route['geometry']
        route_coords = self.decode_geometry(route_geometry)
        
        fuel_stops = self.find_fuel_stops(route_coords, distance_miles)
        
        total_fuel_cost = sum(stop['cost'] for stop in fuel_stops)
        total_gallons = sum(stop['gallons_needed'] for stop in fuel_stops)
        
        map_url = self.generate_map_url(start_coords, end_coords, fuel_stops)
        
        return {
            'start_location': start,
            'end_location': finish,
            'total_distance_miles': round(distance_miles, 2),
            'total_fuel_cost': round(total_fuel_cost, 2),
            'total_gallons': round(total_gallons, 2),
            'fuel_stops': fuel_stops,
            'route_geometry': route_geometry,
            'map_url': map_url
        }
    
    def generate_map_url(self, start: Tuple[float, float], 
                        end: Tuple[float, float], 
                        fuel_stops: List[Dict]) -> str:
        """Generate OpenStreetMap URL for visualization"""
        center_lat = (start[0] + end[0]) / 2
        center_lon = (start[1] + end[1]) / 2
        
        markers = f"&mlon={start[1]}&mlat={start[0]}"
        for stop in fuel_stops:
            markers += f"&mlon={stop['longitude']}&mlat={stop['latitude']}"
        markers += f"&mlon={end[1]}&mlat={end[0]}"
        
        return f"https://www.openstreetmap.org/?mlat={center_lat}&mlon={center_lon}&zoom=6{markers}"
