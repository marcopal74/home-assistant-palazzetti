from datetime import timedelta

# The domain of your component. Should be equal to the name of your component.
DOMAIN = "palazzetti"
COMPANY = "Palazzetti Lelio S.p.A."
INTERVAL_KPAL = timedelta(seconds=45)  # Interval for the keep alive loop
INTERVAL = timedelta(seconds=30)  # Interval for check dynamic data
INTERVAL_CNTR = timedelta(seconds=300)  # Interval for check counters
INTERVAL_STDT = timedelta(days=7)  # Interval for check static data
