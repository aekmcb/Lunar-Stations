# Lunar Stations Calculator

A Streamlit web application that calculates lunar stations based on the user's location and time preferences. This program tracks the Moon's movement through the ecliptic pathway of stars in real-time.

## Features

- Calculates precise starting times for lunar stations based on user location
- Supports both Northern and Southern hemispheres
- Provides ecliptic longitude and latitude calculations
- Includes detailed star descriptions for each lunar station
- Outputs in both CSV and ICS (calendar) formats
- Automatic timezone and DST handling
- Interactive preview of results
- Up to 31 days of calculations (1 month maximum)
- 1-minute precision to ensure no lunar station transitions are missed
- Sequential validation to verify complete lunar station coverage
- Memory-optimized chunked processing for reliable performance

## Installation

1. Clone this repository:
```bash
git clone [your-repository-url]
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the Streamlit app:
```bash
streamlit run lunar_stations_app.py
```

## Input Parameters

- **Latitude** (-90° to 90°): Negative for Southern Hemisphere
- **Longitude** (-180° to 180°): Negative for Western Hemisphere
- **Timezone**: Select nearest city (DST handled automatically)
- **Date Range**: Select start and end dates (up to 31 days / 1 month)

## Output Options

- CSV format (compatible with spreadsheets and Notion)
- ICS format (calendar integration)
- Optional data fields:
  - Ecliptic longitude
  - Ecliptic latitude
  - Star descriptions
  - Calendar alerts (ICS only)

## Data Sources

- Star positions based on precessed tropical coordinates from J.M. Hamade's 'Procession of the Night Theatre' (Revelore Press, 2024)
- Star identifications verified using the Hipparcos Catalogue (ESA, 1997)
- Astronomical calculations performed using the Skyfield library and DE421 ephemeris

## Dependencies

- Python 3.x
- Streamlit
- Skyfield
- pytz
- icalendar
- pandas
- numpy
- psutil
- Built-in Python libraries: csv, datetime, os, time

## Privacy

This application runs on Streamlit's platform. While calculations are performed server-side:
- No user data or calculation results are permanently stored
- Session data is temporarily cached during use and cleared upon closing
- Location inputs and results are not collected or retained
- No personal information is tracked or stored

For more information about Streamlit's data handling, please visit their privacy policy at https://streamlit.io/privacy-policy

## License

MIT License - See LICENSE file for details

## Contact

Email: info@livingelectriclanguage.com

## Version

App Version 1.3 (Updated 2025-07-01)

## Disclaimer

This calculator is provided for informational and educational purposes only. While we strive for accuracy in astronomical calculations, users should verify critical timings independently. The creators and contributors of this application are not liable for any decisions, actions, or consequences resulting from the use of this tool.
