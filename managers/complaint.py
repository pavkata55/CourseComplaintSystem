import uuid

from werkzeug.exceptions import NotFound

from db import db
from managers.auth import auth
from models import State
from models.complaint import ComplaintModel
from models.transaction import TransactionModel
from models.user import ComplainerModel
from services.wise import WiseService

wise = WiseService()


class ComplaintManager:
    @staticmethod
    def create(complaint_data, complainer):
        complaint_data["complainer_id"] = complainer.id
        user = ComplainerModel.query.filter_by(id=complainer.id).first()
        full_name = f"{user.first_name} {user.last_name}"
        iban = user.iban
        amount = complaint_data["amount"]
        complaint = ComplaintModel(**complaint_data)
        db.session.add(complaint)
        db.session.flush()
        ComplaintManager.issue_transaction(amount, full_name, iban, complaint.id)
        return complaint

    @staticmethod
    def issue_transaction(amount, full_name, iban, complaint_id):

        quote_id = wise.create_quota(amount)
        recipient_id = wise.create_recipient(full_name, iban)
        customer_transaction_id = str(uuid.uuid4())
        transfer_id = wise.create_transfer(
            recipient_id, quote_id, customer_transaction_id
        )
        transfer_data = {
            "quote_id": quote_id,
            "transfer_id": transfer_id,
            "target_account_id": customer_transaction_id,
            "amount": amount,
            "complaint_id": complaint_id,
        }
        transfer = TransactionModel(**transfer_data)
        db.session.add(transfer)
        db.session.flush()

    @staticmethod
    def update(complaint_data, id_):
        complaint_q = ComplaintModel.query.filter_by(id=id_)
        complaint = complaint_q.first()
        if not complaint:
            raise NotFound("This complaint does not exist")

        user = auth.current_user()
        if not user.id == complaint.complainer_id:
            raise NotFound("This complaint does not exist")

        complaint_q.update(complaint_data)
        db.session.flush()
        return complaint

    @staticmethod
    def get_all():
        complaint = ComplaintModel.query.all()
        return complaint

    @staticmethod
    def approve(id_):
        complaint_q = ComplaintModel.query.filter_by(id=id_)
        complaint = complaint_q.first()
        if not complaint:
            raise NotFound("This complaint does not exist")
        transfer = TransactionModel.query.filter_by(complaint_id=id_).first()
        status = wise.fund_transfer(transfer.transfer_id)
        complaint_q.update({"status": State.approved})
        db.session.flush()
        return complaint

    @staticmethod
    def reject(id_):
        complaint_q = ComplaintModel.query.filter_by(id=id_)
        complaint = complaint_q.first()
        if not complaint:
            raise NotFound("This complaint does not exist")
        complaint_q.update({"status": State.rejected})
        db.session.flush()
        return complaint

    @staticmethod
    def delete(id_):
        complaint_q = ComplaintModel.query.filter_by(id=id_)
        complaint = complaint_q.first()
        if not complaint:
            raise NotFound("This complaint does not exist")
        db.session.delete(complaint)
        db.session.flush()
