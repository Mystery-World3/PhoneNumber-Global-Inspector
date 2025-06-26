# -----------------------------------------------------------------------------
# Phone Number Global Inspector
# Final Version: 8.1 - Syntax Corrected
#
# A comprehensive command-line tool to analyze, enrich, and visualize
# public data associated with a given phone number.
# -----------------------------------------------------------------------------

import phonenumbers
from phonenumbers import geocoder, carrier, timezone, phonenumberutil
import argparse
import qrcode
import folium
import pytz
from countryinfo import CountryInfo
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
import time
import os
from datetime import datetime

# --- Initialize Global Components ---
console = Console()
geolocator = Nominatim(user_agent="phone_number_global_inspector_v8")

# Human-readable mappings for phone number types
NUMBER_TYPE_MAP = {
    phonenumberutil.PhoneNumberType.FIXED_LINE: "Fixed Line",
    phonenumberutil.PhoneNumberType.MOBILE: "Mobile",
    phonenumberutil.PhoneNumberType.TOLL_FREE: "Toll-Free",
    phonenumberutil.PhoneNumberType.PREMIUM_RATE: "Premium Rate",
    phonenumberutil.PhoneNumberType.UNKNOWN: "Unknown",
}

def get_coordinates(location_name: str) -> tuple | None:
    """Fetches geographic coordinates (lat, lon) for a given location name."""
    try:
        # Sleep for 1s to comply with Nominatim's fair use policy
        time.sleep(1) 
        location = geolocator.geocode(location_name, language='en')
        return (location.latitude, location.longitude) if location else None
    except (GeocoderTimedOut, GeocoderUnavailable):
        console.print("[bold red]Geocoding service is unavailable or timed out.[/bold red]")
        return None

def get_phone_info(phone_number_str: str) -> dict | str:
    """Analyzes a phone number and returns a dictionary of enriched information."""
    try:
        phone_number_obj = phonenumbers.parse(phone_number_str)

        if not phonenumbers.is_valid_number(phone_number_obj):
            return "❌ Error: Invalid phone number format."

        # --- Basic Information Gathering ---
        e164_format = phonenumbers.format_number(phone_number_obj, phonenumbers.PhoneNumberFormat.E164)
        # Get location in English for reliable geocoding
        location_str = geocoder.description_for_number(phone_number_obj, "en")
        
        info = {
            "E.164 Format": e164_format,
            "International Format": phonenumbers.format_number(phone_number_obj, phonenumbers.PhoneNumberFormat.INTERNATIONAL),
            "National Format": phonenumbers.format_number(phone_number_obj, phonenumbers.PhoneNumberFormat.NATIONAL) or "N/A",
            "Number Type": NUMBER_TYPE_MAP.get(phonenumberutil.number_type(phone_number_obj), "Other"),
            "Area Code Location": location_str if location_str else "N/A",
            # Get carrier name in its local language for better results
            "Mobile Carrier": carrier.name_for_number(phone_number_obj, "en") or "N/A",
        }

        # --- Timezone & Local Time Enrichment ---
        timezone_list = timezone.time_zones_for_number(phone_number_obj)
        if timezone_list:
            try:
                first_timezone = timezone_list[0]
                local_time = datetime.now(pytz.timezone(first_timezone))
                info["Current Local Time"] = local_time.strftime('%A, %Y-%m-%d, %H:%M:%S %Z%z')
            except pytz.UnknownTimeZoneError:
                info["Current Local Time"] = "Invalid timezone data."
        
        # --- Country Information Enrichment ---
        country_code = phonenumbers.region_code_for_number(phone_number_obj)
        if country_code:
            try:
                country_data = CountryInfo(country_code).info()
                info["Country"] = f"{country_data.get('name')} ({country_code})"
                info["Capital City"] = country_data.get('capital')
                info["Currency"] = f"{country_data.get('currencies')[0]}"
                info["Continent / Region"] = country_data.get('region')
                info["Bordering Countries"] = ", ".join(country_data.get('borders')) if country_data.get('borders') else "None"
            except (KeyError, IndexError):
                 info["Country Info"] = "Could not retrieve."

        # --- Geolocation Enrichment ---
        if location_str:
            coords = get_coordinates(location_str)
            if coords:
                info["Latitude"] = f"{coords[0]:.4f}"
                info["Longitude"] = f"{coords[1]:.4f}"
                info["Google Maps Link"] = f"https://maps.google.com/maps?q={coords[0]},{coords[1]}"

        # --- Utility Links ---
        info["WhatsApp Link"] = f"https://wa.me/{e164_format.replace('+', '')}"
        
        return info

    except phonenumbers.phonenumberutil.NumberParseException:
        return f"❌ Error: Failed to parse '{phone_number_str}'. Please check the format."
    except Exception as e:
        return f"❌ An unexpected error occurred: {e}"

def create_qr_code(info: dict):
    """Creates a vCard QR code and saves it as a PNG file."""
    e164_format = info.get("E.164 Format")
    if not e164_format: return
    
    vcard_str = f"BEGIN:VCARD\nVERSION:3.0\nFN:{e164_format}\nTEL;TYPE=CELL:{e164_format}\nEND:VCARD"
    qr = qrcode.QRCode(version=1, box_size=10, border=2)
    qr.add_data(vcard_str)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    img_filename = f"contact_{e164_format}.png"
    img.save(img_filename)
    console.print(f"✅ [bold green]Contact QR Code saved as '{img_filename}'[/bold green]")

def create_location_map(info: dict):
    """Creates an interactive map with satellite view and saves it as an HTML file."""
    if "Latitude" not in info or "Longitude" not in info:
        return
        
    lat, lon = float(info["Latitude"]), float(info["Longitude"])
    location_map = folium.Map(location=[lat, lon], zoom_start=11)
    
    # Add multiple tile layers for different map views
    folium.TileLayer('OpenStreetMap').add_to(location_map)
    folium.TileLayer(
        'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr='Esri', name='Satellite View'
    ).add_to(location_map)
    
    # Add a marker with a descriptive popup
    popup_html = f"<b>{info.get('Area Code Location')}</b><br><i>Estimated location for {info.get('International Format')}</i>"
    folium.Marker([lat, lon], popup=popup_html).add_to(location_map)
    
    # Add a layer control button to switch between map views
    folium.LayerControl().add_to(location_map)
    
    html_filename = f"map_{info.get('E.164 Format')}.html"
    location_map.save(html_filename)
    console.print(f"✅ [bold blue]Interactive Map saved as '{html_filename}'[/bold blue]")

def display_results(result: dict | str):
    """Displays the analysis results in a formatted table or shows an error panel."""
    if isinstance(result, str):
        console.print(Panel(result, title="[bold red]Error[/bold red]", border_style="red"))
    elif isinstance(result, dict):
        result_table = Table(title="✨ Phone Number Analysis Results", border_style="cyan", show_header=True, header_style="bold magenta")
        result_table.add_column("Attribute", style="dim", width=25)
        result_table.add_column("Information")
        for key, value in result.items():
            result_table.add_row(key, str(value))
        
        console.print(result_table)
        console.print("--- [bold]Generated Outputs[/bold] " + "-"*50)
        create_location_map(result)
        create_qr_code(result)
        console.print("[dim i]Disclaimer: The map shows the geographical center of the AREA CODE, not a real-time GPS location.[/dim i]")

if __name__ == "__main__":
    # Clear the terminal screen on startup for a clean look
    os.system('cls' if os.name == 'nt' else 'clear') 
    
    # Set up command-line argument parsing
    parser = argparse.ArgumentParser(description="A comprehensive tool to inspect a phone number.")
    parser.add_argument("number", nargs="?", default=None, help="The phone number to analyze (optional).")
    args = parser.parse_args()

    # Print a nice title panel
    console.print(Panel(
        Text("Ultimate Edition v8.1", justify="center", style="bold yellow"),
        title="[bold blue]Phone Number Global Inspector[/bold blue]",
        subtitle="[dim]By M Mishbahul M[/dim]"
    ))

    # Determine which number to analyze
    number_to_analyze = args.number
    if not number_to_analyze:
        number_to_analyze = console.input("[bold yellow]➡️ Enter a phone number (e.g., +14155552671): [/bold yellow]")

    # Run the analysis if a number was provided
    if not number_to_analyze:
        console.print("[bold red]No number was provided. Exiting program.[/bold red]")
    else:
        # Show a status spinner while processing
        with console.status("[bold yellow]Analyzing...[/bold yellow]"):
            analysis_result = get_phone_info(number_to_analyze)
        
        display_results(analysis_result)