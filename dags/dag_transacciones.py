from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator

# Definición de argumentos por defecto con estándares de producción
default_args = {
    'owner': 'data_engineering',
    'depends_on_past': False,
    'email_on_failure': True,
    'retries': 2, # Aumentado a 2 para mayor resiliencia en red
    'retry_delay': timedelta(minutes=3),
}

with DAG(
    dag_id='pipeline_prevencion_fraude',
    default_args=default_args,
    description='ETL y Análisis de Anomalías de Gasto Diario',
    schedule='30 23 * * *', 
    start_date=datetime(2026, 6, 20),
    catchup=False,
    tags=['fraude', 'etl', 'daily'],
) as dag:

    tarea_etl = PythonOperator(
        task_id='extraccion_transformacion_carga',
        python_callable=lambda: print("Ejecutando src/etl_procesamiento.py...")
    )

    tarea_analitica = SQLExecuteQueryOperator(
        task_id='deteccion_anomalias_sql',
        conn_id='supabase_conn',
        sql='sql/02_analisis_anomalias.sql' # CORRECCIÓN: Ruta actualizada
    )

    tarea_etl >> tarea_analitica