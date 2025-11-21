"""Weather Application with enhanced features."""
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, List
import flet as ft
from weather_service import WeatherService
from config import HISTORY_FILE, MAX_HISTORY_ITEMS, OPENWEATHER_API_KEY


class WeatherApp:
    """Main weather application class."""
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.weather_service = WeatherService()
        self.current_unit = "metric"  # 'metric' for Celsius, 'imperial' for Fahrenheit
        self.current_city = ""
        self.current_weather_data = None
        self.forecast_data = None
        
        # Load search history
        self.search_history = self.load_history()
        
        # Setup page
        self.setup_page()
        
        # Build UI
        self.build_ui()
    
    def setup_page(self):
        """Configure page settings."""
        self.page.title = "Weather Application"
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.padding = 20
        self.page.bgcolor = "#ECEFF1"  # Blue grey 50
    
    def load_history(self) -> List[str]:
        """Load search history from file."""
        if HISTORY_FILE.exists():
            try:
                with open(HISTORY_FILE, 'r') as f:
                    history = json.load(f)
                    return history[:MAX_HISTORY_ITEMS] if isinstance(history, list) else []
            except (json.JSONDecodeError, IOError):
                return []
        return []
    
    def save_history(self):
        """Save search history to file."""
        try:
            with open(HISTORY_FILE, 'w') as f:
                json.dump(self.search_history, f)
        except IOError as e:
            print(f"Error saving history: {e}")
    
    def add_to_history(self, city: str):
        """Add city to search history."""
        city = city.strip()
        if not city:
            return
        
        # Remove if exists and add to front
        if city in self.search_history:
            self.search_history.remove(city)
        
        self.search_history.insert(0, city)
        self.search_history = self.search_history[:MAX_HISTORY_ITEMS]
        self.save_history()
        self.update_history_display()
    
    def update_history_display(self):
        """Update the history dropdown with current history."""
        if self.history_dropdown:
            self.history_dropdown.options = [
                ft.dropdown.Option(city) for city in self.search_history
            ]
            self.history_dropdown.update()
    
    def build_ui(self):
        """Build the main UI components."""
        # Header
        header = ft.Container(
            content=ft.Text(
                "Weather Application",
                size=32,
                weight=ft.FontWeight.BOLD,
                color="#0D47A1",  # Blue 900
            ),
            alignment=ft.alignment.center,
            padding=ft.padding.only(bottom=20),
        )
        
        # Search section
        self.city_input = ft.TextField(
            label="Enter city name",
            hint_text="e.g., London, New York, Tokyo",
            expand=True,
            on_submit=self.on_search,
            autofocus=True,
        )
        
        self.search_btn = ft.ElevatedButton(
            "Search",
            icon="search",
            on_click=self.on_search,
            style=ft.ButtonStyle(
                color="#FFFFFF",  # White
                bgcolor="#1976D2",  # Blue 700
            ),
        )
        
        # History dropdown
        self.history_dropdown = ft.Dropdown(
            label="Recent searches",
            options=[ft.dropdown.Option(city) for city in self.search_history],
            on_change=self.on_history_select,
            visible=len(self.search_history) > 0,
            expand=True,
        )
        
        search_row = ft.Row(
            controls=[
                self.city_input,
                self.search_btn,
            ],
            spacing=10,
        )
        
        # Unit toggle
        self.unit_toggle = ft.Switch(
            label="Fahrenheit",
            value=False,
            on_change=self.on_unit_toggle,
        )
        
        unit_row = ft.Row(
            controls=[
                ft.Text("Temperature Unit:", size=14, weight=ft.FontWeight.W_500),
                self.unit_toggle,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        )
        
        # Error message
        self.error_text = ft.Text(
            "",
            color="#F44336",  # Red
            size=14,
            visible=False,
        )
        
        # Weather display container
        self.weather_container = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(
                        "Search for a city to see weather information",
                        size=18,
                        color="#757575",  # Grey 600
                        text_align=ft.TextAlign.CENTER,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
            ),
            padding=20,
            border_radius=10,
            bgcolor="#FFFFFF",  # White
            visible=True,
        )
        
        # Forecast container
        self.forecast_container = ft.Container(
            content=ft.Column(
                controls=[],
                spacing=10,
            ),
            padding=20,
            border_radius=10,
            bgcolor="#FFFFFF",  # White
            visible=False,
        )
        
        # Forecast header
        forecast_header = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Text(
                        "5-Day Forecast",
                        size=20,
                        weight=ft.FontWeight.BOLD,
                        color="#0D47A1",  # Blue 900
                    ),
                    ft.IconButton(
                        icon="refresh",
                        tooltip="Refresh forecast",
                        on_click=self.on_refresh_forecast,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            padding=ft.padding.only(bottom=10),
            visible=False,
        )
        
        self.forecast_header = forecast_header
        
        # Main layout
        self.page.add(
            header,
            search_row,
            ft.Container(
                content=self.history_dropdown,
                padding=ft.padding.only(top=10, bottom=10),
            ),
            unit_row,
            self.error_text,
            self.weather_container,
            forecast_header,
            self.forecast_container,
        )
    
    def on_history_select(self, e):
        """Handle history dropdown selection."""
        if e.control.value:
            self.city_input.value = e.control.value
            self.on_search(e)
    
    def on_unit_toggle(self, e):
        """Handle temperature unit toggle."""
        if e.control.value:
            self.current_unit = "imperial"
        else:
            self.current_unit = "metric"
        
        # If we have current weather, refresh it with new units
        if self.current_city:
            self.page.run_task(self.get_weather, self.current_city)
    
    def on_search(self, e):
        """Handle search button click."""
        city = self.city_input.value.strip()
        if not city:
            self.show_error("Please enter a city name")
            return
        
        self.current_city = city
        self.hide_error()
        self.page.run_task(self.get_weather, city)
    
    def on_refresh_forecast(self, e):
        """Refresh the 5-day forecast."""
        if self.current_city:
            self.page.run_task(self.get_forecast, self.current_city)
    
    async def get_weather(self, city: str):
        """Fetch weather data for a city."""
        # Show loading
        self.weather_container.content = ft.Column(
            controls=[
                ft.ProgressRing(),
                ft.Text("Loading weather data...", size=16),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
        )
        self.weather_container.visible = True
        self.weather_container.update()
        
        try:
            data = await self.weather_service.get_weather(city, self.current_unit)
            self.current_weather_data = data
            self.add_to_history(city)
            self.display_weather(data)
            
            # Automatically load forecast
            await self.get_forecast(city)
            
        except Exception as e:
            self.show_error(str(e))
            self.weather_container.visible = False
            self.weather_container.update()
    
    async def get_forecast(self, city: str):
        """Fetch 5-day forecast for a city."""
        try:
            data = await self.weather_service.get_forecast(city, self.current_unit)
            self.forecast_data = data
            self.display_forecast(data)
        except Exception as e:
            # Don't show error for forecast, just log it
            print(f"Forecast error: {e}")
    
    def display_weather(self, data: dict):
        """Display weather information."""
        main = data.get("main", {})
        weather = data.get("weather", [{}])[0]
        wind = data.get("wind", {})
        
        temp = main.get("temp", 0)
        feels_like = main.get("feels_like", 0)
        humidity = main.get("humidity", 0)
        pressure = main.get("pressure", 0)
        description = weather.get("description", "N/A").title()
        icon_code = weather.get("icon", "01d")
        wind_speed = wind.get("speed", 0)
        city_name = data.get("name", "Unknown")
        country = data.get("sys", {}).get("country", "")
        
        # Weather icon URL
        icon_url = f"https://openweathermap.org/img/wn/{icon_code}@2x.png"
        
        # Unit symbol
        unit_symbol = "°F" if self.current_unit == "imperial" else "°C"
        wind_unit = "mph" if self.current_unit == "imperial" else "m/s"
        
        # Background color based on weather condition
        bg_color = self.get_weather_color(description.lower())
        
        self.weather_container.content = ft.Column(
            controls=[
                # City name
                ft.Text(
                    f"{city_name}, {country}",
                    size=24,
                    weight=ft.FontWeight.BOLD,
                    color="#0D47A1",  # Blue 900
                ),
                
                # Weather icon and temperature
                ft.Row(
                    controls=[
                        ft.Image(
                            src=icon_url,
                            width=100,
                            height=100,
                        ),
                        ft.Text(
                            f"{temp:.1f}{unit_symbol}",
                            size=48,
                            weight=ft.FontWeight.BOLD,
                            color="#1976D2",  # Blue 700
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=10,
                ),
                
                # Description
                ft.Text(
                    description,
                    size=20,
                    color="#616161",  # Grey 700
                ),
                
                # Details row
                ft.Container(
                    content=ft.Row(
                        controls=[
                            # Feels like
                            ft.Column(
                                controls=[
                                    ft.Text(
                                        "Feels Like",
                                        size=12,
                                        color="#757575",  # Grey 600
                                    ),
                                    ft.Text(
                                        f"{feels_like:.1f}{unit_symbol}",
                                        size=18,
                                        weight=ft.FontWeight.W_500,
                                    ),
                                ],
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                spacing=5,
                            ),
                            
                            # Humidity
                            ft.Column(
                                controls=[
                                    ft.Text(
                                        "Humidity",
                                        size=12,
                                        color="#757575",  # Grey 600
                                    ),
                                    ft.Text(
                                        f"{humidity}%",
                                        size=18,
                                        weight=ft.FontWeight.W_500,
                                    ),
                                ],
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                spacing=5,
                            ),
                            
                            # Wind Speed
                            ft.Column(
                                controls=[
                                    ft.Text(
                                        "Wind Speed",
                                        size=12,
                                        color="#757575",  # Grey 600
                                    ),
                                    ft.Text(
                                        f"{wind_speed:.1f} {wind_unit}",
                                        size=18,
                                        weight=ft.FontWeight.W_500,
                                    ),
                                ],
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                spacing=5,
                            ),
                            
                            # Pressure
                            ft.Column(
                                controls=[
                                    ft.Text(
                                        "Pressure",
                                        size=12,
                                        color="#757575",  # Grey 600
                                    ),
                                    ft.Text(
                                        f"{pressure} hPa",
                                        size=18,
                                        weight=ft.FontWeight.W_500,
                                    ),
                                ],
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                spacing=5,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_EVENLY,
                        spacing=20,
                    ),
                    padding=ft.padding.only(top=20),
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=15,
        )
        
        self.weather_container.bgcolor = bg_color
        self.weather_container.visible = True
        self.weather_container.update()
    
    def display_forecast(self, data: dict):
        """Display 5-day weather forecast."""
        if not data or "list" not in data:
            return
        
        forecast_list = data.get("list", [])
        
        # Group by date (take one forecast per day, around noon)
        daily_forecasts = {}
        for item in forecast_list:
            date = item.get("dt_txt", "").split(" ")[0]
            if date not in daily_forecasts:
                daily_forecasts[date] = item
            else:
                # Prefer forecasts around 12:00
                current_time = item.get("dt_txt", "").split(" ")[1]
                if "12:00" in current_time or "15:00" in current_time:
                    daily_forecasts[date] = item
        
        # Limit to 5 days
        forecast_items = list(daily_forecasts.values())[:5]
        
        if not forecast_items:
            return
        
        unit_symbol = "°F" if self.current_unit == "imperial" else "°C"
        
        forecast_cards = []
        for item in forecast_items:
            main = item.get("main", {})
            weather = item.get("weather", [{}])[0]
            wind = item.get("wind", {})
            
            temp = main.get("temp", 0)
            temp_min = main.get("temp_min", 0)
            temp_max = main.get("temp_max", 0)
            description = weather.get("description", "N/A").title()
            icon_code = weather.get("icon", "01d")
            humidity = main.get("humidity", 0)
            wind_speed = wind.get("speed", 0)
            date_str = item.get("dt_txt", "")
            
            # Format date
            try:
                dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
                day_name = dt.strftime("%A")
                date_display = dt.strftime("%b %d")
            except:
                day_name = "Unknown"
                date_display = date_str
            
            icon_url = f"https://openweathermap.org/img/wn/{icon_code}@2x.png"
            wind_unit = "mph" if self.current_unit == "imperial" else "m/s"
            
            card = ft.Card(
                content=ft.Container(
                    content=ft.Column(
                        controls=[
                            # Date
                            ft.Text(
                                day_name,
                                size=16,
                                weight=ft.FontWeight.BOLD,
                                color="#0D47A1",  # Blue 900
                            ),
                            ft.Text(
                                date_display,
                                size=12,
                                color="#757575",  # Grey 600
                            ),
                            
                            # Icon and temp
                            ft.Row(
                                controls=[
                                    ft.Image(
                                        src=icon_url,
                                        width=60,
                                        height=60,
                                    ),
                                    ft.Column(
                                        controls=[
                                            ft.Text(
                                                f"{temp:.0f}{unit_symbol}",
                                                size=24,
                                                weight=ft.FontWeight.BOLD,
                                            ),
                                            ft.Text(
                                                f"{temp_min:.0f}° / {temp_max:.0f}°",
                                                size=12,
                                                color="#757575",  # Grey 600
                                            ),
                                        ],
                                        spacing=2,
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.CENTER,
                            ),
                            
                            # Description
                            ft.Text(
                                description,
                                size=12,
                                color="#616161",  # Grey 700
                                text_align=ft.TextAlign.CENTER,
                            ),
                            
                            # Details
                            ft.Row(
                                controls=[
                                    ft.Text(f"💧 {humidity}%", size=11),
                                    ft.Text(f"💨 {wind_speed:.1f} {wind_unit}", size=11),
                                ],
                                alignment=ft.MainAxisAlignment.CENTER,
                                spacing=10,
                            ),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=8,
                    ),
                    padding=15,
                ),
                elevation=2,
            )
            
            forecast_cards.append(card)
        
        self.forecast_container.content = ft.Column(
            controls=forecast_cards,
            spacing=10,
        )
        self.forecast_container.visible = True
        self.forecast_header.visible = True
        self.forecast_container.update()
        self.forecast_header.update()
    
    def get_weather_color(self, description: str) -> str:
        """Get background color based on weather description."""
        description_lower = description.lower()
        
        if "clear" in description_lower or "sun" in description_lower:
            return "#FFFDE7"  # Yellow 100
        elif "rain" in description_lower or "drizzle" in description_lower:
            return "#E3F2FD"  # Blue 100
        elif "snow" in description_lower:
            return "#E0F7FA"  # Cyan 100
        elif "cloud" in description_lower or "overcast" in description_lower:
            return "#EEEEEE"  # Grey 200
        elif "thunder" in description_lower or "storm" in description_lower:
            return "#F3E5F5"  # Purple 100
        elif "mist" in description_lower or "fog" in description_lower:
            return "#CFD8DC"  # Blue grey 100
        else:
            return "#FFFFFF"  # White
    
    def show_error(self, message: str):
        """Display error message."""
        self.error_text.value = message
        self.error_text.visible = True
        self.error_text.update()
    
    def hide_error(self):
        """Hide error message."""
        self.error_text.visible = False
        self.error_text.update()


def main(page: ft.Page):
    """Main entry point."""
    # Verify API key is loaded
    if not OPENWEATHER_API_KEY or OPENWEATHER_API_KEY.strip() == "":
        # Show error in UI
        error_dialog = ft.AlertDialog(
            title=ft.Text("API Key Not Found"),
            content=ft.Text(
                "The OpenWeatherMap API key was not found.\n\n"
                "Please check your .env file:\n"
                "1. Make sure .env file exists in the project folder\n"
                "2. It should contain: OPENWEATHER_API_KEY=your_key\n"
                "3. Get a free key at: https://openweathermap.org/api\n"
                "4. Restart the application after updating .env"
            ),
            actions=[
                ft.TextButton("OK", on_click=lambda e: page.close_dialog()),
            ],
        )
        page.dialog = error_dialog
        error_dialog.open = True
        page.update()
        print("ERROR: API key not found. Check .env file.")
    else:
        print(f"API key loaded: {OPENWEATHER_API_KEY[:10]}... (length: {len(OPENWEATHER_API_KEY)})")
    
    app = WeatherApp(page)


if __name__ == "__main__":
    ft.app(target=main)

