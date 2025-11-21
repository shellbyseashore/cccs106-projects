# Quick Setup Guide

## Step 1: Install Dependencies

```bash
# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
venv\Scripts\activate


# Install packages
pip install -r requirements.txt
```

## Step 2: Get OpenWeatherMap API Key

1. Go to https://openweathermap.org/api
2. Sign up for a free account (if you don't have one)
3. **VERY IMPORTANT**: Navigate to https://home.openweathermap.org/api_keys
4. **Copy your API key EXACTLY** - don't type it, use copy/paste
5. If you see multiple keys, make sure you're using the correct one
6. If the key doesn't work, generate a NEW key and use that instead

## Step 3: Create .env File

Create a file named `.env` in the project root with the following content:

```
OPENWEATHER_API_KEY=your_api_key_here
```

Replace `your_api_key_here` with your actual API key from Step 2.

## Step 4: Run the Application

```bash
python main.py
```

The application will open in a new window.

## Troubleshooting

### "API key not configured" or "Invalid API key" error
- Make sure you created the `.env` file in the project root
- Verify the file is named exactly `.env` (not `.env.txt`)
- Check that your API key is correct and active
- **Important**: The .env file should contain exactly:
  ```
  OPENWEATHER_API_KEY=your_actual_api_key_here
  ```
  - No quotes around the key
  - No spaces around the `=` sign
  - Replace `your_actual_api_key_here` with your real API key
- Get a free API key at: https://openweathermap.org/api
- After updating .env, restart the application

### "City not found" error
- Check the spelling of the city name
- Try using "City, Country" format (e.g., "London, UK")

### Import errors
- Make sure you activated the virtual environment
- Run `pip install -r requirements.txt` again

