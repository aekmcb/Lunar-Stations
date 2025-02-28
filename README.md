# Lunar Stations Calculator

A Streamlit application that calculates and tracks lunar station timings based on your location. This program helps users follow the traditional practice of tracking the Moon's movement through the ecliptic pathway using modern astronomical calculations.

## Features

- Real-time tracking of lunar stations based on user location
- Precise calculations using NASA's DE421 ephemeris data
- Flexible date range selection (up to 60 days)
- Multiple output formats:
  - CSV file (for spreadsheets and databases)
  - ICS file (for calendar applications)
- Customizable timezone settings
- Optional calendar alerts
- Interactive preview of results

## Installation

1. Clone this repository:
```bash
git clone [your-repository-url]
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

## Usage

1. Run the Streamlit app:
```bash
streamlit run lunar_stations_app.py
```

2. Enter your location details:
   - Latitude and Longitude (can be found using Google Maps)
   - Select your timezone
   - Choose start and end dates/times

3. Select your preferred output format (CSV or ICS)

4. Click "Calculate Lunar Stations" to generate results

## Dependencies

- Python 3.7+
- Streamlit
- Skyfield
- pytz
- icalendar
- pandas
- psutil

## Technical Details

- Calculations are based on the DE421 ephemeris from NASA's Jet Propulsion Laboratory
- Lunar station positions are derived from J.M. Hamade's "The Procession of the Night Theatre" (Revelore Press, 2024)
- All calculations are performed locally in the user's browser

## Privacy Notice

This application performs all calculations locally. No user data, location information, or calculation results are stored or collected. All inputs are temporary and are cleared when you close the application.

## License

Copyright (c) 2025 Living Electric Language LLC
Licensed under the MIT License - see LICENSE file for details

## Contact

Email: info@livingelectriclanguage.com

## Disclaimer

This calculator is provided for informational and educational purposes only. While we strive for accuracy in astronomical calculations, users should verify critical timings independently. The creators and contributors of this application are not liable for any decisions, actions, or consequences resulting from the use of this tool.
