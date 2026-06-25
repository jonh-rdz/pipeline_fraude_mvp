import pytest
import pandas as pd
import numpy as np
from src.etl_procesamiento import FraudETLPipeline
from pathlib import Path

# Fixture (Setup) de datos simulados
@pytest.fixture
def sample_dataframe():
    data = {
        'id_transaccion': ['T-001', 'T-001', 'T-002', 'T-003'], # Incluye un duplicado
        'estado_transaccion': ['aprobada', 'aprobada', 'rechazada', 'aprobada'],
        'monto_usd': [100.0, 100.0, np.nan, 2000.0], # Incluye un nulo en rechazada
        'tipo_comercio': ['local', 'local', 'local', 'internacional']
    }
    return pd.DataFrame(data)

def test_transform_deduplication_and_imputation(sample_dataframe):
    """Prueba unitaria de las reglas de negocio principales."""
    # Instanciamos la clase con un path falso (no lo usaremos para transform)
    pipeline = FraudETLPipeline(Path("dummy_path.csv"))
    
    # Ejecutamos la transformación
    df_clean = pipeline.transform(sample_dataframe)
    
    # Assert 1: Deduplicación (De 4 registros deben quedar 3)
    assert len(df_clean) == 3
    
    # Assert 2: Imputación a 0.0 en rechazada con monto nulo
    rechazada_row = df_clean[df_clean['id_transaccion'] == 'T-002'].iloc[0]
    assert rechazada_row['monto_usd'] == 0.0
    
    # Assert 3: Flag de monto inusual (>1500 e internacional)
    inusual_row = df_clean[df_clean['id_transaccion'] == 'T-003'].iloc[0]
    assert inusual_row['es_monto_inusual'] == True