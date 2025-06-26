# Phone Number Global Inspector

![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)

A comprehensive Python command-line tool to inspect, enrich, and visualize public data associated with a given phone number. This tool provides detailed insights from number formatting and carrier information to geographical and world context data.


## Features

-   **Detailed Phone Analysis:** Validates the number, identifies its type (Mobile, Fixed Line, etc.), carrier, and displays it in multiple formats (E.164, International, National).
-   **World Context:** Provides country information including Capital City, Currency, Continent/Region, and bordering countries.
-   **Real-time Local Time:** Calculates and displays the current time in the number's primary timezone, perfect for checking international call times.
-   **Geolocation Mapping:** Fetches estimated coordinates for the area code and generates an interactive `folium` map with both street and satellite view layers.
-   **Useful Outputs:** Creates a vCard QR code (`.png`) for easy contact saving and provides a direct "Click-to-Chat" WhatsApp link.
-   **Modern CLI:** Uses the `rich` library for a beautiful and user-friendly command-line interface with formatted tables and panels.
-   **Flexible Input:** Accepts a phone number directly as a command-line argument or via an interactive prompt.

## Requirements

All required libraries are listed in the `requirements.txt` file.

-   Python 3.9+
-   phonenumbers
-   rich
-   qrcode[pil]
-   geopy
-   folium
-   pytz
-   countryinfo

## Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/Mystery-World3/PhoneNumber-Global-Inspector.git
    cd PhoneNumber-Global-Inspector
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    # For Windows
    python -m venv venv
    .\venv\Scripts\Activate.ps1

    # For macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install the required packages:**
    ```bash
    pip install -r requirements.txt
    ```

## Usage

Run the script from your terminal.

#### Provide a number as an argument:
```bash
python main.py "+14155552671"
```

#### Run interactively:
```bash
python main.py
```
The script will then prompt you to enter a phone number.

## Disclaimer

This tool **does not** perform real-time GPS tracking. The location data provided is an estimation based on the public area code associated with the phone number, which often points to the center of a city or country, not the live location of the device.

## License

This project is licensed under the MIT License.

---
*Created by M Mishbahul M*
