import requests
import json
import os
from dotenv import load_dotenv
import boto3
from datetime import datetime

load_dotenv() 

COINGECKO_API_KEY = os.getenv("COINGECKO_API_KEY")

def lambda_handler(event, context):
    try:
        # Fetch coins data from CoinGecko API
        url = "https://api.coingecko.com/api/v3/coins/markets"
        params = {
            "vs_currency": "usd",
            "order": "market_cap_desc",
            "per_page": 250,
            "page": 1,
            "sparkline": False
        }
        headers = {
            "x-cg-pro-api-key": COINGECKO_API_KEY
        }

        try:
            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            return {
                "statusCode": 500,
                "body": f"Error fetching data from CoinGecko: {str(e)}",
                "success": False
            }

        try:
            coins_data = response.json()
        except json.JSONDecodeError as e:
            return {
                "statusCode": 500,
                "body": f"Error decoding JSON response: {str(e)}",
                "success": False
            }

        # Store JSON data into S3
        try:
            s3 = boto3.client("s3")
            bucket_name = "crypto-raw-data-abk"
            now = datetime.utcnow()
            s3_key = f"coins_data_{now.strftime('%d-%m-%Y_%H:%M')}.json"
            s3.put_object(
                Bucket=bucket_name,
                Key=s3_key,
                Body=json.dumps(coins_data),
                ContentType="application/json"
            )
        except Exception as e:
            return {
                "statusCode": 500,
                "body": f"Error uploading to S3: {str(e)}",
                "success": False
            }

        return {
            "statusCode": 200,
            "body": f"Successfully stored coins data to s3://{bucket_name}/{s3_key}",
            "success": True
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": f"Unexpected error: {str(e)}",
            "success": False
        }