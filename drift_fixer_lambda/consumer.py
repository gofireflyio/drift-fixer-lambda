import json
import requests
import loguru
from aws_lambda_powertools.utilities.typing import LambdaContext
from drift_fixer_lambda import models
from drift_fixer_lambda.models import NotificationEvent, FireflySession
from utils import login_external_api
from typing import Any, Dict

logger = loguru.logger
SETTINGS = models.DriftFixerConsumerSettings()
INVENTORY_ROUTE = "inventory/v1"
SEARCH_AND_FIX_DRIFT_ROUTE = "searchfixdrift/v1"
DRIFT_WAS_PROBABLY_FIXED_MESSAGE = "We found all drifted properties. There is no change in the property values. The drift was probably fixed."

# get session globally
firefly_session_token = FireflySession(
    **login_external_api(logger=logger, firefly_external_api_base_url=SETTINGS.firefly_api_url,
                         access_key=SETTINGS.firefly_access_key,
                         secret_key=SETTINGS.firefly_secret_key))


def get_inventory(notification_event):
    url = SETTINGS.firefly_api_url + INVENTORY_ROUTE
    frns = []
    for sample in notification_event.samples:
        frns.append(sample.FRN)

    # TODO - pagination
    payload = {
        "frns": frns,
        "pageNumber": 1
    }
    headers = {
        'Authorization': f'Bearer {firefly_session_token.accessToken}'
    }
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        logger.info("get inventory was successful.")
        return response.json()
    else:
        logger.error(
            f"get inventory request failed.", status_code=response.status_code, response_content=response.text)
        raise Exception(f"Could not get inventory items token. reason={response.text}")


def fix_drift(drift_resources):
    url = SETTINGS.firefly_api_url + SEARCH_AND_FIX_DRIFT_ROUTE

    for drift_resource in drift_resources:
        # check mandatory properties for fixing drift
        if drift_resource["vcsId"] == "" or drift_resource["terraformObjectReferencesAncestry"] == "" \
                or drift_resource["drift"] == "":
            logger.warning(f"missing mandatory properties for fixing drift.", resource=drift_resource)
            continue

        payload = {
            "frn": drift_resource["frn"],
            "vcsId": drift_resource["vcsId"],
            "vcsWorkingDir": drift_resource["vcsWorkingDirectory"],
            "references": drift_resource["terraformObjectReferencesAncestry"],
            "drifts": drift_resource["drift"],
            "fixFirstOccurrence": True,
            "prComment": SETTINGS.fix_drift_pr_message,
            "requestSource": "fix_drift_lambda"
        }
        headers = {
            'Authorization': f'Bearer {firefly_session_token.accessToken}'
        }
        response = requests.post(url, json=payload, headers=headers)

        if response.status_code == 200:
            logger.info(f"created PR for fixing drift.", resource=drift_resource, pr_response=response.text)
        else:
            logger.warning(DRIFT_WAS_PROBABLY_FIXED_MESSAGE, resource=drift_resource)


def lambda_handler(event: Dict[str, Any], context: LambdaContext):
    try:
        logger.info(f"incoming message.", event=event)

        try:
            event_body = json.loads(event.get('body'))
        except (ValueError, TypeError, KeyError) as ex:
            logger.error(f"could not parse the notification event.", ex=ex, event=event)
            raise Exception(f"could not parse the notification event. ex={ex}, event={event}")

        # return heartbeat message for creating Firefly webhook integration
        if event_body.get("text", None) is not None:
            return {
                'statusCode': 200,
                'body': json.dumps('Webhook Integration Success!')
            }

        # if session is about to end, refresh the token
        if firefly_session_token.is_token_expired():
            firefly_session_token.set_new_credentials(logger=logger, firefly_api_url=SETTINGS.firefly_api_url,
                                                      firefly_access_key=SETTINGS.firefly_access_key,
                                                      firefly_secret_key=SETTINGS.firefly_secret_key)

        # Parse the notification event to a model
        notification_event = NotificationEvent(**event_body)

        # query Firefly inventory route to find the resources from the event received
        items = get_inventory(notification_event)

        # query Firefly search and fix drift route for opening a PR to fix the needed drift.
        fix_drift(items['responseObjects'])
    except Exception as ex:
        logger.error(f"got unexpected exception from lambda runner", ex=ex, event=event)
        raise Exception(f"got unexpected exception from lambda runner. ex={ex}, event={event}")
