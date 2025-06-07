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
    dag_id='crypto_data_pipeline_intra_day',
    default_args=default_args,
    schedule=None,  # Set to "0 */6 * * *" for every 6 hours if needed
    catchup=False,
    tags=['crypto', 'glue', 'snowflake'],
    # Notify on successful DAG run via Discord
    on_success_callback=DiscordNotifier(
        discord_conn_id="discord_default",
        text=f"✅ Crypto Intra Day Pipeline DAG: Pipeline ran successfully!"
    ).notify # <-- DAG-level success callback
) as dag:

    # Task 1: Invoke AWS Lambda function to fetch crypto data
    run_lambda_function = LambdaInvokeFunctionOperator(
        task_id="run_lambda_function_intra_day",
        function_name="crypto_data_fetch",
        payload='{"run_type": "intra_day"}',
        aws_conn_id="aws_default",
        region_name="eu-north-1",
        # Notify on failure via Discord
        on_failure_callback=DiscordNotifier(
            discord_conn_id="discord_default",
            text=f"❌ DAG {dag.dag_id} failed at task: Run Lambda Function Intra Day."
        )
    )

    # Task 2: Run AWS Glue job for intra-day data transformation
    run_glue_job_intra_day = GlueJobOperator(
        task_id="run_glue_job_intra_day",
        job_name="intra_day_transformation.py",
        script_location="s3://aws-glue-assets-350681797086-eu-north-1/scripts/intra_day_transformation.py",
        iam_role_name="crypto-glue-raw-crawler",
        aws_conn_id="aws_default",
        region_name="eu-north-1",
        # Notify on failure via Discord
        on_failure_callback=DiscordNotifier(
            discord_conn_id="discord_default",
            text=f"❌ DAG {dag.dag_id} failed at task: Run Glue Job Intra Day."
        )
    )

    # Task 3: Truncate the target Snowflake table before loading new data
    truncate_intra_day_table = SQLExecuteQueryOperator(
        task_id="truncate_intra_day_table",
        conn_id="snowflake_conn",
        sql="TRUNCATE TABLE COIN_GECKO_CRYPTO_DATA.PUBLIC.CRYPTO_INTRA_DAY;",
        # Notify on failure via Discord
        on_failure_callback=DiscordNotifier(
            discord_conn_id="discord_default",
            text=f"❌ DAG {dag.dag_id} failed at task: Truncate Intra Day Table in Snowflake."
        )
    )

    # Task 4: Refresh the Snowpipe to load new data into Snowflake
    trigger_intra_day_pipe = SQLExecuteQueryOperator(
        task_id="trigger_intra_day_pipe",
        conn_id="snowflake_conn",
        sql="ALTER PIPE COIN_GECKO_CRYPTO_DATA.PUBLIC.mypipe REFRESH;",
        # Notify on failure via Discord
        on_failure_callback=DiscordNotifier(
            discord_conn_id="discord_default",
            text=f"❌ DAG {dag.dag_id} failed at task: Trigger Intra Day Snowpipe."
        )
    )

    # Define task dependencies: run tasks in sequence
    run_lambda_function >> run_glue_job_intra_day >> truncate_intra_day_table >> trigger_intra_day_pipe
