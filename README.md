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
- Up to 365 days of calculations

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

- **Latitude** (0° to 90°): N for Northern and S for Southern Hemispheres
- **Longitude** (0° to 180°): W for Western and E for Eastern Hemisphere
- **Timezone**: Select nearest city (DST handled automatically)
- **Date Range**: Select start and end dates (up to 365 days)

## Output Options

- CSV format (compatible with spreadsheets and Notion)
- ICS format (calendar integration)
- Optional data fields:
  - Ecliptic longitude
  - Ecliptic latitude
  - Station descriptions
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
- Additional libraries: csv, datetime

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
1.1 April 4, 2025

App Version 1.1 (Updated 2024-04-04)

## Disclaimer

This calculator is provided for informational and educational purposes only. While we strive for accuracy in astronomical calculations, users should verify critical timings independently. The creators and contributors of this application are not liable for any decisions, actions, or consequences resulting from the use of this tool.
