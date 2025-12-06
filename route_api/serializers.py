from rest_framework import serializers

class RouteRequestSerializer(serializers.Serializer):
    start = serializers.CharField(max_length=255, help_text="Start location (city, state or address)")
    finish = serializers.CharField(max_length=255, help_text="Finish location (city, state or address)")

class FuelStopSerializer(serializers.Serializer):
    station_name = serializers.CharField()
    address = serializers.CharField()
    city = serializers.CharField()
    state = serializers.CharField()
    price_per_gallon = serializers.DecimalField(max_digits=6, decimal_places=3)
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()
    distance_from_start = serializers.FloatField()
    gallons_needed = serializers.FloatField()
    cost = serializers.DecimalField(max_digits=10, decimal_places=2)

class RouteResponseSerializer(serializers.Serializer):
    start_location = serializers.CharField()
    end_location = serializers.CharField()
    total_distance_miles = serializers.FloatField()
    total_fuel_cost = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_gallons = serializers.FloatField()
    fuel_stops = FuelStopSerializer(many=True)
    route_geometry = serializers.JSONField()
    map_url = serializers.CharField()