from airflow import DAG
from airflow.providers.amazon.aws.operators.glue import GlueJobOperator
from airflow.providers.amazon.aws.operators.lambda_function import LambdaInvokeFunctionOperator
from airflow.providers.snowflake.operators.snowflake import SQLExecuteQueryOperator

default_args = {
    'owner': 'ali-bin-kashif',
}


with DAG(
    dag_id='crypto_data_pipeline_historical',
    default_args=default_args,
    schedule=None,  # or "0 */6 * * *" for every 6 hours
    catchup=False,
    tags=['crypto', 'glue', 'snowflake'] ,
) as dag:
    
    run_lambda_function = LambdaInvokeFunctionOperator(
        task_id="run_lambda_function_historical",
        function_name="crypto_data_fetch",
        payload='{"run_type": "normal"}',
        aws_conn_id="aws_default",
        region_name="eu-north-1"

    )

    run_glue_job_intra_day = GlueJobOperator(
        task_id="run_glue_job_historical",
        job_name="historical_data_transformation.py",
        script_location="s3://aws-glue-assets-350681797086-eu-north-1/scripts/historical_data_transformation.py",
        iam_role_name="crypto-glue-raw-crawler",
        aws_conn_id="aws_default",
        region_name="eu-north-1"
    )


    truncate_historical_table = SQLExecuteQueryOperator(
        task_id="truncate_historical_table",
        conn_id="snowflake_conn",
        sql="TRUNCATE TABLE COIN_GECKO_CRYPTO_DATA.PUBLIC.CRYPTO_HISTORICAL;"
    )



    trigger_historical_pipe = SQLExecuteQueryOperator(
        task_id="trigger_historical_pipe",
        conn_id="snowflake_conn",
        sql="ALTER PIPE COIN_GECKO_CRYPTO_DATA.PUBLIC.MYPIPE_HISTORICAL REFRESH;"
    )

    # DAG dependencies
    run_lambda_function >> run_glue_job_intra_day >> truncate_historical_table >> trigger_historical_pipe
    # truncate_historical_table >> trigger_historical_pipe
