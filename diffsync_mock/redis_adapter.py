import redis

from typing import List, Mapping, Text, Type, Union
from diffsync import DiffSync, DiffSyncModel
from diffsync_mock.models import Employee
from diffsync_mock.const import REDIS_HOST, REDIS_PORT


class RedisEmployee(Employee):
    """Extend the Country to manage Country in Nautobot. CREATE/UPDATE/DELETE.

    Country are represented in Nautobot as a dcim.region object as well but a country must have a parent.
    Subregion information will be store in the description of the object in Nautobot
    """

    @classmethod
    def create(cls, diffsync: "DiffSync", ids: dict, attrs: dict):
        """Create a country object in Nautobot.

        Args:
            diffsync: The master data store for other DiffSyncModel instances that we might need to reference
            ids: Dictionary of unique-identifiers needed to create the new object
            attrs: Dictionary of additional attributes to set on the new object

        Returns:
            NautobotCountry: DiffSync object newly created
        """

        # Create the new country in Nautobot and attach it to its parent
        emp = diffsync.redis.set(
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
        """Update a country object in Nautobot.

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
        """Delete a country object in Nautobot.

        Returns:
            NautobotCountry: DiffSync object
        """
        # Retrieve the pynautobot object and delete the object in Nautobot
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
        """Get all Country objects from Nautobot"""
        results = []
        for key in diffsync.redis.keys('*'):
            results.append(cls.convert_from(diffsync, diffsync.redis.hgetall(key)))
        return results

    @classmethod
    def get_by_uids(cls, diffsync, uids):
        """Get a list of Country identified by their unique identifiers."""
        results = []
        for key in diffsync.redis.mget(uids):
            results.append(cls.convert_from(diffsync, diffsync.redis.hgetall(key)))
        return results

    @classmethod
    def get(cls, diffsync, identifier):
        """Return an instance of Country based on its unique identifier."""
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

    # Since all countries are associated with a region, we don't need to list country here
    # When doing a diff or a sync between 2 adapters,
    #  diffsync will recursively check all models defined at the top level and their children.
    top_level = ["employee"]

    # Human readable name of the Adapter,
    # mainly used when doing a diff to indicate where each data is coming from
    type = "Redis"

    def load(self):
        """Nothing to load here since this adapter is not leveraging the internal datastore."""
        self.redis = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)
        pass

    # -----------------------------------------------------
    # Redefine the default methods to access the objects from the store to implement a storeless adapter
    #  get / get_all / get_by_uids, add and remove are the main methods to interact with the datastore.
    # For get / get_all / get_by_uids the adapter is acting as passthrough and it's calling the same
    #  method on the model itself
    # -----------------------------------------------------
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
        pass

    def remove(self, obj: DiffSyncModel, remove_children: bool = False):
        """Remove a DiffSyncModel object from the store.

        Args:
            obj (DiffSyncModel): object to remove
            remove_children (bool): If True, also recursively remove any children of this object

        Raises:
            ObjectNotFound: if the object is not present
        """
        pass
