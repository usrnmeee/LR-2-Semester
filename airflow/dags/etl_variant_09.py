from airflow import DAG
from airflow.operators.bash import BashOperator
import pendulum

PROJECT_ROOT = "/opt/airflow/app"
MODE = "full"
LOG_PREFIX = "[ETL-09]"

with DAG(
        dag_id="etl_variant_09",
        start_date=pendulum.datetime(2026, 3, 1, tz="UTC"),
        schedule="*/5 * * * *",
        catchup=False,
        tags=["etl", "variant_09"],
) as dag:
    extract = BashOperator(
        task_id="extract",
        bash_command=f"""
        set -e
        echo "{LOG_PREFIX} extract started"
        echo "{LOG_PREFIX} mode={MODE}"
        cd {PROJECT_ROOT}
        python src/pipeline/extract.py {MODE}
        echo "{LOG_PREFIX} extract finished"
        """,
    )

    transform = BashOperator(
        task_id="transform",
        bash_command=f"""
        set -e
        echo "{LOG_PREFIX} transform started"
        cd {PROJECT_ROOT}
        python src/pipeline/transform.py
        echo "{LOG_PREFIX} transform finished"
        """,
    )

    mart = BashOperator(
        task_id="mart",
        bash_command=f"""
        set -e
        echo "{LOG_PREFIX} mart started"
        cd {PROJECT_ROOT}
        python src/pipeline/mart.py
        echo "{LOG_PREFIX} mart finished"
        """,
    )

    load = BashOperator(
        task_id="load",
        env={
            "DB_USER": "usrnmeee",
            "DB_PASSWORD": "password",
            "DB_HOST": "postgres",
            "DB_PORT": "5432",
            "DB_NAME": "lab",
        },
        bash_command=f"""
        set -e
        echo "{LOG_PREFIX} load started"
        cd {PROJECT_ROOT}
        python src/pipeline/load.py full
        echo "{LOG_PREFIX} load finished"
        """,
    )

    dq = BashOperator(
        task_id="dq",
        bash_command=f"""
        set -e
        echo "{LOG_PREFIX} dq started"
        cd {PROJECT_ROOT}
        python src/dq/dq.py
        echo "{LOG_PREFIX} dq finished"
        """,
    )

    extract >> transform >> mart >> load >> dq
