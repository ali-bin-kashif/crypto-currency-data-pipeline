from airflow import DAG
from airflow.providers.amazon.aws.operators.glue import GlueJobOperator
from airflow.providers.amazon.aws.operators.lambda_function import LambdaInvokeFunctionOperator
from airflow.providers.snowflake.operators.snowflake import SQLExecuteQueryOperator

default_args = {
    'owner': 'ali-bin-kashif',
}


with DAG(
    dag_id='crypto_data_pipeline_intra_day',
    default_args=default_args,
    schedule=None,  # or "0 */6 * * *" for every 6 hours
    catchup=False,
    tags=['crypto', 'glue', 'snowflake'] ,
) as dag:
    
    run_lambda_function = LambdaInvokeFunctionOperator(
        task_id="run_lambda_function",
        function_name="crypto_data_fetch",
        payload='{"run_type": "intra_day"}',
        aws_conn_id="aws_default",
        region_name="eu-north-1"

    )

    run_glue_job_intra_day = GlueJobOperator(
        task_id="run_glue_job_intra_day",
        job_name="intra_day_transformation.py",
        script_location="s3://aws-glue-assets-350681797086-eu-north-1/scripts/intra_day_transformation.py",
        iam_role_name="crypto-glue-raw-crawler",
        aws_conn_id="aws_default",
        region_name="eu-north-1"
    )


    truncate_intra_day_table = SQLExecuteQueryOperator(
        task_id="truncate_intra_day_table",
        conn_id="snowflake_conn",
        sql="TRUNCATE TABLE COIN_GECKO_CRYPTO_DATA.PUBLIC.CRYPTO_INTRA_DAY;"
    )



    trigger_intra_day_pipe = SQLExecuteQueryOperator(
        task_id="trigger_intra_day_pipe",
        conn_id="snowflake_conn",
        sql="ALTER PIPE COIN_GECKO_CRYPTO_DATA.PUBLIC.mypipe REFRESH;"
    )

    # DAG dependencies
    run_lambda_function >> run_glue_job_intra_day >> truncate_intra_day_table >> trigger_intra_day_pipe
