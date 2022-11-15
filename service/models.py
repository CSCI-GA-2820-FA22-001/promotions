"""
Models for Promotion

All of the models are stored in this module
"""
import logging
from flask_sqlalchemy import SQLAlchemy

logger = logging.getLogger("flask.app")

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()


class DataValidationError(Exception):
    """ Used for an data validation errors when deserializing """

    pass


class Promotion(db.Model):
    """
    Class that represents a Promotion
    """

    app = None

    # Table Schema
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(63))
    # products = db.Column(db.String(63), nullable=False) #Affected product type. Can be "All"
    product_id = db.Column(db.Integer, nullable = False)
    type = db.Column(db.String(63), nullable=False) #Types: BOGO, Flat, Percentage
    value = db.Column(db.Integer, default=0) #0 for Bogo
    active = db.Column(db.Boolean(), nullable=False, default=False)

    def __repr__(self):
        return "<Promotion %r id=[%s]>" % (self.name, self.id)

    def create(self):
        """
        Creates a Promotion to the database
        """
        if self.product_id is None:
            raise DataValidationError("Product Id cannot be empty")

        logger.info("Creating %s", self.name)
        self.id = None  # id must be none to generate next primary key
        db.session.add(self)
        db.session.commit()

    def update(self):
        """
        Updates a Promotion to the database
        """

        if not self.id or not isinstance(self.id, int):
            raise DataValidationError("Update called with invalid id field")

        if self.product_id is None or not isinstance(self.product_id, int):
            raise DataValidationError("Product Id is not valid")

        logger.info("Saving %s", self.name)
        db.session.commit()

    def delete(self):
        """ Removes a Promotion from the data store """
        logger.info("Deleting %s", self.name)
        db.session.delete(self)
        db.session.commit()

    def serialize(self):
        """ Serializes a Promotion into a dictionary """
        return {
            "id": self.id, 
            "name": self.name,
            "product_id": self.product_id,
            "type": self.type,
            "value": self.value,
            "active": self.active
        }

    def deserialize(self, data):
        """
        Deserializes a Promotion from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:

            self.product_id = data["product_id"]
            # check if product id is Integer
            if self.product_id is None or not isinstance(self.product_id, int):
                raise DataValidationError("Product Id must be an Integer")

            self.name = data["name"]
            self.type = data["type"]
            self.value = data["value"]
            self.active = data["active"]

        except KeyError as error:
            raise DataValidationError(
                "Invalid Promotion: missing " + error.args[0]
            )
        except TypeError as error:
            raise DataValidationError(
                "Invalid Promotion: body of request contained bad or no data - "
                "Error message: " + error
            )
        return self

    @classmethod
    def init_db(cls, app):
        """ Initializes the database session """
        logger.info("Initializing database")
        cls.app = app
        # This is where we initialize SQLAlchemy from the Flask app
        db.init_app(app)
        app.app_context().push()
        db.create_all()  # make our sqlalchemy tables

    @classmethod
    def all(cls):
        """ Returns all of the Promotions in the database """
        logger.info("Processing all Promotions")
        return cls.query.all()

    @classmethod
    def find(cls, promotion_id):
        """ Finds a Promotion by it's ID """
        logger.info("Processing lookup for id %s ...", promotion_id)
        return cls.query.get(promotion_id)

    @classmethod
    def find_by_name(cls, name):
        """Returns all Promotions with the given name

        Args:
            name (string): the name of the Promotions you want to match
        """
        logger.info("Processing name query for %s ...", name)
        return cls.query.filter(cls.name == name)

    @classmethod
    def find_by_type(cls, type):
        """Returns all Promotions with the given type

        Args:
            type (string): the type of the Promotions you want to match
        """
        logger.info("Processing type query for %s ...", type)
        return cls.query.filter(cls.type == type).all()

    @classmethod
    def find_by_value(cls, value):
        """Returns all Promotions with the given value

        Args:
            value (Integer): the type of the Promotions you want to match
        """
        logger.info("Processing value query for %s ...", value)
        return cls.query.filter(cls.value == value).all()

    @classmethod
    def find_by_active(cls, active):
        """Returns all Promotions with the given active status

        Args:
            active (boolean): the type of the Promotions you want to match
        """
        logger.info("Processing active query for %s ...", active)
        return cls.query.filter(cls.active == active).all()
    


    @classmethod
    def find_by_product_id(cls, product_id: int):
        """Returns the promotion with product_id: product_id """
        logger.info("Processing product_id query for %s ...", product_id)
        return cls.query.filter(cls.product_id == product_id).all()
