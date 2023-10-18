from datetime import datetime, timedelta
from pydantic import BaseModel, BaseSettings, Field
from typing import List, Dict, Optional
from utils import login_external_api


class DriftFixerConsumerSettings(BaseSettings):
    firefly_access_key: str = Field(env="FIREFLY_ACCESS_KEY")
    firefly_secret_key: str = Field(env="FIREFLY_SECRET_KEY")
    firefly_api_url: str = Field(env="FIREFLY_API_URL", default="https://api.firefly.ai/")
    fix_drift_pr_message: str = Field(env="FIX_DRIFT_PR_MESSAGE",
                                      default="PR for Drift fix was created by the Firefly drift fixer Lambda")


class FireflySession(BaseModel):
    accessToken: str
    expiresAt: int
    tokenType: str

    def set_new_credentials(self, logger, firefly_api_url, firefly_access_key, firefly_secret_key):
        new_credentials = login_external_api(logger=logger, firefly_external_api_base_url=firefly_api_url,
                                             access_key=firefly_access_key,
                                             secret_key=firefly_secret_key)
        self.accessToken = new_credentials['accessToken']
        self.expiresAt = new_credentials['expiresAt']
        self.tokenType = new_credentials['tokenType']

    def is_token_expired(self):
        dt = datetime.fromtimestamp(self.expiresAt)
        expiration_with_buffer = dt + timedelta(minutes=5)
        return expiration_with_buffer > datetime.now()


class Drift(BaseModel):
    iacType: str
    iacValue: str
    keyName: str
    providerValue: str


class OwnerDataUserIdentity(BaseModel):
    arn: str
    customColor: str
    displayName: str
    initials: str
    type: str
    email: Optional[str]


class OwnerData(BaseModel):
    eventName: str
    eventTime: str
    otherOwnerData: Optional[Dict]
    userIdentity: OwnerDataUserIdentity
    workflowId: str


class Sample(BaseModel):
    ARN: str
    FRN: str
    crawlerId: str
    drifts: List[Drift]
    firstSeen: str
    inventoryUpdateTime: str
    isChild: bool
    isCrawlerEventDriven: bool
    isExcluded: bool
    isLocked: bool
    lastResourceStateChange: str
    name: str
    ownerData: OwnerData
    tags: str


class NotificationEvent(BaseModel):
    accountId: str
    accountName: str
    assetType: str
    integrationId: str
    integrationIdentifier: str
    integrationName: str
    notificationType: str
    providerType: str
    region: str
    samples: List[Sample]
    workflowId: str
