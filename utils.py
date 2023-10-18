import requests


def login_external_api(logger, firefly_external_api_base_url, access_key, secret_key):
    """
    Logs into an external API service using Firefly access and secret keys.

    This function sends a POST request to the Firefly external API to obtain a session token
    for authentication purposes.

    Args:
        logger (Logger): The logger instance for logging messages.
        firefly_external_api_base_url (str): The base URL of the Firefly external API.
        access_key (str): The Firefly access key for authentication.
        secret_key (str): The Firefly secret key for authentication.

    Returns:
        dict: A dictionary containing the response from the API, which typically includes
              a session token upon successful login.

    Raises:
        Exception: If access_key or secret_key is missing, or if the login request fails.
    """
    if access_key == "" or secret_key == "":
        logger.error(
            f"missing Firefly access key or secret key.", access_key=access_key, secret_key=secret_key)
        raise Exception(f"missing Firefly access key or secret key. access_key={access_key} secret_key={secret_key}")
    url = firefly_external_api_base_url + "account/v1/login"
    payload = {
        "accessKey": access_key,
        "secretKey": secret_key
    }
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        logger.info("get session was successful")
        return response.json()
    else:
        logger.error(
            f"get session request failed.", status_code=response.status_code, response_content=response.text)
        raise Exception(f"Could not get session token. reason={response.text}")
