import openmeteo_requests
import datetime


class IncreaseSpeed:
    def __init__(self, car, max_speed):
        self.car = car
        self.max_speed = max_speed

    def __iter__(self):
        return self

    def __next__(self):
        if self.car.current_speed >= self.max_speed:
            raise StopIteration
        else:
            self.car.current_speed += 10
            return self.car.current_speed


class DecreaseSpeed:
    def __init__(self, car):
        self.car = car

    def __iter__(self):
        return self

    def __next__(self):
        if self.car.current_speed <= 0:
            raise StopIteration
        else:
            self.car.current_speed -= 10
            return self.car.current_speed


class Car:
    total_cars_on_road = 0

    def __init__(self, max_speed, current_speed=0):
        self.max_speed = max_speed
        self.current_speed = current_speed
        self.state = 'on_road'
        Car.total_cars_on_road += 1

    def accelerate(self, upper_border=None):
        iterator = IncreaseSpeed(self, self.max_speed)
        if upper_border:
            while self.current_speed < upper_border and self.current_speed < self.max_speed:
                try:
                    print(f"Current speed: {next(iterator)} km/h")
                except StopIteration:
                    break
        else:
            self.current_speed += 10
            print(f"Current speed: {self.current_speed} km/h")

    def brake(self, lower_border=None):
        iterator = DecreaseSpeed(self)
        if lower_border:
            while self.current_speed > lower_border:
                try:
                    print(f"Current speed: {next(iterator)} km/h")
                except StopIteration:
                    break
        else:
            self.current_speed -= 10
            print(f"Current speed: {self.current_speed} km/h")

    def parking(self):
        if self.state == 'on_road':
            self.state = 'parked'
            Car.total_cars_on_road -= 1
            print("Car is now parked.")
        else:
            print("Car is already parked.")

    @staticmethod
    def show_weather():
        openmeteo = openmeteo_requests.Client()
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": 59.9386,  # for St.Petersburg
            "longitude": 30.3141,  # for St.Petersburg
            "current": ["temperature_2m", "apparent_temperature", "rain", "wind_speed_10m"],
            "wind_speed_unit": "ms",
            "timezone": "Europe/Moscow"
        }
        response = openmeteo.weather_api(url, params=params)[0]
        current = response.Current()
        current_temperature_2m = current.Variables(0).Value()
        current_apparent_temperature = current.Variables(1).Value()
        current_rain = current.Variables(2).Value()
        current_wind_speed_10m = current.Variables(3).Value()

        print(f"Current time: {datetime.datetime.fromtimestamp(current.Time() + response.UtcOffsetSeconds())} {response.TimezoneAbbreviation().decode()}")
        print(f"Current temperature: {round(current_temperature_2m, 0)} C")
        print(f"Current apparent_temperature: {round(current_apparent_temperature, 0)} C")
        print(f"Current rain: {current_rain} mm")
        print(f"Current wind_speed: {round(current_wind_speed_10m, 1)} m/s")

    @classmethod
    def total_cars(cls):
        print(f"Total cars on road: {cls.total_cars_on_road}")
