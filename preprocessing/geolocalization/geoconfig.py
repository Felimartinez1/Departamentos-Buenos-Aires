from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

geolocator = Nominatim(user_agent="geoapi_powerbi")
geocode = RateLimiter(
    lambda query: geolocator.geocode(query, country_codes='ar', timeout=3),
    min_delay_seconds=1,
    max_retries=3,
    error_wait_seconds=2.0
)