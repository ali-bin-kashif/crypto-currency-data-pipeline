from lambda_funcs import app

def test_lambda_handler():
    result = app.lambda_handler({}, None)
    assert result["statusCode"] == 200