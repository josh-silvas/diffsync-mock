from diffsync import DiffSyncModel


class Employee(DiffSyncModel):
    """Example model of an employee."""

    _modelname = "employee"
    _identifiers = ("username",)
    _attributes = ("company", "job", "ssn", "residence", "name", "mail")

    name: str
    company: str
    job: str
    ssn: str
    residence: str
    username: str
    mail: str

