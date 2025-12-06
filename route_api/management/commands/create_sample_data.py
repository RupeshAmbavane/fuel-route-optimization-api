# route_api/management/commands/create_sample_data.py
# This creates sample fuel stations for testing

from django.core.management.base import BaseCommand
from route_api.models import FuelStation

class Command(BaseCommand):
    help = 'Create sample fuel stations for testing'
    
    def handle(self, *args, **options):
        self.stdout.write('Creating sample fuel stations...')
        
        sample_stations = [
            # California stations
            {'opis_id': 1001, 'name': 'Pilot Travel Center LA', 'address': '123 Highway 5', 
             'city': 'Los Angeles', 'state': 'CA', 'rack_id': 1, 'retail_price': 3.599,
             'latitude': 34.0522, 'longitude': -118.2437},
            
            {'opis_id': 1002, 'name': 'TA Travel Center Bakersfield', 'address': '456 I-5', 
             'city': 'Bakersfield', 'state': 'CA', 'rack_id': 1, 'retail_price': 3.499,
             'latitude': 35.3733, 'longitude': -119.0187},
            
            {'opis_id': 1003, 'name': 'Loves San Diego', 'address': '789 Interstate 8', 
             'city': 'San Diego', 'state': 'CA', 'rack_id': 1, 'retail_price': 3.699,
             'latitude': 32.7157, 'longitude': -117.1611},
            
            {'opis_id': 1004, 'name': 'Flying J Fresno', 'address': '321 Highway 99', 
             'city': 'Fresno', 'state': 'CA', 'rack_id': 1, 'retail_price': 3.449,
             'latitude': 36.7378, 'longitude': -119.7871},
            
            # Arizona stations
            {'opis_id': 2001, 'name': 'Pilot Phoenix', 'address': '111 I-10', 
             'city': 'Phoenix', 'state': 'AZ', 'rack_id': 2, 'retail_price': 3.299,
             'latitude': 33.4484, 'longitude': -112.0740},
            
            {'opis_id': 2002, 'name': 'TA Tucson', 'address': '222 I-10', 
             'city': 'Tucson', 'state': 'AZ', 'rack_id': 2, 'retail_price': 3.199,
             'latitude': 32.2226, 'longitude': -110.9747},
            
            # Nevada stations
            {'opis_id': 3001, 'name': 'Loves Las Vegas', 'address': '333 I-15', 
             'city': 'Las Vegas', 'state': 'NV', 'rack_id': 3, 'retail_price': 3.399,
             'latitude': 36.1699, 'longitude': -115.1398},
            
            # Texas stations
            {'opis_id': 4001, 'name': 'Pilot Dallas', 'address': '444 I-35', 
             'city': 'Dallas', 'state': 'TX', 'rack_id': 4, 'retail_price': 2.899,
             'latitude': 32.7767, 'longitude': -96.7970},
            
            {'opis_id': 4002, 'name': 'Flying J Houston', 'address': '555 I-10', 
             'city': 'Houston', 'state': 'TX', 'rack_id': 4, 'retail_price': 2.799,
             'latitude': 29.7604, 'longitude': -95.3698},
            
            {'opis_id': 4003, 'name': 'Loves San Antonio', 'address': '666 I-10', 
             'city': 'San Antonio', 'state': 'TX', 'rack_id': 4, 'retail_price': 2.849,
             'latitude': 29.4241, 'longitude': -98.4936},
            
            {'opis_id': 4004, 'name': 'TA Austin', 'address': '777 I-35', 
             'city': 'Austin', 'state': 'TX', 'rack_id': 4, 'retail_price': 2.949,
             'latitude': 30.2672, 'longitude': -97.7431},
            
            # New Mexico stations
            {'opis_id': 5001, 'name': 'Pilot Albuquerque', 'address': '888 I-40', 
             'city': 'Albuquerque', 'state': 'NM', 'rack_id': 5, 'retail_price': 3.099,
             'latitude': 35.0844, 'longitude': -106.6504},
            
            # Oklahoma stations
            {'opis_id': 6001, 'name': 'Loves Oklahoma City', 'address': '999 I-40', 
             'city': 'Oklahoma City', 'state': 'OK', 'rack_id': 6, 'retail_price': 2.799,
             'latitude': 35.4676, 'longitude': -97.5164},
            
            # Missouri stations
            {'opis_id': 7001, 'name': 'Flying J Kansas City', 'address': '1010 I-70', 
             'city': 'Kansas City', 'state': 'MO', 'rack_id': 7, 'retail_price': 2.899,
             'latitude': 39.0997, 'longitude': -94.5786},
            
            # Illinois stations
            {'opis_id': 8001, 'name': 'Pilot Chicago', 'address': '1111 I-90', 
             'city': 'Chicago', 'state': 'IL', 'rack_id': 8, 'retail_price': 3.299,
             'latitude': 41.8781, 'longitude': -87.6298},
            
            # New York stations
            {'opis_id': 9001, 'name': 'TA New York', 'address': '1212 I-95', 
             'city': 'New York', 'state': 'NY', 'rack_id': 9, 'retail_price': 3.599,
             'latitude': 40.7128, 'longitude': -74.0060},
            
            # Florida stations
            {'opis_id': 10001, 'name': 'Loves Miami', 'address': '1313 I-95', 
             'city': 'Miami', 'state': 'FL', 'rack_id': 10, 'retail_price': 3.199,
             'latitude': 25.7617, 'longitude': -80.1918},
            
            {'opis_id': 10002, 'name': 'Pilot Orlando', 'address': '1414 I-4', 
             'city': 'Orlando', 'state': 'FL', 'rack_id': 10, 'retail_price': 3.099,
             'latitude': 28.5383, 'longitude': -81.3792},
        ]
        
        created_count = 0
        for station_data in sample_stations:
            station, created = FuelStation.objects.update_or_create(
                opis_id=station_data['opis_id'],
                defaults=station_data
            )
            if created:
                created_count += 1
        
        self.stdout.write(self.style.SUCCESS(f'Successfully created {created_count} sample stations'))
        self.stdout.write(self.style.SUCCESS(f'Total stations in database: {FuelStation.objects.count()}'))