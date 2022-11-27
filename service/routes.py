"""
Promotion Service

This microservice handles the lifecycle of Promotions
"""

from flask import jsonify, request, url_for, make_response, abort
from service.models import Promotion
from service.common import status  # HTTP Status Codes
from flask_restx import Api, Resource, fields, reqparse, inputs
from . import app  # Import Flask application
from werkzeug.exceptions import NotFound

######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Root URL response"""
    """ Index page """
    return app.send_static_file('index.html')

######################################################################
# Configure Swagger before initializing it
######################################################################
api = Api(app,
          version='1.0.0',
          title='Promotions REST API Service',
          description='This is the Promotions server.',
          default='promotions',
          default_label='Promotions service operations',
          doc='/apidocs', # default also could use doc='/apidocs/'
          prefix='/'
         )

#Define the create model so that the docs define what can be sent
######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################


def init_db():
    """ Initializes the SQLAlchemy app """
    global app
    Promotion.init_db(app)

def check_content_type(media_type):
    """Checks that the media type is correct"""
    content_type = request.headers.get("Content-Type")
    if content_type and content_type == media_type:
        return
    app.logger.error("Invalid Content-Type: %s", content_type)
    abort(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        f"Content-Type must be {media_type}",
    )


######################################################################
# LIST ALL Promotions
######################################################################
@app.route("/promotions", methods=["GET"])
def list_promotions():
    """Returns all of the Promotions"""

    app.logger.info("Request for Promotions list")
    all_promotions = []

    # Process the query string if any
    name = request.args.get("name")
    type = request.args.get("type")
    value = request.args.get("value")
    active = request.args.get("active")
    product_id = request.args.get("product_id")
    if name:
        all_promotions = Promotion.find_by_name(name)
    elif product_id:
        all_promotions = Promotion.find_by_product_id(product_id)
    elif type:
        all_promotions = Promotion.find_by_type(type)
    elif value:
        all_promotions = Promotion.find_by_value(value)
    elif active:
        all_promotions = Promotion.find_by_active(active)
    else:
        all_promotions = Promotion.all()

    # Return as an array of dictionaries
    results = [promo.serialize() for promo in all_promotions]

    return make_response(jsonify(results), status.HTTP_200_OK)

######################################################################
# RETRIEVE A Promotion
######################################################################
@app.route("/promotions/<int:promotion_id>", methods=["GET"])
def get_promotion(promotion_id):
    """
    Retrieve a single Promotion
    This endpoint will return an Promotion based on it's id
    """
    app.logger.info("Request for promotion with id: %s", promotion_id)
    promotion = Promotion.find(promotion_id)
    if not promotion:
        raise NotFound("Promotion with id '{}' was not found.".format(promotion_id))
    return make_response(jsonify(promotion.serialize()), status.HTTP_200_OK)

######################################################################
# CREATE A NEW Promotion
######################################################################

@app.route("/promotions", methods=["POST"])
def create_promotion():
    """
    Creates a Promotion
    This endpoint will create an Promotion based the data in the body that is posted
    """
    app.logger.info("Request to create a Promotion")
    check_content_type("application/json")

    # Create the account
    promotion = Promotion()
    promotion.deserialize(request.get_json())
    promotion.create()

    # Create a message to return
    message = promotion.serialize()
    location_url = url_for("get_promotion", promotion_id=promotion.id, _external=True)

    return make_response(
        jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}
    )


######################################################################
# UPDATE AN EXISTING Promotion
######################################################################
@app.route("/promotions/<int:promotion_id>", methods=["PUT"])
def update_promotion(promotion_id):
    """
    Update a Promotion
    This endpoint will update an Promotion based the body that is posted
    """
    app.logger.info("Request to update account with id: %s", promotion_id)
    check_content_type("application/json")

    # See if the account exists and abort if it doesn't
    promotion = Promotion.find(promotion_id)
    if not promotion:
        abort(
            status.HTTP_404_NOT_FOUND, f"Account with id '{promotion_id}' was not found."
        )

    # Update from the json in the body of the request
    promotion.deserialize(request.get_json())
    promotion.id = promotion_id
    promotion.update()

    return make_response(jsonify(promotion.serialize()), status.HTTP_200_OK)


######################################################################
# DELETE AN Promotion
######################################################################
@app.route("/promotions/<int:promotion_id>", methods=["DELETE"])
def delete_promotion(promotion_id):
    """
    Delete a Promotion
    This endpoint will delete an Promotion based the id specified in the path
    """
    app.logger.info("Request to delete account with id: %s", promotion_id)

    # Retrieve the account to delete and delete it if it exists
    promotion = Promotion.find(promotion_id)
    if promotion:
        promotion.delete()

    return make_response("", status.HTTP_204_NO_CONTENT)

######################################################################
# Health check for Kube
######################################################################
@app.route("/health", methods=["GET"])
def check_health():
    return (
        jsonify(
            status="OK",
        ),
        status.HTTP_200_OK,
    )

######################################################################
# Action Endpoint to Activate the Resource
######################################################################
@app.route("/promotions/<int:promotion_id>/activate", methods=["PUT"])
def activate_promotion(promotion_id):
    """
        Activate a Promotion
        This endpoint will activate a Promotion
    """
    app.logger.info('Request to activate promotion with id: %s', promotion_id)
    promotion = Promotion.find(promotion_id)
    if promotion == None:
        app.abort(status.HTTP_404_NOT_FOUND, "Promotion with id '{}' was not found".format(promotion_id))
    promotion.active = True
    promotion.update()
    return promotion.serialize(), status.HTTP_200_OK

######################################################################
# Action Endpoint to Deactivate the Resource
######################################################################
@app.route("/promotions/<int:promotion_id>/deactivate", methods=["PUT"])
def deactivate_promotion(promotion_id):
    """
        Deactivate a Promotion
        This endpoint will deactivate a Promotion
    """
    app.logger.info('Request to deactivate promotion with id: %s', promotion_id)
    promotion = Promotion.find(promotion_id)
    if promotion == None:
        app.abort(status.HTTP_404_NOT_FOUND, "Promotion with id '{}' was not found".format(promotion_id))
    promotion.active = False
    promotion.update()
    return promotion.serialize(), status.HTTP_200_OK
