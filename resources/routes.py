from resources.auth import Register, Login, LoginApprover
from resources.complaint import (
    ComplaintListCreate,
    ComplaintDetail,
    ApproveComplain,
    RejectComplain,
)

routes = (
    (Register, "/register"),
    (Login, "/login"),
    (LoginApprover, "/approvers/login"),
    (ComplaintListCreate, "/complainers/complaints"),
    (ComplaintDetail, "/complainers/complaints/<int:id_>"),
    (ApproveComplain, "/approvers/complaints/<int:id_>/approve"),
    (RejectComplain, "/approvers/complaints/<int:id_>/reject"),
)
