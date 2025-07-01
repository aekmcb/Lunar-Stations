"""
Lunar Stations Calculator (Streamlit App Version)
Copyright (c) 2025 Living Electric Language LLC
Licensed under the MIT License - see LICENSE file for details
"""

import streamlit as st
import csv
from skyfield.api import Topos, load
from datetime import datetime, timedelta
import pytz
from icalendar import Calendar, Event, Alarm
import os
import psutil
import time

def check_timeout(start_time, max_seconds=300):
    """Check if calculation has exceeded timeout"""
    if time.time() - start_time > max_seconds:
        raise TimeoutError("Calculation timed out")

def validate_lunar_station_sequence(results):
    """Validate that lunar stations appear in sequential order"""
    if not results:
        return
    
    # Extract station numbers from results
    station_numbers = []
    for _, ls, _, _ in results:
        # Extract number from "1#LS", "2#LS", etc.
        try:
            num = int(ls.split('#')[0])
            station_numbers.append(num)
        except (ValueError, IndexError):
            continue
    
    if len(station_numbers) < 2:
        return
    
    # Check for gaps in sequence
    gaps = []
    for i in range(len(station_numbers) - 1):
        current = station_numbers[i]
        next_station = station_numbers[i + 1]
        
        # Handle wraparound from 28 to 1
        if current == 28 and next_station == 1:
            continue
        elif current == 1 and next_station == 28:
            continue
        elif next_station != current + 1:
            gaps.append(f"Missing station between {current}#LS and {next_station}#LS")
    
    if gaps:
        raise Exception(f"Lunar station sequence validation failed: {'; '.join(gaps)}")

# Define lunar stations data (same as original)
LUNAR_STATIONS = {
    50.7833: ("3#LS", "Eta Tauri (Alcyone); 27 Tauri (Atlas); 17 Tauri (Electra); 20 Tauri (Maia):  Pleiades"),
    64.1167: ("4#LS", "Epsilon Tauri (Ain); Delta Tauri; Alpha Tauri: Taurus face where Aldebaran is 0.3° outside of Moon orbital range"),
    77.45: ("5#LS", "Zeta Tauri:  Taurus horn in Milky Way"),
    90.7833: ("6#LS", "Eta Geminorum (Propus); Mu Geminorum (Tejat); Epsilon Geminorum (Mebsuta): Foot&Legs of Castor in Milkyway"),
    104.1167: ("7#LS", "Delta Geminorum (Wasat); Kappa Geminorum: Torso of Pollux"),
    117.45: ("8#LS", "Delta Cancri (Asellus Australis); Gamma Cancri (Ascellus Borealis):  Goal Posts of Praesepe (low visibility) in Cancer"),
    130.7833: ("9#LS", "Alpha Cancer (Acubens):  Claw of Cancer"),
    144.1167: ("10#LS", "Alpha Leonis (Regulus); Eta Leonis, Omnicron Leonis (Subra); Rho Leonis: Front Lower section of Leo"),
    157.45: ("11#LS", "Sigma Leonis; Chi Leonis: Back legs of Leo"),
    170.7833: ("12#LS", "Beta Virginis (Zavijava); Nu Virginis:  Head of Virgo"),
    184.1167: ("13#LS", "Gamma Virginis (Porrima); Eta Virginis (Zaniah): Arm of Virgo"),
    197.45: ("14#LS", "Alpha Virginis (Spica): Hand of Virgo"),
    210.7833: ("15#LS", "Kappa Virginis (Kang); Lambda Virginis:  Hemline of Virgo"),
    224.1167: ("16#LS", "Alpha Librae (Zubenelgenubi II); Gamma Librae:  Fulcrum of Libra"),
    237.45: ("17#LS", "Alpha Scorpii (Antares); Delta Scorpii (Dschubba); Beta Scorpii (Acrab); Sigma Scorpii (Alniyat); Omega Scorpii:  Tip of Scorpio claw; Base of claw+Antares in Milky Way where Antares is 1° before start of LS#18"),
    250.7833: ("18#LS", "Theta Ophiuchi: Leg of Ophiuchus in Milky Way"),
    264.1167: ("19#LS", "Lambda Sagittarii (Kaus Borealis); Mu Sagittarii: Head of Sagittarius in Milky Way"),
    277.45: ("20#LS", "Sigma Sagittarii (Nunki); Pi Sagittarii (Albaldah); Phi Sagittarii; Tau Sagittarii; Xi2 Sagittarii; Omnicron Sagittarii; Rho Sagittarii: Arm+Cape of Sagittarius in Milky Way"),
    290.7833: ("21#LS", "H2 Sagittarii:  Rear end of Sagittarius"),
    300.6167: ("22#LS", "Beta Capricorni (Dabih) in Moon Orbit:  Memory Stars Ursa Major from Alkaid to Dubhe+Mirfak (Perseus) in North; Southern Cross in South"),
    305.6167: ("23#LS", "Theta Capricorni (Dorsum):  Back of Capricorn (HIP 104139)"),
    317.45: ("24#LS", "Delta Capricorni (Deneb Algedi); Gamma Capricorni (Nashira): Tail fin of Capricorn"),
    330.7833: ("25#LS", "Lambda Aquarii (Hydor); Theta Aquarii (Ancha):  Abs+Water of Aquarius"),
    344.1166: ("26#LS", "Phi Aquarii; Psi1 Aquarii:  Water of Aquarius"),
    357.45: ("27#LS", "27 Piscium: Faint star on tail of Cetus (HIP 118209)"),
    10.7833: ("28#LS", "Epsilon Piscium; Delta Piscium:  Longer connection thread for Pisces"),
    24.1167: ("1#LS", "Nu Piscium; Omicron Piscium; Xi1 Ceti: V part of connection thread for Pisces + Face fin of Cetus"),
    37.45: ("2#LS", "Epsilon Arietis: Hind leg of Aries")
}

def check_memory_usage():
    """Monitor memory usage and return True if within safe limits"""
    try:
        memory = psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024  # MB
        return memory < 800  # More conservative limit: 800MB instead of 1GB
    except Exception:
        # If we can't check memory, assume it's okay but log it
        return True

def validate_time_range(start_datetime, end_datetime):
    """Validate time range and return error message if invalid"""
    if end_datetime <= start_datetime:
        return "End time must be after start time"
    
    time_span = end_datetime - start_datetime
    if time_span > timedelta(days=31):
        return "Time span cannot exceed 31 days (1 month)"
    
    return None

def calculate_lunar_stations(lat_deg, lat_dir, lon_deg, lon_dir, timezone, start_time, end_time, include_alerts=False):
    """Main calculation function with optimized memory usage and chunked processing"""
    try:
        # Start timing for timeout check
        start_calc_time = time.time()
        # Set timezone
        local_tz = pytz.timezone(timezone)
        
        # Load ephemeris data
        try:
            ts = load.timescale()
            planets = load('de421.bsp')
        except Exception as e:
            raise Exception(f"Failed to load ephemeris data: {str(e)}")
        
        earth, moon = planets['earth'], planets['moon']
        
        # Calculate positions from observer's location (topocentric)
        location = Topos(f'{lat_deg} {lat_dir}', f'{lon_deg} {lon_dir}')
        my_position = earth + location
        
        # Calculate time span and limit to 1 month maximum
        time_span = end_time - start_time
        if time_span > timedelta(days=31):
            raise Exception("Time span cannot exceed 31 days (1 month)")
        
        # Use 1-minute intervals for all periods to ensure no lunar stations are missed
        # Lunar stations can vary from ~5 hours to 28 hours, so we need fine sampling
        chunk_size = timedelta(days=1)  # 1-day chunks to manage memory
        fine_step = timedelta(minutes=1)  # Always use 1-minute intervals for accuracy
        
        # Process in chunks to manage memory
        all_sorted_matches = []
        current_chunk_start = start_time
        
        while current_chunk_start < end_time:
            # Check for timeout
            check_timeout(start_calc_time, 300)  # 5-minute timeout
            
            if not check_memory_usage():
                raise Exception("Memory usage exceeded safe limits")
            
            current_chunk_end = min(current_chunk_start + chunk_size, end_time)
            
            # Generate 1-minute time points for this chunk
            fine_time_points = []
            current = current_chunk_start
            while current <= current_chunk_end:
                fine_time_points.append(current)
                current += fine_step
            
            if not fine_time_points:
                current_chunk_start = current_chunk_end
                continue
            
            # Step 3: Fine scanning for precise lunar station crossings
            fine_times = ts.from_datetimes(fine_time_points)
            fine_positions = my_position.at(fine_times).observe(moon).apparent()
            fine_ecl_positions = fine_positions.ecliptic_latlon(epoch='date')
            fine_longitudes = fine_ecl_positions[1].degrees % 360
            fine_latitudes = fine_ecl_positions[0].degrees
            
            # Step 4: Find exact lunar station crossings
            chunk_matches = {lon: [] for lon in LUNAR_STATIONS.keys()}
            
            for lon_target in LUNAR_STATIONS.keys():
                min_difference = float('inf')
                min_time = None
                min_lon = None
                min_lat = None
                last_difference = float('inf')
                
                for i, lon in enumerate(fine_longitudes):
                    difference = min(
                        abs(lon - lon_target),
                        abs(lon - lon_target + 360),
                        abs(lon - lon_target - 360)
                    )
                    
                    if difference < 0.008:  # Within ~0.5 arcminute
                        if difference < min_difference:
                            min_difference = difference
                            min_time = fine_time_points[i]
                            min_lon = lon
                            min_lat = fine_latitudes[i]
                            
                    elif last_difference < 0.008 and min_time is not None:
                        chunk_matches[lon_target].append((min_time, min_lon, min_lat))
                        min_difference = float('inf')
                        min_time = None
                        min_lon = None
                        min_lat = None
                    
                    last_difference = difference
                
                if min_time is not None:
                    chunk_matches[lon_target].append((min_time, min_lon, min_lat))
            
            # Add chunk results to overall results
            for lon_target, matches in chunk_matches.items():
                ls, _ = LUNAR_STATIONS[lon_target]
                for match_time, lon, lat in matches:
                    all_sorted_matches.append((match_time, ls, lon, lat))
            
            # Move to next chunk
            current_chunk_start = current_chunk_end
        
        # Sort all results by time
        all_sorted_matches.sort(key=lambda x: x[0])
        
        # Validate that we have sequential lunar station transitions
        validate_lunar_station_sequence(all_sorted_matches)
        
        return all_sorted_matches

    except Exception as e:
        raise Exception(f"Calculation error: {str(e)}")

def save_to_csv(results, timezone, filename="lunar_stations.csv", include_longitude=True, include_latitude=True, include_description=True):
    """Save results to CSV file"""
    try:
        local_tz = pytz.timezone(timezone)
        
        with open(filename, 'w', newline='') as file:
            writer = csv.writer(file)
            # Create header based on selected columns
            header = ['Time (Local)', 'Lunar_Station']
            if include_longitude:
                header.append('Ecliptic_Longitude')
            if include_latitude:
                header.append('Ecliptic_Latitude')
            if include_description:
                header.append('Station_Description')
            writer.writerow(header)
            
            for match_time, ls, topo_lon, topo_lat in results:
                # Get the description for this station
                station_desc = ""
                if include_description:
                    for lon, (station, desc) in LUNAR_STATIONS.items():
                        if station == ls:
                            station_desc = desc
                            break
                
                local_time = match_time.replace(tzinfo=pytz.UTC).astimezone(local_tz)
                formatted_time = local_time.strftime('%Y-%m-%d %H:%M:%S')
                
                # Create row based on selected columns
                row = [formatted_time, ls]
                if include_longitude:
                    row.append(f"{topo_lon:.2f}")
                if include_latitude:
                    row.append(f"{topo_lat:.2f}")
                if include_description:
                    row.append(station_desc)
                
                writer.writerow(row)
        
        print(f"Results saved to {filename}")
    except Exception as e:
        raise Exception(f"CSV generation error: {str(e)}")

def save_to_ics(results, timezone, include_alerts, filename="lunar_stations.ics", include_longitude=True, include_latitude=True, include_description=True):
    """Save results to ICS file"""
    try:
        cal = Calendar()
        cal.add('prodid', '-//Lunar Station Calculator//example.com//')
        cal.add('version', '2.0')
        local_tz = pytz.timezone(timezone)

        for match_time, ls, topo_lon, topo_lat in results:
            # Get the description for this station
            station_desc = ""
            if include_description:
                for lon, (station, desc) in LUNAR_STATIONS.items():
                    if station == ls:
                        station_desc = desc
                        break
                    
            local_time = match_time.replace(tzinfo=pytz.UTC).astimezone(local_tz)
            event = Event()
            event.add('summary', f'Lunar Station {ls}')
            event.add('dtstart', local_time)
            event.add('dtend', local_time + timedelta(minutes=30))
            
            # Build description based on selected columns
            desc_parts = [f'Lunar Station {ls}']
            if include_longitude:
                desc_parts.append(f'Ecliptic Longitude: {topo_lon:.2f}°')
            if include_latitude:
                desc_parts.append(f'Ecliptic Latitude: {topo_lat:.2f}°')
            if include_description:
                desc_parts.append(f'Stars: {station_desc}')
            
            event.add('description', '\n'.join(desc_parts))
            
            if include_alerts:
                alarm = Alarm()
                alarm.add('action', 'DISPLAY')
                alarm.add('description', f'Lunar Station {ls} - {station_desc if include_description else ""}')
                alarm.add('trigger', timedelta(minutes=0))
                event.add_component(alarm)
            
            cal.add_component(event)

        with open(filename, 'wb') as f:
            f.write(cal.to_ical())
        
        print(f"Calendar events saved to {filename}")
    except Exception as e:
        raise Exception(f"ICS generation error: {str(e)}")
  
def main():    
    st.title("Lunar Stations Calculator")
    
    st.markdown("""
    This simple app tracks in real time the Moon's movement through the *ecliptic pathway* of stars based on your location. 

    Throughout history, astrologers from Arabic, Vedic, and Chinese traditions track the Moon's journey across the ecliptic by dividing the circle into 27-28 sections. These are marked by distinctive star patterns. These celestial waypoints became known as *Lunar Stations*. You can follow the Moon across this time-worn celestial trail with the modern assistance of this app.

    The Lunar Station starting locations in this app are based the precessed tropical coordinates found in J.M. Hamade's '*Procession of the Night Theatre*' (Revelore Press, 2024). This is an excellent and inspiring resource on the Lunar Stations across cultures.
    """)
    
    # Location Input
    st.header("Location")
    col1, col2 = st.columns(2)
    
    with col1:
        lat_deg = st.number_input("Latitude Degrees", min_value=0.0, max_value=90.0, value=0.0, step=0.0001)
        lat_dir = st.radio("Latitude Direction", ["N", "S"])
    
    with col2:
        lon_deg = st.number_input("Longitude Degrees", min_value=0.0, max_value=180.0, value=0.0, step=0.0001)
        lon_dir = st.radio("Longitude Direction", ["E", "W"])
    
    st.markdown("""
    Enter your location information for which you want to calculate the Lunar Stations:
    * Latitude (0 to 90) - Select N for Northern or S for Southern Hemisphere
    * Longitude (0 to 180)- Select E for Eastern or W for Western Hemisphere
    """)
    
    # Timezone Selection
    st.header("Timezone")
    timezones = sorted(pytz.all_timezones)
    timezone = st.selectbox("Select your timezone", timezones)
    
    st.markdown("""
    * Select the city that best represents your time zone
    * Example: For US Eastern Time, choose 'America/New_York'
    * Example: For UK Time, choose 'Europe/London'
    * Times will automatically adjust for Daylight Saving Time (DST)
    """)
    
    # Date Range Selection
    st.header("Date Range (up to 31 days)")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Start Date")
        start_year = st.number_input("Start Year", min_value=1900, max_value=2100, value=datetime.now().year)
        start_month = st.number_input("Start Month", min_value=1, max_value=12, value=datetime.now().month)
        start_day = st.number_input("Start Day", min_value=1, max_value=31, value=datetime.now().day)
    
    with col2:
        st.subheader("End Date")
        end_year = st.number_input("End Year", min_value=1900, max_value=2100, value=datetime.now().year)
        end_month = st.number_input("End Month", min_value=1, max_value=12, value=datetime.now().month)
        end_day = st.number_input("End Day", min_value=1, max_value=31, value=datetime.now().day)
    
    # Output Format Selection
    st.header("Output Format")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **CSV file**
        * Can be imported into spreadsheets (Excel, Google Sheets)
        * Works with Notion databases
        * Simple text format for data analysis
        """)
    
    with col2:
        st.markdown("""
        **ICS file**
        * Imports directly into calendar apps
        * Works with Google Calendar, Apple Calendar, Outlook
        * Optional alerts for station changes
        """)
    
    output_format = st.radio("Select output format", ["CSV", "ICS"], horizontal=True, label_visibility="collapsed")
    
    include_alerts = False
    if output_format == "ICS":
        include_alerts = st.checkbox("Include calendar alerts for ICS file")
    
    # Column Selection
    st.subheader("Optional Information")
    col1, col2, col3 = st.columns(3)
    with col1:
        include_longitude = st.checkbox("Ecliptic Longitude", value=True)
    with col2:
        include_latitude = st.checkbox("Ecliptic Latitude", value=True)
    with col3:
        include_description = st.checkbox("Station Description", value=True)
    
    st.markdown("""
    Your output file can include:
    * Ecliptic longitude of the Moon at the start of the Lunar Station (converted zodiacal locations) based on your viewing location and Lunar Station time
    * Ecliptic latitude of the Moon at the start of the Lunar Station based on your viewing location and Lunar Station time
      (Note: The Moon's ecliptic latitude will naturally vary by approximately ±1.25° 
      during each Lunar Station)
    * Station description listing the bright stars (mostly 4 or brighter with a few dimmer stars if needed) 
      that the Moon encounters along the ecliptic (within ±5.145° of the ecliptic as 
      measured from the Earth-Moon barycenter). Most of these marker stars are visible 
      from both Northern and Southern hemispheres.
    """)
    
    # Create datetime objects
    start_datetime = datetime(start_year, start_month, start_day, 0, 0)
    end_datetime = datetime(end_year, end_month, end_day, 23, 59)
    
    # Validate time range
    error_message = validate_time_range(start_datetime, end_datetime)
    if error_message:
        st.error(f"Error: {error_message}")
        return
    
    # Convert to UTC
    local_tz = pytz.timezone(timezone)
    start_datetime = local_tz.localize(start_datetime).astimezone(pytz.UTC)
    end_datetime = local_tz.localize(end_datetime).astimezone(pytz.UTC)
    
    # Calculate Button
    st.markdown("""
    #### Privacy Policy
    This application runs on Streamlit's platform. While calculations are performed server-side:
    - No user data or calculation results are permanently stored
    - Session data is temporarily cached during use and cleared upon closing
    - Location inputs and results are not collected or retained
    - No personal information is tracked or stored
    
    For more information about Streamlit's data handling, please visit 
    their privacy policy at https://streamlit.io/privacy-policy
    """)
    
    privacy_acknowledged = st.checkbox("I acknowledge and agree to the privacy policy", value=False)
    
    if not privacy_acknowledged:
        st.warning("Please acknowledge the privacy policy to proceed with the calculation.")
        return
    
    # Add warnings for potentially problematic calculations
    time_span_days = (end_datetime - start_datetime).days
    if time_span_days > 14:
        st.info(f"📅 **Date Range**: You've selected {time_span_days} days. The app uses 1-minute precision to ensure all lunar station transitions are captured.")
    
    if start_datetime < datetime.now(pytz.UTC) - timedelta(days=7):
        st.info("📅 **Past Dates**: Calculating for past dates uses the same high-precision method to ensure accuracy.")
    
    st.markdown("**Please be patient. Because the Lunar Station start times are location specific, the calculation may take a few minutes.**")
    
    if st.button("Calculate the Lunar Stations"):
        # Create progress indicators
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            status_text.text("Initializing calculation...")
            progress_bar.progress(10)
            
            status_text.text("Loading ephemeris data...")
            progress_bar.progress(20)
            
            results = calculate_lunar_stations(
                lat_deg, lat_dir, lon_deg, lon_dir, timezone, 
                start_datetime, end_datetime, include_alerts
            )
            
            progress_bar.progress(90)
            status_text.text("Finalizing results...")
            
            if output_format == "CSV":
                filename = "lunar_stations.csv"
                save_to_csv(results, timezone, filename, include_longitude, include_latitude, include_description)
                with open(filename, "rb") as file:
                    st.download_button(
                        label="Download CSV",
                        data=file,
                        file_name=filename,
                        mime="text/csv"
                    )
            else:
                filename = "lunar_stations.ics"
                save_to_ics(results, timezone, include_alerts, filename, include_longitude, include_latitude, include_description)
                with open(filename, "rb") as file:
                    st.download_button(
                        label="Download ICS",
                        data=file,
                        file_name=filename,
                        mime="text/calendar"
                    )
            
            progress_bar.progress(100)
            status_text.text("Complete!")
            st.success("Calculation complete! Click the download button above to get your results.")
            
            st.markdown("""
            #### Disclaimer
            This calculator is provided for informational and educational purposes only. While we strive for accuracy in astronomical calculations, users should verify critical timings independently. The creators and contributors of this application are not liable for any decisions, actions, or consequences resulting from the use of this tool.
            
            All calculations are based on the DE421 ephemeris and Skyfield library's implementation. Actual astronomical observations may vary due to local conditions, atmospheric effects, and other factors.
            
            #### Additional Credits
            - **Astronomical Calculations**: [Skyfield](https://rhodesmill.org/skyfield/) by Brandon Rhodes
            - **Ephemeris Data**: DE421 from NASA's Jet Propulsion Laboratory
            - **Calendar Integration**: icalendar library for ICS file generation
            - **Timezone Handling**: pytz library for accurate time conversions
            
            #### Star Data Acknowledgment
            The station descriptions in this program were prepared using the Hipparcos Catalogue 
            (ESA, 1997) to identify and verify the bright stars (5 or brighter) along the Moon's path. 
            This identification process was done separately from this program, and the 
            resulting descriptions were incorporated into the program's database.
            
            #### Technical Stack
            - Python 3.x
            - Streamlit web framework
            - Skyfield (astronomical calculations)
            - pytz (timezone handling)
            - icalendar (calendar integration)
            - pandas & numpy (data processing)
            - Additional libraries: csv, datetime
            
            #### Version
            App Version 1.3, Updated 2025-07-01
            
            #### Contact
            Email: info@livingelectriclanguage.com
            """)
            
        except TimeoutError:
            progress_bar.progress(0)
            status_text.text("Calculation timed out")
            st.error("The calculation took too long and was cancelled. Please try a shorter time period or contact support if the problem persists.")
        except Exception as e:
            progress_bar.progress(0)
            status_text.text("Error occurred")
            st.error(f"An error occurred: {str(e)}")
            st.info("If you're calculating for a long time period or past dates, try reducing the date range to 14 days or less.")

if __name__ == "__main__":
    main()

