import json
import requests
import loguru
from aws_lambda_powertools.utilities.typing import LambdaContext
from drift_fixer_lambda import models
from drift_fixer_lambda.models import NotificationEvent, FireflySession
from utils import login_external_api
from typing import Any, Dict
import sys

logger = loguru.logger
logger.remove()
logger.add(
    sink=sys.stdout,
    format='{level: <8} | {message} | {extra}',
)
SETTINGS = models.DriftFixerConsumerSettings()
INVENTORY_ROUTE = "inventory/v1"
SEARCH_AND_FIX_DRIFT_ROUTE = "searchfixdrift/v1"
DRIFT_WAS_PROBABLY_FIXED_MESSAGE = "Cannot fix drift. Either there is no code refrence, or we found all drifted properties and there is no change in the property values."

# get session globally
firefly_session_token = FireflySession(
    **login_external_api(logger=logger, firefly_external_api_base_url=SETTINGS.firefly_api_url,
                         access_key=SETTINGS.firefly_access_key,
                         secret_key=SETTINGS.firefly_secret_key))


def fix_drift(notification_sample):
    url = SETTINGS.firefly_api_url + SEARCH_AND_FIX_DRIFT_ROUTE

    # check mandatory properties for fixing drift
    if notification_sample.FRN == "" or notification_sample.drifts == "":
        logger.warning(f"missing mandatory properties for fixing drift.", resource=notification_sample)
        return

    payload = {
        "frn": notification_sample.FRN,
        "drifts": [model.dict() for model in notification_sample.drifts],
        "fixFirstOccurrence": True,
        "prComment": SETTINGS.fix_drift_pr_message,
        "requestSource": "fix_drift_lambda"
    }
    headers = {
        'Authorization': f'Bearer {firefly_session_token.accessToken}'
    }
    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 200:
        logger.info(f"created PR for fixing drift.", resource=notification_sample, pr_response=response.text)
    else:
        logger.warning(DRIFT_WAS_PROBABLY_FIXED_MESSAGE, resource=notification_sample)


def lambda_handler(event: Dict[str, Any], context: LambdaContext):
    try:
        logger.info(f"incoming message.", event=event.get('body', {}))

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

        # for each notification sample -
        # query Firefly search and fix drift route for opening a PR to fix the needed drift.
        for sample in notification_event.samples:
            fix_drift(sample)

        logger.info(f"Finished working on message.")

    except Exception as ex:
        logger.error(f"got unexpected exception from lambda runner.", ex=ex, event=event)
        raise Exception(f"got unexpected exception from lambda runner. ex={ex}, event={event}")
