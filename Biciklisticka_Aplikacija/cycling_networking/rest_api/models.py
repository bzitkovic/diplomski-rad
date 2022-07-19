class BikeEvent:
    entry_fee: str

    def __init__(self, name, city, date, url):
        self.name = name
        self.city = city
        self.date = date
        self.url = url
