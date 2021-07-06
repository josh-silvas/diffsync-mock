"""Redis adapter used to load 'remote' data."""
from typing import List, Mapping, Text, Type, Union
import redis

from diffsync import DiffSync, DiffSyncModel
from models import Employee
from const import REDIS_HOST, REDIS_PORT


class RedisEmployee(Employee):
    """Extend the Employee object in Redis."""

    @classmethod
    def create(cls, diffsync: "DiffSync", ids: dict, attrs: dict):
        """Create an Employee record in Redis.

        Args:
            diffsync: The master data store for other DiffSyncModel instances that we might need to reference
            ids: Dictionary of unique-identifiers needed to create the new object
            attrs: Dictionary of additional attributes to set on the new object

        Returns:
            Employee: DiffSync object newly created
        """
        # Create the new employee in Redis.
        diffsync.redis.set(
            username=ids.get("username"),
            company=attrs.get("company"),
            job=attrs.get("job"),
            ssn=attrs.get("ssn"),
            residence=attrs.get("residence"),
            name=attrs.get("name"),
            mail=attrs.get("mail"),
        )
        print(f"Created Employee : {ids} | {attrs}")

        # Add the newly created remote_id and create the internal object for this resource.
        item = super().create(ids=ids, diffsync=diffsync, attrs=attrs)
        return item

    def update(self, attrs: dict):
        """Update an Employee object in Redis.

        Args:
            attrs: Dictionary of attributes to update on the object

        Returns:
            DiffSyncModel: this instance, if all data was successfully updated.
            None: if data updates failed in such a way that child objects of this model should not be modified.

        Raises:
            ObjectNotUpdated: if an error occurred.
        """
        self.diffsync.redis.hset(attrs["username"], None, None, attrs)

        return super().update(attrs)

    def delete(self):
        """Delete an Employee object in Redis.

        Returns:
            Employee: DiffSync object
        """
        # Delete the employee object using it's unique identifier, username.
        self.diffsync.redis.delete(self.username)

        super().delete()
        return self

    @classmethod
    def convert_from(cls, diffsync, obj):
        """Convert a Redis Employee object into an Employee object."""
        return cls(
            diffsync=diffsync,
            name=obj[b"name"],
            company=obj[b"company"],
            job=obj[b"job"],
            ssn=obj[b"ssn"],
            residence=obj[b"residence"],
            username=obj[b"username"],
            mail=obj[b"mail"],
        )

    # -----------------------------------------------------
    # Redefine the default methods to access the objects from the store to implement a storeless adapter
    # -----------------------------------------------------
    @classmethod
    def get_all(cls, diffsync):
        """Get all Employee objects from Redis."""
        results = []
        for key in diffsync.redis.keys("*"):
            results.append(cls.convert_from(diffsync, diffsync.redis.hgetall(key)))
        return results

    @classmethod
    def get_by_uids(cls, diffsync, uids):
        """Get a list of Employees identified by their unique identifiers."""
        results = []
        for key in diffsync.redis.mget(uids):
            results.append(cls.convert_from(diffsync, diffsync.redis.hgetall(key)))
        return results

    @classmethod
    def get(cls, diffsync, identifier):
        """Return an instance of an Employee based on their unique identifier."""
        if isinstance(identifier, str):
            employee = diffsync.redis.hgetall(identifier)
        elif isinstance(identifier, dict):
            employee = diffsync.redis.hgetall(**identifier)
        else:
            raise TypeError

        return cls.convert_from(diffsync, employee)


class RedisAdapter(DiffSync):
    """Example of a DiffSync adapter implementation."""

    employee = RedisEmployee

    top_level = ["employee"]

    type = "Redis"

    def __init__(self, *args, **kwargs):
        """Initialize the redis client."""
        self.redis = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)
        super().__init__(*args, **kwargs)

    def load(self):
        """Nothing to load here since this adapter is not leveraging the internal datastore."""

    def get(
        self, obj: Union[Text, DiffSyncModel, Type[DiffSyncModel]], identifier: Union[Text, Mapping]
    ) -> DiffSyncModel:
        """Get one object from the data store based on its unique id.

        This method is acting as passthrough and it's calling the same method on the model itself.

        Args:
            obj: DiffSyncModel class or instance, or modelname string, that defines the type of the object to retrieve
            identifier: Unique ID of the object to retrieve, or dict of unique identifier keys/values

        Raises:
            ValueError: if obj is a str and identifier is a dict (can't convert dict into a uid str without a model class)
            ObjectNotFound: if the requested object is not present
        """
        if isinstance(obj, str):
            obj = getattr(self, obj)

        return obj.get(diffsync=self, identifier=identifier)

    def get_all(self, obj: Union[Text, DiffSyncModel, Type[DiffSyncModel]]) -> List[DiffSyncModel]:
        """Get all objects of a given type.

        This method is acting as passthrough and it's calling the same method on the model itself.

        Args:
            obj: DiffSyncModel class or instance, or modelname string, that defines the type of the objects to retrieve
        Returns:
            List[DiffSyncModel]: List of Object
        """
        if isinstance(obj, str):
            obj = getattr(self, obj)

        return obj.get_all(diffsync=self)

    def get_by_uids(
        self, uids: List[Text], obj: Union[Text, DiffSyncModel, Type[DiffSyncModel]]
    ) -> List[DiffSyncModel]:
        """Get multiple objects from the store by their unique IDs/Keys and type.

        This method is acting as passthrough and it's calling the same method on the model itself.

        Args:
            uids: List of unique id / key identifying object in the database.
            obj: DiffSyncModel class or instance, or modelname string, that defines the type of the objects to retrieve

        Raises:
            ObjectNotFound: if any of the requested UIDs are not found in the store
        """
        if isinstance(obj, str):
            obj = getattr(self, obj)

        return obj.get_by_uids(diffsync=self, uids=uids)

    def add(self, obj: DiffSyncModel):
        """Add a DiffSyncModel object to the store.

        Args:
            obj (DiffSyncModel): Object to store

        Raises:
            ObjectAlreadyExists: if an object with the same uid is already present
        """

    def remove(self, obj: DiffSyncModel, remove_children: bool = False):
        """Remove a DiffSyncModel object from the store.

        Args:
            obj (DiffSyncModel): object to remove
            remove_children (bool): If True, also recursively remove any children of this object

        Raises:
            ObjectNotFound: if the object is not present
        """
