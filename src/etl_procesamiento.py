import os
import logging
import pandas as pd
import numpy as np
from dotenv import load_dotenv
from supabase import create_client, Client

# Configuración básica para ver mensajes en la terminal
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def cargar_variables() -> tuple[str, str]:
    """Carga las credenciales de Supabase desde el archivo .env"""
    load_dotenv()
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    
    if not url or not key:
        raise ValueError("No se encontraron las credenciales en el archivo .env")
    return url, key

def extraer_datos(ruta_archivo: str) -> pd.DataFrame:
    """Lee el archivo CSV desde la carpeta local."""
    logging.info(f"Iniciando extracción de datos desde {ruta_archivo}")
    return pd.read_csv(ruta_archivo)

def transformar_datos(df: pd.DataFrame) -> pd.DataFrame:
    """Aplica las reglas de negocio estrictas usando Pandas."""
    logging.info("Iniciando transformación de datos...")
    
    # Regla 1: Eliminar duplicados basados en id_transaccion
    registros_iniciales = len(df)
    df_clean = df.drop_duplicates(subset=['id_transaccion'], keep='first').copy()
    logging.info(f"Se eliminaron {registros_iniciales - len(df_clean)} registros duplicados.")

    # Regla 2: Imputar 0.0 si monto_usd es nulo y estado_transaccion es 'rechazada'
    mask_null_rejected = df_clean['monto_usd'].isnull() & (df_clean['estado_transaccion'] == 'rechazada')
    df_clean.loc[mask_null_rejected, 'monto_usd'] = 0.0
    logging.info(f"Se imputaron {mask_null_rejected.sum()} nulos a 0.0 en transacciones rechazadas.")
    
    # Regla 3: Crear columna booleana 'es_monto_inusual'
    df_clean['es_monto_inusual'] = np.where(
        (df_clean['monto_usd'] > 1500) & (df_clean['tipo_comercio'] == 'internacional'),
        True,
        False
    )
    
    # Reemplazar NaN restantes por None para que la Base de Datos lo acepte sin errores
    df_clean['monto_usd'] = df_clean['monto_usd'].replace({np.nan: None})
    
    return df_clean

def cargar_a_supabase(df: pd.DataFrame, url: str, key: str):
    """Sube los datos limpios a la tabla en Supabase."""
    try:
        logging.info("Conectando a Supabase e insertando registros...")
        supabase: Client = create_client(url, key)
        
        # Convertir Pandas DataFrame a una lista de diccionarios
        records = df.to_dict(orient='records')
        
        # Insertar en la tabla 'transacciones'
        response = supabase.table("transacciones").insert(records).execute()
        logging.info(f"¡Carga exitosa! Se insertaron {len(records)} registros en la nube.")
    except Exception as e:
        logging.error(f"Error durante la carga a Supabase: {e}")

def main():
    # --- SOLUCIÓN DE RUTAS: Encuentra el CSV sin importar dónde estés parado ---
    directorio_actual = os.path.dirname(os.path.abspath(__file__))
    ruta_archivo = os.path.join(directorio_actual, '..', 'data', 'transacciones_diarias.csv') 
    
    try:
        url, key = cargar_variables()
        df_raw = extraer_datos(ruta_archivo)
        df_clean = transformar_datos(df_raw)
        cargar_a_supabase(df_clean, url, key)
    except Exception as e:
        logging.critical(f"El pipeline falló: {e}")

if __name__ == "__main__":
    main()