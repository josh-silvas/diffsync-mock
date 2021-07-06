"""Local adapter used to load 'local' data."""
from diffsync import DiffSync
from models import Employee


class LocalAdapter(DiffSync):
    """DiffSync Adapter to Load the list of employees from a local JSON file."""

    employee = Employee

    top_level = ["employee"]

    type = "Local"

    def load(self, employees):  # pylint: disable=arguments-differ
        """Load all employees from a local JSON file."""
        # Load all employees
        for index, employee in enumerate(employees):
            self.add(
                self.employee(
                    name=employee["name"],
                    company=employee["company"],
                    job=employee["job"],
                    ssn=employee["ssn"],
                    residence=employee["residence"],
                    username=f"{employee['username']}{index}",
                    mail=employee["mail"],
                )
            )
