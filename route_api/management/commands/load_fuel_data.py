# route_api/management/commands/load_fuel_data.py


from django.core.management.base import BaseCommand
from route_api.models import FuelStation
import csv
import os
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
import time

class Command(BaseCommand):
    help = 'Load fuel price data from CSV and geocode addresses'
    
    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to CSV file')
        parser.add_argument(
            '--skip-geocoding',
            action='store_true',
            help='Skip geocoding (faster, but less accurate routing)'
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=None,
            help='Limit number of stations to geocode (for testing)'
        )
    
    def handle(self, *args, **options):
        csv_file = options['csv_file']
        skip_geocoding = options['skip_geocoding']
        limit = options['limit']
        
        # Check if file exists
        if not os.path.exists(csv_file):
            self.stdout.write(self.style.ERROR(f'File not found: {csv_file}'))
            self.stdout.write('Current directory: ' + os.getcwd())
            return
        
        # Get file size
        file_size = os.path.getsize(csv_file)
        self.stdout.write(self.style.SUCCESS(f'Found CSV file: {csv_file} ({file_size:,} bytes)'))
        
        # Read CSV with multiple encoding attempts
        stations_data = []
        encodings_to_try = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252', 'iso-8859-1']
        
        for encoding in encodings_to_try:
            try:
                self.stdout.write(f'\nTrying encoding: {encoding}')
                
                with open(csv_file, 'r', encoding=encoding, errors='replace') as file:
                    # Peek at first few lines
                    first_lines = [file.readline() for _ in range(3)]
                    self.stdout.write('First 3 lines:')
                    for i, line in enumerate(first_lines, 1):
                        self.stdout.write(f'  Line {i}: {line[:100]}')
                    
                    # Reset to beginning
                    file.seek(0)
                    
                    # Use csv.DictReader
                    reader = csv.DictReader(file)
                    
                    # Verify headers
                    if reader.fieldnames:
                        self.stdout.write(f'Headers: {reader.fieldnames}')
                    else:
                        self.stdout.write(self.style.WARNING('No headers found!'))
                        continue
                    
                    # Read all rows
                    row_count = 0
                    error_count = 0
                    
                    for row_num, row in enumerate(reader, 1):
                        try:
                            # Get retail price
                            price_str = row.get('Retail Price', '').strip()
                            if not price_str:
                                continue
                            
                            # Parse price (handle different formats)
                            try:
                                price = float(price_str)
                            except ValueError:
                                self.stdout.write(
                                    self.style.WARNING(f'Row {row_num}: Invalid price "{price_str}"')
                                )
                                error_count += 1
                                continue
                            
                            # Parse OPIS ID
                            try:
                                opis_id = int(row.get('OPIS Truckstop ID', 0))
                            except ValueError:
                                self.stdout.write(
                                    self.style.WARNING(f'Row {row_num}: Invalid OPIS ID')
                                )
                                error_count += 1
                                continue
                            
                            # Parse Rack ID
                            try:
                                rack_id = int(row.get('Rack ID', 0))
                            except ValueError:
                                rack_id = 0
                            
                            # Store station data
                            station = {
                                'opis_id': opis_id,
                                'name': row.get('Truckstop Name', '').strip(),
                                'address': row.get('Address', '').strip(),
                                'city': row.get('City', '').strip(),
                                'state': row.get('State', '').strip(),
                                'rack_id': rack_id,
                                'retail_price': price,
                            }
                            
                            # Validate required fields
                            if not station['name'] or not station['city'] or not station['state']:
                                error_count += 1
                                continue
                            
                            stations_data.append(station)
                            row_count += 1
                            
                            # Show first valid row
                            if row_count == 1:
                                self.stdout.write(self.style.SUCCESS(f'\n✓ First valid row parsed:'))
                                self.stdout.write(f'  ID: {station["opis_id"]}')
                                self.stdout.write(f'  Name: {station["name"]}')
                                self.stdout.write(f'  City: {station["city"]}, {station["state"]}')
                                self.stdout.write(f'  Price: ${station["retail_price"]:.3f}')
                        
                        except Exception as e:
                            error_count += 1
                            if error_count <= 3:
                                self.stdout.write(
                                    self.style.WARNING(f'Row {row_num} error: {str(e)}')
                                )
                            continue
                    
                    self.stdout.write(
                        self.style.SUCCESS(f'\n✓ Successfully read {row_count} valid stations')
                    )
                    if error_count > 0:
                        self.stdout.write(
                            self.style.WARNING(f'⚠ Skipped {error_count} invalid rows')
                        )
                    
                    # If we got data, break the encoding loop
                    if stations_data:
                        break
                    
            except UnicodeDecodeError as e:
                self.stdout.write(self.style.WARNING(f'Encoding {encoding} failed: {str(e)[:50]}'))
                continue
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Unexpected error with {encoding}: {str(e)}'))
                continue
        
        # Check if we got any data
        if not stations_data:
            self.stdout.write(self.style.ERROR('\n✗ Could not read any valid station data!'))
            self.stdout.write('Please check that:')
            self.stdout.write('  1. The CSV file is not corrupted')
            self.stdout.write('  2. The file has the correct headers')
            self.stdout.write('  3. The file is in the correct location')
            return
        
        self.stdout.write(self.style.SUCCESS(f'\n{"="*70}'))
        self.stdout.write(self.style.SUCCESS(f'LOADING {len(stations_data)} STATIONS INTO DATABASE'))
        self.stdout.write(self.style.SUCCESS(f'{"="*70}\n'))
        
        # Initialize geocoder
        geolocator = None
        if not skip_geocoding:
            geolocator = Nominatim(user_agent="fuel_data_loader", timeout=10)
            if limit:
                self.stdout.write(
                    f'Geocoding limited to {limit} stations (~{limit} seconds)\n'
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f'⚠ WARNING: Geocoding ALL {len(stations_data)} stations will take '
                        f'~{len(stations_data)/60:.0f} minutes!\n'
                        f'Consider using --limit 300 for faster setup.\n'
                    )
                )
        
        # Load stations into database
        created_count = 0
        updated_count = 0
        geocoded_count = 0
        failed_geocode_count = 0
        
        for idx, station_data in enumerate(stations_data):
            # Create or update station
            station, created = FuelStation.objects.update_or_create(
                opis_id=station_data['opis_id'],
                defaults={
                    'name': station_data['name'],
                    'address': station_data['address'],
                    'city': station_data['city'],
                    'state': station_data['state'],
                    'rack_id': station_data['rack_id'],
                    'retail_price': station_data['retail_price'],
                }
            )
            
            if created:
                created_count += 1
            else:
                updated_count += 1
            
            # Geocode if needed
            if not skip_geocoding and (station.latitude is None or station.longitude is None):
                # Check limit
                if limit and geocoded_count >= limit:
                    if geocoded_count == limit:
                        self.stdout.write(
                            self.style.WARNING(f'\n✓ Reached geocoding limit of {limit} stations\n')
                        )
                    skip_geocoding = True
                    continue
                
                try:
                    full_address = f"{station_data['address']}, {station_data['city']}, {station_data['state']}, USA"
                    location = geolocator.geocode(full_address)
                    
                    if location:
                        station.latitude = location.latitude
                        station.longitude = location.longitude
                        station.save()
                        geocoded_count += 1
                        
                        if geocoded_count % 10 == 0:
                            percent = (geocoded_count / (limit or len(stations_data))) * 100
                            self.stdout.write(
                                f'  [{geocoded_count:3d}] {station.city:20s}, {station.state}  '
                                f'({percent:5.1f}% complete)'
                            )
                    else:
                        failed_geocode_count += 1
                    
                    # Rate limiting - Nominatim requires 1 second between requests
                    time.sleep(1)
                    
                except (GeocoderTimedOut, GeocoderServiceError) as e:
                    failed_geocode_count += 1
                    continue
                except Exception as e:
                    failed_geocode_count += 1
                    if failed_geocode_count <= 3:
                        self.stdout.write(
                            self.style.WARNING(f'Geocoding error: {str(e)[:50]}')
                        )
                    continue
            
            # Progress update for non-geocoding operations
            if skip_geocoding and (idx + 1) % 500 == 0:
                self.stdout.write(f'  Loaded {idx + 1}/{len(stations_data)} stations...')
        
        # Final summary
        self.stdout.write('\n' + '='*70)
        self.stdout.write(self.style.SUCCESS('✓ IMPORT COMPLETE'))
        self.stdout.write('='*70)
        self.stdout.write(f'Created:          {created_count:4d} new stations')
        self.stdout.write(f'Updated:          {updated_count:4d} existing stations')
        self.stdout.write(f'Geocoded:         {geocoded_count:4d} locations')
        self.stdout.write(f'Failed geocoding: {failed_geocode_count:4d} stations')
        self.stdout.write(f'Total in DB:      {FuelStation.objects.count():4d} stations')
        
        # Check how many have coordinates
        with_coords = FuelStation.objects.filter(
            latitude__isnull=False, 
            longitude__isnull=False
        ).count()
        self.stdout.write(f'With coordinates: {with_coords:4d} stations ({with_coords/FuelStation.objects.count()*100:.1f}%)')
        
        if with_coords < 50:
            self.stdout.write(
                self.style.WARNING(
                    f'\n⚠ WARNING: Only {with_coords} stations have coordinates.'
                )
            )
            self.stdout.write(
                self.style.WARNING(
                    '⚠ Fuel stops may not be found for some routes.'
                )
            )
            self.stdout.write(
                self.style.WARNING(
                    '⚠ Run: python manage.py load_fuel_data fuelpricesforbeassessment.csv --limit 300'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f'\n✓ Success! You have {with_coords} geocoded stations.'
                )
            )
            self.stdout.write(
                self.style.SUCCESS(
                    '✓ API is ready for testing!'
                )
            )