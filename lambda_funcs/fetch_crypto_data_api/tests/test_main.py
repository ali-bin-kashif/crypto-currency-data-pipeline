from lambda_funcs.fetch_crypto_data_api import main

def test_lambda_handler():
    result = main.lambda_handler({}, None)
    assert result["statusCode"] == 200