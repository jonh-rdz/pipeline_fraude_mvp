import logging
from pathlib import Path
import pandas as pd
import numpy as np
from dotenv import load_dotenv
from supabase import create_client, Client
import os

# Configuración de logger profesional
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class FraudETLPipeline:
    """Clase principal para orquestar la ingesta y limpieza de transacciones."""
    
    def __init__(self, data_file_path: Path):
        self.data_file_path = data_file_path
        self.supabase: Client = self._init_supabase_client()

    def _init_supabase_client(self) -> Client:
        """Inicializa el cliente de Supabase usando variables de entorno."""
        load_dotenv()
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        
        if not url or not key:
            raise EnvironmentError("Faltan las credenciales SUPABASE_URL o SUPABASE_KEY en el archivo .env")
        return create_client(url, key)

    def extract(self) -> pd.DataFrame:
        """Extrae los datos crudos del archivo CSV local."""
        logger.info(f"Extrayendo datos desde: {self.data_file_path}")
        if not self.data_file_path.exists():
            raise FileNotFoundError(f"El archivo no existe: {self.data_file_path}")
        return pd.read_csv(self.data_file_path)

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Aplica reglas de calidad de datos y lógica de negocio."""
        logger.info("Iniciando transformación de datos...")
        df_clean = df.copy()
        
        # 1. Deduplicación
        initial_len = len(df_clean)
        df_clean.drop_duplicates(subset=['id_transaccion'], keep='first', inplace=True)
        logger.info(f"Registros duplicados eliminados: {initial_len - len(df_clean)}")

        # 2. Imputación condicionada
        mask_null_rejected = df_clean['monto_usd'].isnull() & (df_clean['estado_transaccion'] == 'rechazada')
        df_clean.loc[mask_null_rejected, 'monto_usd'] = 0.0
        logger.info(f"Nulos imputados en transacciones rechazadas: {mask_null_rejected.sum()}")
        
        # 3. Feature Engineering
        df_clean['es_monto_inusual'] = np.where(
            (df_clean['monto_usd'] > 1500) & (df_clean['tipo_comercio'] == 'internacional'),
            True, False
        )
        
        # 4. Casteo para base de datos (NaN a None)
        df_clean['monto_usd'] = df_clean['monto_usd'].replace({np.nan: None})
        return df_clean

    def load(self, df: pd.DataFrame, table_name: str = "transacciones") -> None:
        """Carga el DataFrame transformado a Supabase."""
        logger.info(f"Iniciando carga a Supabase en la tabla '{table_name}'...")
        records = df.to_dict(orient='records')
        
        try:
            response = self.supabase.table(table_name).upsert(records).execute()
            logger.info(f"Carga exitosa: {len(response.data)} registros insertados.")
        except Exception as e:
            logger.error(f"Error crítico durante la carga en base de datos: {e}")
            raise

    def run_pipeline(self) -> None:
        """Método orquestador del pipeline."""
        try:
            raw_data = self.extract()
            clean_data = self.transform(raw_data)
            self.load(clean_data)
            logger.info("Pipeline ETL finalizado con éxito.")
        except Exception as e:
            logger.critical(f"El pipeline falló en ejecución: {e}")
            raise

if __name__ == "__main__":
    # Pathlib calcula la ruta absoluta de forma segura y multiplataforma
    current_dir = Path(__file__).resolve().parent
    csv_path = current_dir.parent / "data" / "transacciones_diarias.csv"
    
    # Ejecución orientada a objetos
    pipeline = FraudETLPipeline(data_file_path=csv_path)
    pipeline.run_pipeline()