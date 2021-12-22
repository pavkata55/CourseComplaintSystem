import json
import uuid

import requests
from decouple import config
from werkzeug.exceptions import InternalServerError


class WiseService:
    def __init__(self):
        self.token = config("WISE_API_KEY")
        self.base_url = config("WISE_URL")
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-type": "application/json",
        }
        self.profile_id = self.get_profie_id()

    def get_profie_id(self):
        url = self.base_url + "/v1/profiles"

        resp = requests.get(url, headers=self.headers)
        if resp.status_code in (200, 201):
            return [el["id"] for el in resp.json() if el["type"] == "personal"][0]
        logger.exceptions("")
        raise InternalServerError("Payment provider is not available")

    def create_quota(self, amount):
        url = self.base_url + "/v2/quotes"
        data = {
            "sourceCurrency": "EUR",
            "targetCurrency": "EUR",
            "sourceAmount": amount,
            "targetAmount": None,
            "profile": self.profile_id,
        }
        resp = requests.post(url, data=json.dumps(data), headers=self.headers)
        if resp.status_code in (200, 201):
            return resp.json()["id"]
        raise InternalServerError("Payment provider is not available")

    def create_recipient(self, full_name, iban):
        url = self.base_url + "/v1/accounts"
        data = {
            "currency": "EUR",
            "type": "iban",
            "profile": self.profile_id,
            "accountHolderName": full_name,
            "legalType": "PRIVATE",
            "details": {"iban": iban},
        }
        resp = requests.post(url, data=json.dumps(data), headers=self.headers)
        if resp.status_code in (200, 201):
            return resp.json()["id"]
        raise InternalServerError("Payment provider is not available")

    def create_transfer(self, recipient_id, quote_id, customer_transaction_id):
        url = self.base_url + "/v1/transfers"
        data = {
            "targetAccount": recipient_id,
            "quoteUuid": quote_id,
            "customerTransactionId": customer_transaction_id,
            "details": {},
        }
        resp = requests.post(url, data=json.dumps(data), headers=self.headers)
        if resp.status_code in (200, 201):
            return resp.json()["id"]
        raise InternalServerError("Payment provider is not available")

    def fund_transfer(self, transferId):
        url = (
            self.base_url
            + "/v3/profiles/"
            + f"{self.profile_id}"
            + "/transfers/"
            + f"{transferId}"
            + "/payments"
        )
        data = {"type": "BALANCE"}
        resp = requests.post(url, data=json.dumps(data), headers=self.headers)
        if resp.status_code in (200, 201):
            return resp.json()["status"]
        raise InternalServerError("Payment provider is not available")


if __name__ == "__main__":
    wise = WiseService()
    quote_id = wise.create_quota(20)
    recipient_id = wise.create_recipient("AA BB", "BG18RZBB91550123456789")
    customer_transaction_id = str(uuid.uuid4())
    transfer_id = wise.create_transfer(recipient_id, quote_id, customer_transaction_id)
    status = wise.fund_transfer(transfer_id)
