from flask import request
from flask_restful import Resource

from managers.auth import auth
from managers.complaint import ComplaintManager
from models.enums import RoleType
from schemas.request.complaint import ComplaintRequestCreateSchema
from schemas.response.complaint import ComplaintResponseCreateSchema
from util.decorators import validate_schema, permission_required


class ComplaintListCreate(Resource):
    @auth.login_required
    def get(self):
        complaints = ComplaintManager.get_all()
        schema = ComplaintResponseCreateSchema()
        return schema.dump(complaints, many=True), 201

    @auth.login_required
    @permission_required(RoleType.complainer)
    @validate_schema(ComplaintRequestCreateSchema)
    def post(self):
        current_user = auth.current_user()
        data = request.get_json()
        compaint = ComplaintManager.create(data, current_user)
        schema = ComplaintResponseCreateSchema()
        return schema.dump(compaint), 201


class ComplaintDetail(Resource):
    def get(self, id_):
        pass

    @auth.login_required
    @permission_required(RoleType.complainer)
    @validate_schema(ComplaintRequestCreateSchema)
    def put(self, id_):
        updated_complaint = ComplaintManager.update(request.get_json(), id_)
        schema = ComplaintRequestCreateSchema()
        return schema.dump(updated_complaint), 201

    @auth.login_required
    # @permission_required(RoleType.admin)
    def delete(self, id_):
        ComplaintManager.delete(id_)
        return {"message": "Success"}, 204


class ApproveComplain(Resource):
    @auth.login_required
    @permission_required(RoleType.approver)
    def get(self, id_):
        complaint = ComplaintManager.approve(id_)
        schema = ComplaintResponseCreateSchema()
        return schema.dump(complaint), 200


class RejectComplain(Resource):
    @auth.login_required
    # @permission_required(RoleType.approver)
    def get(self, id_):
        complaint = ComplaintManager.reject(id_)
        schema = ComplaintResponseCreateSchema()
        return schema.dump(complaint), 200
