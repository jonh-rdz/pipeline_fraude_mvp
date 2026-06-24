from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator

# Definición de argumentos por defecto
default_args = {
    'owner': 'data_engineering',
    'depends_on_past': False,
    'email_on_failure': True,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Creación del DAG (Programado a las 11:30 PM todos los días)
with DAG(
    dag_id='pipeline_prevencion_fraude',
    default_args=default_args,
    description='ETL y Análisis de Anomalías',
    schedule='30 23 * * *',  # CAMBIO: Usamos 'schedule' en lugar de 'schedule_interval'
    start_date=datetime(2026, 6, 20),
    catchup=False,
    tags=['fraude', 'etl'],
) as dag:

    # Tarea 1: Ejecutar ETL en Python (Pandas a Supabase)
    tarea_etl = PythonOperator(
        task_id='extraccion_transformacion_carga',
        python_callable=lambda: print("Ejecutando src/etl_procesamiento.py...")
    )

    # Tarea 2: Ejecutar Análisis SQL en Supabase
    tarea_analitica = SQLExecuteQueryOperator(
        task_id='deteccion_anomalias_sql',
        conn_id='supabase_conn',
        sql='sql/analisis.sql'
    )

    # Dependencia estricta: El SQL solo corre si el ETL fue exitoso
    tarea_etl >> tarea_analitica