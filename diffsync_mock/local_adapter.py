"""Local adapter used to load 'local' data."""
from diffsync import DiffSync
from models import Employee


class LocalAdapter(DiffSync):
    """DiffSync Adapter to Load the list of regions and countries from a local JSON file."""

    employee = Employee

    # Since all countries are associated with a region, we don't need to list country here
    # When doing a diff or a sync between 2 adapters,
    #  diffsync will recursively check all models defined at the top level and their children.
    top_level = ["employee"]

    # Human readable name of the Adapter,
    # mainly used when doing a diff to indicate where each data is coming from
    type = "Local"

    def load(self, employees):  # pylint: disable=arguments-differ
        """Load all regions and countries from a local JSON file."""
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
