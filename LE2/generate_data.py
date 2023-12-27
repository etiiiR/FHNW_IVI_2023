import pandas as pd
import random

def generate_synthetic_car_data(num_rows):
    car_brands = ['Toyota', 'Ford', 'BMW', 'Mercedes', 'Volkswagen', 'Honda', 'Nissan']
    car_models = ['Model A', 'Model B', 'Model C', 'Model D', 'Model E']

    data = []
    for _ in range(num_rows):
        brand = random.choice(car_brands)
        model = random.choice(car_models)
        speed = random.randint(100, 250)  # Geschwindigkeit in km/h
        acceleration = round(random.uniform(2.0, 10.0), 2)  # Beschleunigung in s von 0 auf 100 km/h
        price = random.randint(20000, 80000)  # Preis in Euro
        age = random.randint(0, 20)  # Alter in Jahren
        fuel_consumption = round(random.uniform(5.0, 15.0), 2)  # Spritverbrauch in l/100km

        data.append([f'{brand} {model}', brand, speed, acceleration, price, age, fuel_consumption])

    columns = ['Auto Name', 'Markenname', 'Geschwindigkeit', 'Beschleunigung', 'Preis', 'Alter', 'Spritverbrauch']
    return pd.DataFrame(data, columns=columns)

# Erstellen des DataFrames
synthetic_car_df = generate_synthetic_car_data(100)
