# Module 1: Meteo API

import requests
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from time import sleep
from typing import Dict, Any

# Datos
api_url = "https://archive-api.open-meteo.com/v1/archive?"

coordinates = {
    "Madrid": {"latitude": 40.416775, "longitude": -3.703790},
    "London": {"latitude": 51.507351, "longitude": -0.127758},
    "Rio": {"latitude": -22.906847, "longitude": -43.172896},
}

variables = ["temperature_2m_mean", "precipitation_sum", "wind_speed_10m_max"]


def call_api(url: str, params: Dict[str, Any]):

    # Primer intento
    response = requests.get(url, params=params)

    if response.status_code == 200:
        return response.json()

    # Si falla identificar tipo de error
    if response.status_code == 429:
        print("Rate limit detectado")
        sleep(3)
    else:
        print(f" Error: Status Code {response.status_code}")

    # Segundo intento
    print("Reintentando...")
    response = requests.get(url, params=params)

    if response.status_code == 200:
        return response.json()

    # Si falla dos veces lanzamos el error

    raise Exception(f"Error en API: Status Code {response.status_code}")


def get_data_meteo_api(
    city: str, start_date: str = "2010-01-01", end_date: str = "2020-12-31"
) -> pd.DataFrame:

    # Obtener coordenadas
    if city not in coordinates:
        raise ValueError(f"Ciudad '{city}' no encontrada en Coordinates")

    coords = coordinates[city]
    latitude = coords["latitude"]
    longitude = coords["longitude"]

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": start_date,
        "end_date": end_date,
        "daily": ["temperature_2m_mean", "precipitation_sum", "wind_speed_10m_max"],
        "timezone": "auto",
    }

    # Llamar a la API
    data = call_api(api_url, params)

    # Crear DataFrame
    df = pd.DataFrame(
        {
            "date": pd.to_datetime(data["daily"]["time"]),
            "temperature": data["daily"]["temperature_2m_mean"],
            "precipitation": data["daily"]["precipitation_sum"],
            "wind_speed": data["daily"]["wind_speed_10m_max"],
            "city": city,
        }
    )

    return df


def process_data_to_monthly(df: pd.DataFrame) -> pd.DataFrame:

    df["year_month"] = df["date"].dt.to_period("M")

    df_monthly = (
        df.groupby(["city", "year_month"])
        .agg({"temperature": "mean", "precipitation": "sum", "wind_speed": "max"})
        .reset_index()
    )

    df_monthly["date"] = df_monthly["year_month"].dt.to_timestamp()

    df_monthly = df_monthly.drop("year_month", axis=1)

    return df_monthly


def plot_weather_data(df: pd.DataFrame):
    fig, ax = plt.subplots(3, 1, figsize=(14, 12))
    fig.suptitle("Evolución Meteorológica 2010-2020 (Datos Mensuales)", fontsize=14)

    cities = df["city"].unique()

    # Gráfico Temperatura
    for city in cities:
        df_city = df[df["city"] == city]
        ax[0].plot(df_city["date"], df_city["temperature"], label=city, linewidth=0.8)
    ax[0].set_ylabel("Cº")
    ax[0].set_title("Temperatura Media", fontsize=12)
    ax[0].legend(loc="upper right")
    ax[0].grid(True, alpha=0.3)

    # Gráfico Precipitaciones
    for city in cities:
        df_city = df[df["city"] == city]
        ax[1].plot(df_city["date"], df_city["precipitation"], label=city, linewidth=0.8)
    ax[1].set_ylabel("mm")
    ax[1].set_title("Precipitacion Total", fontsize=12)
    ax[1].legend(loc="upper right")
    ax[1].grid(True, alpha=0.3)

    # Gráfico Velocidad del viento
    for city in cities:
        df_city = df[df["city"] == city]
        ax[2].plot(df_city["date"], df_city["wind_speed"], label=city, linewidth=0.8)
    ax[2].set_ylabel("Km/h")
    ax[2].set_title("Velocidad Máxima del viento", fontsize=12)
    ax[2].legend(loc="upper right")
    ax[2].grid(True, alpha=0.3)

    plt.tight_layout(rect=[0, 0, 1, 0.97])
    plt.savefig("weather_cities_comparison.png")
    plt.show()


def main():

    all_data = []

    # Obtener los datos de cada ciudad
    for city in coordinates.keys():
        df = get_data_meteo_api(city)
        all_data.append(df)
        sleep(1)
    # Combina los df de las ciudades
    df_combined = pd.concat(all_data, ignore_index=True)

    # Procesa los datos periodicidad mensual
    df_monthly = process_data_to_monthly(df_combined)

    # Genera los gráficos
    plot_weather_data(df_monthly)

    return df_monthly


# Ejecutar el script
if __name__ == "__main__":
    df_result = main()
