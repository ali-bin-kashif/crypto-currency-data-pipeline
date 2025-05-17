from lambda_funcs import fetch_crypto_data_api

def test_lambda_handler():
    result = fetch_crypto_data_api.lambda_handler({}, None)
    assert result["statusCode"] == 200