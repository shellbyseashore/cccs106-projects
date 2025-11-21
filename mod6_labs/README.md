# Weather Application

A modern, feature-rich weather application built with Flet v0.28.3 that provides real-time weather information and forecasts using the OpenWeatherMap API.

## Features

### Base Features ✅
- **City Search**: Search for weather information by city name
- **Current Weather Display**: Shows temperature, weather description, humidity, wind speed, and pressure
- **Weather Icons**: Displays weather condition icons from OpenWeatherMap
- **Error Handling**: Comprehensive error handling for invalid cities and network issues
- **Modern UI**: Clean, Material Design-inspired interface with color-coded weather conditions
- **Async Operations**: Proper async/await implementation using `page.run_task()`

### Enhanced Features ✨

#### 1. Search History (Easy)
- Stores the last 10 searched cities
- Displays history in a dropdown menu
- Allows quick re-search by selecting from history
- Persists history using JSON file storage (`search_history.json`)

#### 2. Temperature Unit Toggle (Easy)
- Switch between Celsius (°C) and Fahrenheit (°F)
- Automatically converts and redisplay current weather data
- Remembers user's preference during session
- Updates both current weather and forecast when toggled

#### 3. 5-Day Weather Forecast (Medium)
- Displays weather forecast for the next 5 days
- Shows daily high/low temperatures
- Weather conditions and icons for each day
- Additional details: humidity and wind speed
- Organized in card-based layout for better UX

#### 4. Weather Data Caching (Hard)
- Caches API responses to reduce API calls
- 30-minute cache expiry for optimal balance
- Serves cached data when available
- Automatic cache invalidation after expiry
- Improves performance and reduces API usage

## Screenshots

*Note: Add screenshots of your application here*

## Running the Application

### Prerequisites
- Python 3.8 or higher
- OpenWeatherMap API key (free tier available)

### Installation

1. **Clone or download this repository**

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   - Create a `.env` file in the project root
   - Add your OpenWeatherMap API key:
     ```
     OPENWEATHER_API_KEY=your_api_key_here
     ```

5. **Run the application**:
   ```bash
   python main.py
   ```

## API Configuration

### Getting OpenWeatherMap API Key

1. Sign up at [OpenWeatherMap](https://openweathermap.org/api)
2. Navigate to the API Keys section in your account
3. Copy your API key
4. Add it to your `.env` file:
   ```
   OPENWEATHER_API_KEY=your_api_key_here
   ```

### API Endpoints Used

- **Current Weather**: `https://api.openweathermap.org/data/2.5/weather`
- **5-Day Forecast**: `https://api.openweathermap.org/data/2.5/forecast`

## Project Structure

```
mod6_labs/
├── main.py                 # Main application file
├── weather_service.py      # API service layer with caching
├── config.py              # Configuration management
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (not committed)
├── .gitignore            # Git ignore file
├── README.md             # This file
├── cache/                # Cache directory (auto-created)
│   └── [city_cache_files].json
└── search_history.json   # Search history storage (auto-created)
```

## Technologies Used

- **Flet v0.28.3**: Cross-platform UI framework for building desktop and web apps
- **httpx**: Modern async HTTP client for API requests
- **python-dotenv**: Environment variable management
- **OpenWeatherMap API**: Weather data provider

## Features Implementation Details

### Search History
The search history feature stores up to 10 recently searched cities in a JSON file. The history is automatically loaded when the application starts and updated each time a new city is searched.

**File**: `search_history.json`  
**Location**: Project root  
**Format**: JSON array of city names

### Temperature Unit Toggle
The unit toggle allows users to switch between metric (Celsius) and imperial (Fahrenheit) units. When toggled, the application automatically:
- Fetches new data from the API with the selected units
- Updates all displayed temperatures
- Maintains the selection during the session

### 5-Day Forecast
The forecast feature fetches and displays weather predictions for the next 5 days. The implementation:
- Groups forecast data by date
- Selects representative forecasts (preferring noon-time forecasts)
- Displays daily high/low temperatures
- Shows weather conditions, icons, humidity, and wind speed

### Weather Data Caching
The caching system reduces API calls and improves performance:
- Caches responses for 30 minutes
- Stores cache files in the `cache/` directory
- Automatically checks cache before making API requests
- Handles cache expiration and cleanup

## Error Handling

The application includes comprehensive error handling for:
- **Invalid city names**: Shows user-friendly error messages
- **Network issues**: Handles timeouts and connection errors
- **API errors**: Displays appropriate messages for API failures
- **Missing API key**: Warns if API key is not configured
- **File I/O errors**: Gracefully handles cache and history file errors

## UI/UX Features

- **Color-coded backgrounds**: Weather conditions determine background colors
  - Sunny/Clear: Yellow
  - Rainy: Blue
  - Snowy: Cyan
  - Cloudy: Grey
  - Stormy: Purple
  - Misty/Foggy: Blue-grey

- **Material Design**: Modern, clean interface following Material Design principles
- **Responsive layout**: Adapts to different screen sizes
- **Loading indicators**: Shows progress during API calls
- **Error messages**: Clear, actionable error messages

## Development Notes

### Async Operations
All network operations use async/await patterns with `httpx.AsyncClient`. UI updates are handled through Flet's `page.run_task()` method to ensure proper thread safety.

### Code Organization
- **Separation of concerns**: UI logic in `main.py`, API logic in `weather_service.py`
- **Configuration management**: Centralized in `config.py`
- **Error handling**: Comprehensive try-except blocks with user-friendly messages

## Future Enhancements

Potential features for future development:
- Weather alerts and warnings
- Multiple cities comparison
- Weather charts and graphs
- Current location detection
- Desktop notifications
- Voice input for city search

## License

This project is created for educational purposes as part of CCCS 106 - Application Development and Emerging Technologies.

## Author

Created for Module 6 - System Integration and Network Programming

## Acknowledgments

- OpenWeatherMap for providing weather data API
- Flet team for the excellent UI framework

