from lambda_funcs import app


def test_coingecko_api_key():
    assert app.COINGECKO_API_KEY is not None, "COINGECKO_API_KEY should be set in .env file"


def test_ping_coingecko():
    url = "https://api.coingecko.com/api/v3/ping"

    headers = {
    "accept": "application/json",
    "x-cg-demo-api-key": app.COINGECKO_API_KEY
        }

    response = app.requests.get(url, headers=headers)
    response_json = response.json()
    assert response.status_code == 200, response_json["status"]["error_message"]


def test_s3_buckets():
    s3 = app.boto3.client("s3")
    bucket_name = "crypto-raw-data-abk"
    try:
        response = s3.head_bucket(Bucket=bucket_name)
        assert True
    except Exception as e:
        assert False, f"Bucket {bucket_name} does not exist or is not accessible: {e}"


# def test_lambda_handler():
#     result = app.lambda_handler({}, None)
#     assert result["statusCode"] == 200

