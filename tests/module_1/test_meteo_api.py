import pytest
import pandas as pd
from unittest.mock import patch, Mock
from src.module_1.module_1_meteo_api import get_data_meteo_api, call_api


@patch("src.module_1.module_1_meteo_api.call_api")
def test_get_data_return_dataframe(mock_call_api):
    """
    Tes1: Verificar que get_data_meteo_api devuelve un DataFrame

    """
    # Arrange: preparar los datos que simulan la respuesta de la API

    mock_call_api.return_value = {
        "daily": {
            "time": ["2010-01-01", "2020-12-31"],
            "temperature_2m_mean": [15.5, 17.5],
            "precipitation_sum": [0.0, 2.5],
            "wind_speed_10m_max": [12.5, 20.3],
        }
    }

    # Act: llamar a la funcion get_data_meteo_api
    resultado = get_data_meteo_api("Madrid")

    # Assert: verificar el resultado

    assert isinstance(resultado, pd.DataFrame)
    assert len(resultado) == 2
    assert "temperature" in resultado.columns
    assert "precipitation" in resultado.columns
    assert "wind_speed" in resultado.columns
    assert "city" in resultado.columns
    assert resultado["city"][0] == "Madrid"


def test_get_data_ciudad_no_valida():
    """
    Test 2: Verificar que salta ValueError con una ciudad que no existe en los datos

    """
    # Act: verificar que se lanza la excepcion esperada
    with pytest.raises(ValueError) as error:
        get_data_meteo_api("Valencia")
    # Assert: verificar que el mensaje de error es correcto

    assert "no encontrada" in str(error.value)


@patch("src.module_1.module_1_meteo_api.requests.get")
def test_call_api_rate_limit(mock_get):
    """
    Test 3: Verificar que call_api reintenta cuando hay rate limit (429)

    """
    # Arrange: Simular que da el error 429 y luego funciona

    mock_response_error = Mock()
    mock_response_error.status_code = 429

    mock_response_ok = Mock()
    mock_response_ok.status_code = 200
    mock_response_ok.json.return_value = {"data": "success"}

    mock_get.side_effect = [mock_response_error, mock_response_ok]

    # Act: llamar a call_api
    resultado = call_api("http://test.com", {})

    # Assert: Verificar que funciona despues del reintento
    assert resultado == {"data": "success"}
    assert mock_get.call_count == 2
