from airflow import DAG
from airflow.providers.amazon.aws.operators.glue import GlueJobOperator
from airflow.providers.amazon.aws.operators.lambda_function import LambdaInvokeFunctionOperator
from airflow.providers.snowflake.operators.snowflake import SQLExecuteQueryOperator
from airflow.providers.discord.notifications.discord import DiscordNotifier

# Default arguments for the DAG
default_args = {
    'owner': 'ali-bin-kashif'
}

with DAG(
    dag_id='crypto_data_pipeline_historical',
    default_args=default_args,
    schedule=None,  # Set schedule interval (None for manual, or cron for periodic)
    catchup=False,  # Do not perform backfill
    tags=['crypto', 'glue', 'snowflake'],
    # Notify on successful DAG run via Discord
    on_success_callback = DiscordNotifier(
        discord_conn_id="discord_default",
        text=f"✅ Crypto Historical Data Pipeline DAG: Pipeline ran successfully!"
        ).notify # <-- DAG-level success callback
) as dag:
    
    # Task 1: Invoke AWS Lambda to fetch crypto data
    run_lambda_function = LambdaInvokeFunctionOperator(
        task_id="run_lambda_function_historical",
        function_name="crypto_data_fetch",
        payload='{"run_type": "normal"}',
        aws_conn_id="aws_default",
        region_name="eu-north-1",
        # Notify on failure via Discord
        on_failure_callback=DiscordNotifier(
            discord_conn_id="discord_default",
            text=f"❌ DAG {dag.dag_id} failed at task: Run Lambda Function Historical."
        )
    )

    # Task 2: Run AWS Glue job to transform historical data
    run_glue_job_historical = GlueJobOperator(
        task_id="run_glue_job_historical",
        job_name="historical_data_transformation.py",
        script_location="s3://aws-glue-assets-350681797086-eu-north-1/scripts/historical_data_transformation.py",
        iam_role_name="crypto-glue-raw-crawler",
        aws_conn_id="aws_default",
        region_name="eu-north-1",
        # Notify on failure via Discord
        on_failure_callback=DiscordNotifier(
            discord_conn_id="discord_default",
            text=f"❌ DAG {dag.dag_id} failed at task: Run Glue Job Historical."
        )
    )

    # Task 3: Truncate the historical table in Snowflake before loading new data
    truncate_historical_table = SQLExecuteQueryOperator(
        task_id="truncate_historical_table",
        conn_id="snowflake_conn",
        sql="TRUNCATE TABLE COIN_GECKO_CRYPTO_DATA.PUBLIC.CRYPTO_HISTORICAL;",
        # Notify on failure via Discord
        on_failure_callback=DiscordNotifier(
            discord_conn_id="discord_default",
            text=f"❌ DAG {dag.dag_id} failed at task: Truncate Historical Table in Snowflake."
        )
    )

    # Task 4: Trigger Snowpipe to load new historical data into Snowflake
    trigger_historical_pipe = SQLExecuteQueryOperator(
        task_id="trigger_historical_pipe",
        conn_id="snowflake_conn",
        sql="ALTER PIPE COIN_GECKO_CRYPTO_DATA.PUBLIC.MYPIPE_HISTORICAL REFRESH;",
        # Notify on failure via Discord
        on_failure_callback=DiscordNotifier(
            discord_conn_id="discord_default",
            text=f"❌ DAG {dag.dag_id} failed at task: Trigger Historical Data Snowpipe in Snowflake."
        )
    )

    # Define task dependencies (sequential execution)
    run_lambda_function >> run_glue_job_historical >> truncate_historical_table >> trigger_historical_pipe
