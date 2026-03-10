# ==========================================================
# 🗺️ OpenStreetMap Emergency Services Locator
# ==========================================================

import requests
import math
from typing import List, Dict, Tuple, Optional

try:
    from config import DEFAULT_LATITUDE, DEFAULT_LONGITUDE, WEATHER_API_KEY
except ImportError:
    DEFAULT_LATITUDE = 13.0827
    DEFAULT_LONGITUDE = 80.2707
    WEATHER_API_KEY = ""


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great-circle distance between two points on Earth
    using the Haversine formula.
    
    Args:
        lat1, lon1: Coordinates of first point
        lat2, lon2: Coordinates of second point
        
    Returns:
        Distance in kilometers
    """
    R = 6371  # Earth's radius in kilometers
    
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    a = (math.sin(delta_lat / 2) ** 2 + 
         math.cos(lat1_rad) * math.cos(lat2_rad) * 
         math.sin(delta_lon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c


class EmergencyServicesLocator:
    """Locates nearest emergency services using OpenStreetMap"""
    
    def __init__(self):
        self.overpass_url = "https://overpass-api.de/api/interpreter"
        self.nominatim_url = "https://nominatim.openstreetmap.org"
        self.weather_api_key = WEATHER_API_KEY
        
    def _query_overpass(self, query: str) -> Optional[Dict]:
        """Execute Overpass API query"""
        try:
            response = requests.post(
                self.overpass_url,
                data={'data': query},
                timeout=30
            )
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"⚠️ Overpass API error: {e}")
        return None
    
    def get_address_from_coords(self, lat: float, lon: float) -> str:
        """Reverse geocoding - get address from coordinates"""
        try:
            response = requests.get(
                f"{self.nominatim_url}/reverse",
                params={
                    'lat': lat,
                    'lon': lon,
                    'format': 'json'
                },
                headers={'User-Agent': 'AccidentDetectionSystem/1.0'},
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                return data.get('display_name', 'Unknown Location')
        except Exception as e:
            print(f"⚠️ Geocoding error: {e}")
        return "Unknown Location"
    
    def find_nearest_hospitals(self, lat: float, lon: float, 
                               radius: int = 5000, limit: int = 5) -> List[Dict]:
        """
        Find nearest hospitals within radius
        
        Args:
            lat, lon: Current location coordinates
            radius: Search radius in meters
            limit: Maximum number of results
            
        Returns:
            List of hospitals with details
        """
        query = f"""
        [out:json][timeout:25];
        (
          node["amenity"="hospital"](around:{radius},{lat},{lon});
          way["amenity"="hospital"](around:{radius},{lat},{lon});
          relation["amenity"="hospital"](around:{radius},{lat},{lon});
        );
        out center {limit};
        """
        
        result = self._query_overpass(query)
        hospitals = []
        
        if result and 'elements' in result:
            for element in result['elements']:
                h_lat = element.get('lat') or element.get('center', {}).get('lat')
                h_lon = element.get('lon') or element.get('center', {}).get('lon')
                
                if h_lat and h_lon:
                    distance = haversine_distance(lat, lon, h_lat, h_lon)
                    hospitals.append({
                        'name': element.get('tags', {}).get('name', 'Hospital'),
                        'latitude': h_lat,
                        'longitude': h_lon,
                        'distance_km': round(distance, 2),
                        'phone': element.get('tags', {}).get('phone', 'N/A'),
                        'emergency': element.get('tags', {}).get('emergency', 'unknown'),
                        'address': element.get('tags', {}).get('addr:full', 'N/A')
                    })
        
        # Sort by distance
        hospitals.sort(key=lambda x: x['distance_km'])
        return hospitals[:limit]
    
    def find_nearest_police_stations(self, lat: float, lon: float,
                                     radius: int = 5000, limit: int = 5) -> List[Dict]:
        """
        Find nearest police stations within radius
        
        Args:
            lat, lon: Current location coordinates
            radius: Search radius in meters
            limit: Maximum number of results
            
        Returns:
            List of police stations with details
        """
        query = f"""
        [out:json][timeout:25];
        (
          node["amenity"="police"](around:{radius},{lat},{lon});
          way["amenity"="police"](around:{radius},{lat},{lon});
          relation["amenity"="police"](around:{radius},{lat},{lon});
        );
        out center {limit};
        """
        
        result = self._query_overpass(query)
        stations = []
        
        if result and 'elements' in result:
            for element in result['elements']:
                s_lat = element.get('lat') or element.get('center', {}).get('lat')
                s_lon = element.get('lon') or element.get('center', {}).get('lon')
                
                if s_lat and s_lon:
                    distance = haversine_distance(lat, lon, s_lat, s_lon)
                    stations.append({
                        'name': element.get('tags', {}).get('name', 'Police Station'),
                        'latitude': s_lat,
                        'longitude': s_lon,
                        'distance_km': round(distance, 2),
                        'phone': element.get('tags', {}).get('phone', 'N/A'),
                        'address': element.get('tags', {}).get('addr:full', 'N/A')
                    })
        
        # Sort by distance
        stations.sort(key=lambda x: x['distance_km'])
        return stations[:limit]
    
    def find_nearest_fire_stations(self, lat: float, lon: float,
                                   radius: int = 5000, limit: int = 3) -> List[Dict]:
        """Find nearest fire stations"""
        query = f"""
        [out:json][timeout:25];
        (
          node["amenity"="fire_station"](around:{radius},{lat},{lon});
          way["amenity"="fire_station"](around:{radius},{lat},{lon});
        );
        out center {limit};
        """
        
        result = self._query_overpass(query)
        stations = []
        
        if result and 'elements' in result:
            for element in result['elements']:
                f_lat = element.get('lat') or element.get('center', {}).get('lat')
                f_lon = element.get('lon') or element.get('center', {}).get('lon')
                
                if f_lat and f_lon:
                    distance = haversine_distance(lat, lon, f_lat, f_lon)
                    stations.append({
                        'name': element.get('tags', {}).get('name', 'Fire Station'),
                        'latitude': f_lat,
                        'longitude': f_lon,
                        'distance_km': round(distance, 2),
                        'phone': element.get('tags', {}).get('phone', 'N/A')
                    })
        
        stations.sort(key=lambda x: x['distance_km'])
        return stations[:limit]
    
    def get_all_emergency_services(self, lat: float, lon: float) -> Dict:
        """
        Get all nearest emergency services
        
        Returns:
            Dictionary containing nearest hospital, police, and fire station
        """
        hospitals = self.find_nearest_hospitals(lat, lon, limit=3)
        police = self.find_nearest_police_stations(lat, lon, limit=3)
        fire = self.find_nearest_fire_stations(lat, lon, limit=2)
        address = self.get_address_from_coords(lat, lon)
        
        return {
            'location': {
                'latitude': lat,
                'longitude': lon,
                'address': address
            },
            'nearest_hospital': hospitals[0] if hospitals else None,
            'all_hospitals': hospitals,
            'nearest_police': police[0] if police else None,
            'all_police_stations': police,
            'nearest_fire_station': fire[0] if fire else None,
            'all_fire_stations': fire
        }


class WeatherService:
    """Fetches real-time weather data"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or WEATHER_API_KEY
        self.base_url = "https://api.openweathermap.org/data/2.5/weather"
    
    def get_weather(self, lat: float, lon: float) -> Dict:
        """
        Get current weather conditions
        
        Args:
            lat, lon: Location coordinates
            
        Returns:
            Weather data dictionary
        """
        if not self.api_key:
            return self._get_simulated_weather()
        
        try:
            response = requests.get(
                self.base_url,
                params={
                    'lat': lat,
                    'lon': lon,
                    'appid': self.api_key,
                    'units': 'metric'
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'weather': data['weather'][0]['main'],
                    'description': data['weather'][0]['description'],
                    'temperature': round(data['main']['temp'], 1),
                    'humidity': data['main']['humidity'],
                    'wind_speed': data['wind']['speed'],
                    'visibility': data.get('visibility', 10000) / 1000,  # km
                    'clouds': data['clouds']['all'],
                    'rain': data.get('rain', {}).get('1h', 0),
                    'risk_factor': self._calculate_risk_factor(data)
                }
        except Exception as e:
            print(f"⚠️ Weather API error: {e}")
        
        return self._get_simulated_weather()
    
    def _get_simulated_weather(self) -> Dict:
        """Return simulated weather when API unavailable"""
        return {
            'weather': 'Clear',
            'description': 'clear sky',
            'temperature': 28,
            'humidity': 65,
            'wind_speed': 3.5,
            'visibility': 10,
            'clouds': 20,
            'rain': 0,
            'risk_factor': 'Low'
        }
    
    def _calculate_risk_factor(self, weather_data: Dict) -> str:
        """Calculate accident risk based on weather conditions"""
        risk_score = 0
        
        weather_main = weather_data['weather'][0]['main'].lower()
        visibility = weather_data.get('visibility', 10000)
        rain = weather_data.get('rain', {}).get('1h', 0)
        wind = weather_data['wind']['speed']
        
        # Weather condition scoring
        if weather_main in ['rain', 'drizzle']:
            risk_score += 30
        elif weather_main in ['thunderstorm']:
            risk_score += 50
        elif weather_main in ['snow', 'sleet']:
            risk_score += 60
        elif weather_main in ['fog', 'mist', 'haze']:
            risk_score += 40
        
        # Visibility scoring
        if visibility < 1000:
            risk_score += 40
        elif visibility < 5000:
            risk_score += 20
        
        # Rain intensity
        if rain > 10:
            risk_score += 30
        elif rain > 5:
            risk_score += 15
        
        # Wind speed
        if wind > 20:
            risk_score += 20
        elif wind > 10:
            risk_score += 10
        
        # Determine risk level
        if risk_score >= 60:
            return 'High'
        elif risk_score >= 30:
            return 'Medium'
        else:
            return 'Low'


# Create global instances
emergency_locator = EmergencyServicesLocator()
weather_service = WeatherService()


def get_emergency_info(lat: float = None, lon: float = None) -> Dict:
    """
    Get complete emergency information for a location
    
    Args:
        lat, lon: Location coordinates (uses default if not provided)
        
    Returns:
        Complete emergency services and weather info
    """
    lat = lat or DEFAULT_LATITUDE
    lon = lon or DEFAULT_LONGITUDE
    
    services = emergency_locator.get_all_emergency_services(lat, lon)
    weather = weather_service.get_weather(lat, lon)
    
    return {
        **services,
        'weather': weather
    }


if __name__ == "__main__":
    # Test the emergency services locator
    print("🗺️ Testing Emergency Services Locator...")
    print("=" * 50)
    
    # Test location: Chennai, India
    test_lat = 13.0827
    test_lon = 80.2707
    
    info = get_emergency_info(test_lat, test_lon)
    
    print(f"\n📍 Location: {info['location']['address']}")
    print(f"\n🏥 Nearest Hospital:")
    if info['nearest_hospital']:
        h = info['nearest_hospital']
        print(f"   Name: {h['name']}")
        print(f"   Distance: {h['distance_km']} km")
        print(f"   Phone: {h['phone']}")
    
    print(f"\n👮 Nearest Police Station:")
    if info['nearest_police']:
        p = info['nearest_police']
        print(f"   Name: {p['name']}")
        print(f"   Distance: {p['distance_km']} km")
    
    print(f"\n🌤️ Weather Conditions:")
    w = info['weather']
    print(f"   Weather: {w['weather']} ({w['description']})")
    print(f"   Temperature: {w['temperature']}°C")
    print(f"   Visibility: {w['visibility']} km")
    print(f"   Risk Factor: {w['risk_factor']}")
    
    print("\n✅ Test complete!")
