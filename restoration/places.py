"""Recording cities that appear in the selected LoC records (city-level only).

`loc` is the lower-case city string as it appears in the LoC `location` field.
Coordinates are city centres; no studio addresses are implied.
`us` marks places under US jurisdiction (Puerto Rico included), where the
US public-domain assessment is the home-country assessment.
"""
CITIES = {
    "New York": {"loc": "new york", "country": "United States", "us": True, "lat": 40.7128, "lon": -74.0060},
    "Camden": {"loc": "camden", "country": "United States", "us": True, "lat": 39.9259, "lon": -75.1196},
    "Philadelphia": {"loc": "philadelphia", "country": "United States", "us": True, "lat": 39.9526, "lon": -75.1652},
    "Chicago": {"loc": "chicago", "country": "United States", "us": True, "lat": 41.8781, "lon": -87.6298},
    "San Juan": {"loc": "san juan", "country": "Puerto Rico", "us": True, "lat": 18.4655, "lon": -66.1057},
    "Mexico City": {"loc": "mexico city", "country": "Mexico", "lat": 19.4326, "lon": -99.1332},
    "Havana": {"loc": "havana", "country": "Cuba", "lat": 23.1136, "lon": -82.3666},
    "Caracas": {"loc": "caracas", "country": "Venezuela", "lat": 10.4806, "lon": -66.9036},
    "Lima": {"loc": "lima", "country": "Peru", "lat": -12.0464, "lon": -77.0428},
    "Santiago": {"loc": "santiago", "country": "Chile", "lat": -33.4489, "lon": -70.6693},
    "Buenos Aires": {"loc": "buenos aires", "country": "Argentina", "lat": -34.6037, "lon": -58.3816},
    "Rio de Janeiro": {"loc": "rio de janeiro", "country": "Brazil", "lat": -22.9068, "lon": -43.1729},
    "London": {"loc": "london", "country": "United Kingdom", "lat": 51.5072, "lon": -0.1276},
    "Paris": {"loc": "paris", "country": "France", "lat": 48.8566, "lon": 2.3522},
    "Milan": {"loc": "milan", "country": "Italy", "lat": 45.4642, "lon": 9.1900},
    "Berlin": {"loc": "berlin", "country": "Germany", "lat": 52.5200, "lon": 13.4050},
    "Madrid": {"loc": "madrid", "country": "Spain", "lat": 40.4168, "lon": -3.7038},
    "St. Petersburg": {"loc": "st. petersburg", "country": "Russia", "lat": 59.9311, "lon": 30.3609},
    "Bogotá": {"loc": "bogotá", "country": "Colombia", "lat": 4.7110, "lon": -74.0721},
    "Guayaquil": {"loc": "guayaquil", "country": "Ecuador", "lat": -2.1710, "lon": -79.9224},
    "Arequipa": {"loc": "arequipa", "country": "Peru", "lat": -16.4090, "lon": -71.5375},
    "La Paz": {"loc": "la paz", "country": "Bolivia", "lat": -16.4897, "lon": -68.1193},
    "Tokyo": {"loc": "tokyo", "country": "Japan", "lat": 35.6762, "lon": 139.6503},
    "Osaka": {"loc": "osaka", "country": "Japan", "lat": 34.6937, "lon": 135.5023},
}

# Country-level entries, used only when the LoC record names a country but no city.
# The map highlights the whole country (shape = world-atlas name); no point is invented.
REGIONS = {
    "Japan (city not recorded)": {"loc": "japan", "country": "Japan", "shape": "Japan", "lat": 37.5, "lon": 137.5, "region": True},
}


def city_from_loc(locations):
    """Pick the city from an LoC location list such as ['mexico city', 'mexico']."""
    locs = [x.lower() for x in locations or []]
    # 'new york' is both a city and a state in LoC records; prefer more specific cities first
    for name, c in sorted(CITIES.items(), key=lambda kv: kv[0] == "New York"):
        if c["loc"] in locs:
            return name
    for name, c in REGIONS.items():
        if c["loc"] in locs:
            return name
    return None


def place(name):
    """City or region record for a name returned by city_from_loc."""
    return CITIES.get(name) or REGIONS[name]
