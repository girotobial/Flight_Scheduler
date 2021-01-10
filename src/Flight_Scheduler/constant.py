from pathlib import Path

VERSION = 1.7
FLIGHT_SCHEDULER_DIR = Path(__file__).parent.absolute()
ICON_PATH = str(FLIGHT_SCHEDULER_DIR / "resources" / "Icon.ico")

TABLE_HEADERS = ["Airline", "From", "To", "Aircraft"]

DATABASE_PATH = "/FlightDBv2.db"
