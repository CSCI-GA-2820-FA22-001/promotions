"""
Promotion Service

This microservice handles the lifecycle of Promotions
"""

from flask import jsonify, request, url_for, make_response, abort
from service.models import Promotion, PromotionType, DataValidationError
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
create_model = api.model(
    'Promotion',
    {
        'name': fields.String(required=False, description='The name of the promotion'),
        'product_id': fields.Integer(
            required=False, description='The product id associated with this promotion'
        ),
        'type': fields.String(required=False , description='The type of promotion [BOGO | DISCOUNT | FIXED]'),
        'value': fields.Integer(
            required=False,
            description='The value of the promotion based on promo type',
        ),
        'start_date': fields.DateTime(
            required=False, description='The start date of the promotion'
        ),
        'expiration_date': fields.DateTime(
            required=False, description='The end date of the promotion'
        ),
        'active': fields.Boolean(required=False,
                                description='Is the promotion active?')
    }
)

promotion_model = api.inherit(
    'PromotionModel',
    create_model,
    {
        'id': fields.Integer(
            readOnly=True, description='The unique id assigned internally by service'
        ),
    },
)

# query string arguments
# --------------------------------------------------------------------------------------------------
promotion_args = reqparse.RequestParser()
promotion_args.add_argument('name', type=str, required=False, location='args', help='List Promotions by name')
promotion_args.add_argument('product_id', type=int, required=False, location='args', help='The product id associated with this promotion')
promotion_args.add_argument('type', type=str, required=False, location='args', help='The type of promotion [BOGO | DISCOUNT | FIXED]')
promotion_args.add_argument('value', type=int, required=False, location='args', help='The value of the promotion based on promo type')
promotion_args.add_argument('start_date', type=str, required=False, location='args', help='List Promotions by start date')
promotion_args.add_argument('expiration_date', type=str, required=False, location='args', help='List Promotions by end date')
promotion_args.add_argument('active', type=inputs.boolean, required=False, location='args', help='List Promotions by active status')


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
#  PATH: /promotions
######################################################################
@api.route('/promotions', strict_slashes=False)
class PromotionCollection(Resource):
    """ Handles all interactions with collections of Promotions """

    # ------------------------------------------------------------------
    # LIST ALL PROMOTIONS
    # ------------------------------------------------------------------
    @api.doc('list_promotions')
    @api.expect(promotion_args, validate=True)
    @api.marshal_list_with(promotion_model)
    def get(self):
        """ Returns all of the Promotions """
        args = promotion_args.parse_args()
        all_promotions = []
        app.logger.info("Request to list promotions based on query string %s ...", args)
        if args['name']:
            app.logger.info('Filtering by name: %s', args['name'])
            all_promotions = Promotion.find_by_name(args['name'])
        elif args['product_id']:
            app.logger.info('Filtering by product id %s', args['product_id'])
            all_promotions = Promotion.find_by_product_id(args['product_id'])
        elif args['type']:
            app.logger.info('Filtering by type %s', args['type'])
            all_promotions = Promotion.find_by_type(args['type'])
        elif args['value']:
            app.logger.info('Filtering by value %s', args['value'])
            all_promotions = Promotion.find_by_value(args['value'])
        elif args['active']:
            app.logger.info('Filtering by active %s', args['active'])
            all_promotions = Promotion.find_by_active(args['active'])
        else:
            app.logger.info('Returning unfiltered list.')
            all_promotions = Promotion.all()
        results = [promo.serialize() for promo in all_promotions]
        app.logger.info("Returning %d promotions", len(results))
        return results, status.HTTP_200_OK

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
    args = request.get_json()
    promotion_args = Promotion.find(args['id'])
    if promotion_args:
        abort(
            status.HTTP_409_CONFLICT,
            f"Promotion with id {args['id']} and name {args['name']} already exists",
        )

     # Create the account
    promotion = Promotion()
    promotion = promotion.deserialize(args)
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
            status.HTTP_404_NOT_FOUND, f"Promotion with id '{promotion_id}' was not found."
        )

    # Update from the json in the body of the request
    promotion = promotion.deserialize(request.get_json())
    promotion.update()

    app.logger.info(
        f"Promotion with id {id} updated"
    )

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
        abort(status.HTTP_404_NOT_FOUND, "Promotion with id '{}' was not found".format(promotion_id))

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
        abort(status.HTTP_404_NOT_FOUND, "Promotion with id '{}' was not found".format(promotion_id))
    promotion.active = False
    promotion.update()
    return promotion.serialize(), status.HTTP_200_OK
