"""Weather service for API integration and caching."""
import json
import time
from pathlib import Path
from typing import Optional, Dict, Any
import httpx
from config import (
    OPENWEATHER_API_KEY,
    OPENWEATHER_BASE_URL,
    FORECAST_BASE_URL,
    CACHE_DIR,
    CACHE_EXPIRY_MINUTES
)


class WeatherCache:
    """Handles caching of weather data to reduce API calls."""
    
    def __init__(self, cache_dir: Path = CACHE_DIR, expiry_minutes: int = CACHE_EXPIRY_MINUTES):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(exist_ok=True)
        self.expiry_seconds = expiry_minutes * 60
    
    def _get_cache_file(self, city: str) -> Path:
        """Get cache file path for a city."""
        return self.cache_dir / f"{city.lower().replace(' ', '_')}.json"
    
    def get(self, city: str) -> Optional[Dict[str, Any]]:
        """Get cached weather data if not expired."""
        cache_file = self._get_cache_file(city)
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    cached = json.load(f)
                    if time.time() - cached['timestamp'] < self.expiry_seconds:
                        return cached['data']
            except (json.JSONDecodeError, KeyError):
                # Invalid cache file, remove it
                cache_file.unlink()
        return None
    
    def set(self, city: str, data: Dict[str, Any]):
        """Cache weather data with timestamp."""
        cache_file = self._get_cache_file(city)
        cached = {
            'timestamp': time.time(),
            'data': data
        }
        try:
            with open(cache_file, 'w') as f:
                json.dump(cached, f)
        except Exception as e:
            print(f"Error caching data: {e}")


class WeatherService:
    """Service for fetching weather data from OpenWeatherMap API."""
    
    def __init__(self):
        self.api_key = OPENWEATHER_API_KEY
        self.cache = WeatherCache()
    
    async def get_weather(self, city: str, units: str = "metric") -> Dict[str, Any]:
        """
        Get current weather for a city.
        
        Args:
            city: City name
            units: Temperature units ('metric' for Celsius, 'imperial' for Fahrenheit)
        
        Returns:
            Dictionary containing weather data
        
        Raises:
            Exception: If API call fails
        """
        # Check cache first
        cache_key = f"{city}_{units}"
        cached_data = self.cache.get(cache_key)
        if cached_data:
            return cached_data
        
        if not self.api_key:
            raise Exception("API key not configured. Please set OPENWEATHER_API_KEY in .env file.")
        
        params = {
            "q": city,
            "appid": self.api_key,
            "units": units,
        }
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(OPENWEATHER_BASE_URL, params=params)
                
                if response.status_code == 404:
                    raise Exception(f"City '{city}' not found. Please check the spelling.")
                elif response.status_code == 401:
                    raise Exception(
                        "Invalid API key. Please check your OpenWeatherMap API key.\n"
                        "1. Make sure your .env file contains: OPENWEATHER_API_KEY=your_actual_key\n"
                        "2. Get a free API key at: https://openweathermap.org/api\n"
                        "3. Remove any quotes or extra spaces around the key\n"
                        "4. Restart the application after updating .env"
                    )
                elif response.status_code != 200:
                    raise Exception(f"API error: {response.status_code}")
                
                data = response.json()
                
                # Cache the result
                self.cache.set(cache_key, data)
                
                return data
                
        except httpx.TimeoutException:
            raise Exception("Request timed out. Please check your internet connection.")
        except httpx.RequestError as e:
            raise Exception(f"Network error: {str(e)}")
    
    async def get_forecast(self, city: str, units: str = "metric") -> Dict[str, Any]:
        """
        Get 5-day weather forecast for a city.
        
        Args:
            city: City name
            units: Temperature units ('metric' for Celsius, 'imperial' for Fahrenheit)
        
        Returns:
            Dictionary containing forecast data
        
        Raises:
            Exception: If API call fails
        """
        if not self.api_key:
            raise Exception("API key not configured. Please set OPENWEATHER_API_KEY in .env file.")
        
        params = {
            "q": city,
            "appid": self.api_key,
            "units": units,
        }
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(FORECAST_BASE_URL, params=params)
                
                if response.status_code == 404:
                    raise Exception(f"City '{city}' not found. Please check the spelling.")
                elif response.status_code == 401:
                    raise Exception(
                        "Invalid API key. Please check your OpenWeatherMap API key.\n"
                        "1. Make sure your .env file contains: OPENWEATHER_API_KEY=your_actual_key\n"
                        "2. Get a free API key at: https://openweathermap.org/api\n"
                        "3. Remove any quotes or extra spaces around the key\n"
                        "4. Restart the application after updating .env"
                    )
                elif response.status_code != 200:
                    raise Exception(f"API error: {response.status_code}")
                
                return response.json()
                
        except httpx.TimeoutException:
            raise Exception("Request timed out. Please check your internet connection.")
        except httpx.RequestError as e:
            raise Exception(f"Network error: {str(e)}")
    
    def convert_temperature(self, temp: float, from_unit: str, to_unit: str) -> float:
        """Convert temperature between Celsius and Fahrenheit."""
        if from_unit == to_unit:
            return temp
        
        if from_unit == "metric" and to_unit == "imperial":
            return (temp * 9/5) + 32
        elif from_unit == "imperial" and to_unit == "metric":
            return (temp - 32) * 5/9
        
        return temp

