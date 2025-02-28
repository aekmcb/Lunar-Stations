"""
Lunar Stations Calculator
Copyright (c) 2025 Living Electric Language LLC
Licensed under the MIT License - see LICENSE file for details
"""

import streamlit as st
import csv
from skyfield.api import Topos, load
from datetime import datetime, timedelta
import pytz
from icalendar import Calendar, Event, Alarm
import pandas as pd
from io import StringIO
import os
import psutil

# Define lunar stations data
LUNAR_STATIONS = {
    50.7833: ("3#LS", "nnn"),
    64.1167: ("4#LS", "nnn"),
    77.45: ("5#LS", "nnn"),
    90.7833: ("6#LS", "nnn"),
    104.1167: ("7#LS", "nnn"),
    117.45: ("8#LS", "nnn"),
    130.7833: ("9#LS", "nnn"),
    144.1167: ("10#LS", "nnn"),
    157.45: ("11#LS", "nnn"),
    170.7833: ("12#LS", "nnn"),
    184.1167: ("13#LS", "nnn"),
    197.45: ("14#LS", "nnn"),
    210.7833: ("15#LS", "nnn"),
    224.1167: ("16#LS", "nnn"),
    237.45: ("17#LS", "nnn"),
    250.7833: ("18#LS", "nnn"),
    264.1167: ("19#LS", "nnn"),
    277.45: ("20#LS", "nnn"),
    290.7833: ("21#LS", "nnn"),
    300.6167: ("22#LS", "nnn"),
    305.6167: ("23#LS", "nnn"),
    317.45: ("24#LS", "nnn"),
    330.7833: ("25#LS", "nnn"),
    344.1166: ("26#LS", "nnn"),
    357.45: ("27#LS", "nnn"),
    10.7833: ("28#LS", "nnn"),
    24.1167: ("1#LS", "nnn"),
    37.45: ("2#LS", "nnn")
}

def check_memory_usage():
    """Monitor memory usage and return True if within safe limits"""
    memory = psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024  # MB
    return memory < 1000  # Return False if over 1GB

def validate_time_range(start_datetime, end_datetime):
    """Validate time range and return error message if invalid"""
    if end_datetime <= start_datetime:
        return "End time must be after start time"
    
    time_span = end_datetime - start_datetime
    if time_span > timedelta(days=60):
        return "Time span cannot exceed 60 days to prevent memory issues"
    
    return None

def calculate_lunar_stations(lat, lon, timezone, start_time, end_time, output_format, include_alerts=False):
    """Main calculation function with error handling"""
    try:
        # Set timezone
        local_tz = pytz.timezone(timezone)
        
        # Load ephemeris data
        try:
            ts = load.timescale()
            planets = load('de421.bsp')
        except Exception as e:
            raise Exception(f"Failed to load ephemeris data: {str(e)}")
        
        earth, moon = planets['earth'], planets['moon']
        
        # Set observer position
        location = Topos(f'{lat} N' if lat >= 0 else f'{abs(lat)} S', 
                        f'{lon} E' if lon >= 0 else f'{abs(lon)} W')
        my_position = earth + location
        
        # Pre-compute time values
        time_points = []
        current = start_time
        while current <= end_time:
            if not check_memory_usage():
                raise Exception("Memory usage exceeded safe limits")
            time_points.append(current)
            current += timedelta(minutes=1)

        times = ts.from_datetimes(time_points)

        # Calculate positions
        positions = my_position.at(times).observe(moon).apparent()
        ecl_positions = positions.ecliptic_latlon(epoch='date')
        longitudes = ecl_positions[1].degrees % 360

        # Process results
        all_matches = {lon: [] for lon in LUNAR_STATIONS.keys()}
        
        for lon_target in LUNAR_STATIONS.keys():
            min_difference = float('inf')
            min_time = None
            min_lon = None
            last_difference = float('inf')
            
            for i, lon in enumerate(longitudes):
                difference = min(
                    abs(lon - lon_target),
                    abs(lon - lon_target + 360),
                    abs(lon - lon_target - 360)
                )
                
                if difference < 0.008:
                    if difference < min_difference:
                        min_difference = difference
                        min_time = time_points[i]
                        min_lon = lon
                        
                elif last_difference < 0.008 and min_time is not None:
                    all_matches[lon_target].append((min_time, min_lon))
                    min_difference = float('inf')
                    min_time = None
                    min_lon = None
                
                last_difference = difference
            
            if min_time is not None:
                all_matches[lon_target].append((min_time, min_lon))

        # Collect all matches
        all_sorted_matches = []
        for lon_target, matches in all_matches.items():
            ls, _ = LUNAR_STATIONS[lon_target]  # Removed asterism from output
            for match_time, lon in matches:
                all_sorted_matches.append((match_time, ls, lon))

        # Sort by datetime
        all_sorted_matches.sort(key=lambda x: x[0])
        
        return all_sorted_matches

    except Exception as e:
        raise Exception(f"Calculation error: {str(e)}")

def generate_csv(results, timezone):
    """Generate CSV with error handling"""
    try:
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(['Time (Local)', 'Lunar_Station', 'Ecliptic_Longitude'])
        local_tz = pytz.timezone(timezone)
        
        for match_time, ls, topo_lon in results:
            local_time = match_time.replace(tzinfo=pytz.UTC).astimezone(local_tz)
            formatted_time = local_time.strftime('%Y-%m-%d %H:%M:%S')
            writer.writerow([formatted_time, ls, f"{topo_lon:.2f}"])
        
        return output.getvalue()
    except Exception as e:
        raise Exception(f"CSV generation error: {str(e)}")

def generate_ics(results, timezone, include_alerts):
    """Generate ICS with error handling"""
    try:
        cal = Calendar()
        cal.add('prodid', '-//Lunar Station Calculator//example.com//')
        cal.add('version', '2.0')
        local_tz = pytz.timezone(timezone)

        for match_time, ls, topo_lon in results:
            local_time = match_time.replace(tzinfo=pytz.UTC).astimezone(local_tz)
            event = Event()
            event.add('summary', f'Lunar Station {ls}')
            event.add('dtstart', local_time)
            event.add('dtend', local_time + timedelta(minutes=30))
            event.add('description', 
                     f'Lunar Station {ls}\n'
                     f'Ecliptic Longitude: {topo_lon:.2f}°')
            
            if include_alerts:
                alarm = Alarm()
                alarm.add('action', 'DISPLAY')
                alarm.add('description', f'Lunar Station {ls} active now')
                alarm.add('trigger', timedelta(minutes=0))
                event.add_component(alarm)
            
            cal.add_component(event)

        return cal.to_ical()
    except Exception as e:
        raise Exception(f"ICS generation error: {str(e)}")

def display_results_preview(results, timezone):
    """Display preview with error handling"""
    try:
        local_tz = pytz.timezone(timezone)
        preview_data = []
        
        for match_time, ls, topo_lon in results:
            local_time = match_time.replace(tzinfo=pytz.UTC).astimezone(local_tz)
            preview_data.append({
                'Time': local_time.strftime('%Y-%m-%d %H:%M:%S'),
                'Station': ls,
                'Ecliptic Longitude': f"{topo_lon:.2f}°"
            })
        
        df = pd.DataFrame(preview_data)
        return df
    except Exception as e:
        raise Exception(f"Preview generation error: {str(e)}")

def main():
    st.title("Lunar Stations Calculator")
    
    # Add description
    st.markdown("""
    This simple program tracks in real time the Moon's movement through the *ecliptic pathway* of stars based on your location. Join your ancestors in practicing this ancient technique but with modern assistance.

    Traditionally, our ancestors divided the ecliptic circle into 27-28 sections using *asterisms* (star patterns) to mark each segment, with each section representing approximately 24 hours of lunar movement. These sections are known as *Lunar Stations*. 

    The Lunar Station locations in this program are based on J.M. Hamade's '*The Procession of the Night Theatre*' (Revelore Press, 2024). This excellent resource covers this practice across cultures.

    ---

    **How to Use**

    Enter in your:
    * Latitude and Longitude (Google Maps can help with this)
    * Time zone (important: select your local timezone for accurate local times)
    * Start date and time
    * End date and time (up to 60 days)
    
    Select your preferred output file format:
    
    **CSV file**
    * Can be imported into spreadsheets (Excel, Google Sheets)
    * Works with Notion databases
    * Simple text format for data analysis
    
    **ICS file**
    * Imports directly into calendar apps
    * Works with Google Calendar, Apple Calendar, Outlook
    * Optional alerts for station changes

    This program provides the precise starting date and time for each Lunar Station based on your specific location, along with the ecliptic longitude (same dimension as zodiacal locations).
    """)
    
    # Sidebar for inputs
    st.sidebar.header("Location Settings")
    lat = st.sidebar.number_input("Latitude (-90 to 90)", min_value=-90.0, max_value=90.0, value=0.0)
    lon = st.sidebar.number_input("Longitude (-180 to 180)", min_value=-180.0, max_value=180.0, value=0.0)
    
    # Timezone selector
    timezones = sorted(pytz.all_timezones)
    timezone = st.sidebar.selectbox("Select Timezone", timezones, 
                                  index=timezones.index('UTC'))
    
    # Date and time settings
    st.sidebar.header("Time Settings")
    start_date = st.sidebar.date_input("Start Date", datetime(2025, 2, 4))
    start_time = st.sidebar.time_input("Start Time", datetime(2025, 2, 4).time())
    end_date = st.sidebar.date_input("End Date", datetime(2025, 4, 2))
    end_time = st.sidebar.time_input("End Time", datetime(2025, 4, 2).time())
    
    # Output format selection
    st.sidebar.header("Output Settings")
    output_format = st.sidebar.selectbox("Output Format", ["CSV", "ICS"])
    
    # Alert option for ICS
    include_alerts = False
    if output_format == "ICS":
        include_alerts = st.sidebar.checkbox("Include Calendar Alerts", value=True)
    
    # Calculate button
    if st.sidebar.button("Calculate Lunar Stations"):
        try:
            # Combine date and time
            start_datetime = datetime.combine(start_date, start_time)
            end_datetime = datetime.combine(end_date, end_time)
            
            # Validate time range
            error_message = validate_time_range(start_datetime, end_datetime)
            if error_message:
                st.error(error_message)
                return
            
            # Convert to UTC
            local_tz = pytz.timezone(timezone)
            start_datetime = local_tz.localize(start_datetime).astimezone(pytz.UTC)
            end_datetime = local_tz.localize(end_datetime).astimezone(pytz.UTC)
            
            with st.spinner("Calculating lunar stations..."):
                # Run calculations
                results = calculate_lunar_stations(
                    lat, lon, timezone, start_datetime, end_datetime, 
                    output_format, include_alerts
                )
                
                # Generate and offer download of output file
                if output_format == "CSV":
                    csv_data = generate_csv(results, timezone)
                    st.download_button(
                        label="Download CSV",
                        data=csv_data,
                        file_name="lunar_stations.csv",
                        mime="text/csv"
                    )
                else:  # ICS
                    ics_data = generate_ics(results, timezone, include_alerts)
                    st.download_button(
                        label="Download ICS",
                        data=ics_data,
                        file_name="lunar_stations.ics",
                        mime="text/calendar"
                    )
                
                # Display preview of results
                st.success("Calculation complete!")
                df = display_results_preview(results, timezone)
                st.dataframe(df)
                
                # Display credits and disclaimer
                st.markdown("""
                #### Additional Credits
                - **Astronomical Calculations**: [Skyfield](https://rhodesmill.org/skyfield/) by Brandon Rhodes
                - **Ephemeris Data**: DE421 from NASA's Jet Propulsion Laboratory
                - **Calendar Integration**: icalendar library
                - **Timezone Handling**: pytz library
                
                #### Technical Stack
                - Python
                - Streamlit web framework
                - Additional libraries: csv, datetime
                
                #### Version
                App Version 1.0
                
                #### Contact
                Email: info@livingelectriclanguage.com
                
                #### Privacy
                This application performs all calculations locally in your browser. No user data, location information, or calculation results are stored or collected. All inputs are temporary and are cleared when you close the application.
                
                #### Disclaimer
                This calculator is provided for informational and educational purposes only. While we strive for accuracy in astronomical calculations, users should verify critical timings independently. The creators and contributors of this application are not liable for any decisions, actions, or consequences resulting from the use of this tool.
                
                All calculations are based on the DE421 ephemeris and Skyfield library's implementation. Actual astronomical observations may vary due to local conditions, atmospheric effects, and other factors.
                """)
                
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main() 