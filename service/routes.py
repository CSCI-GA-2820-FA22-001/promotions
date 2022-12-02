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
# Configure the Root route before OpenAPI
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
        elif args['start_date']:
            app.logger.info('Filtering by start date %s', args['start_date'])
            all_promotions = Promotion.find_by_start_date(args['start_date'])
        elif args['expiration_date']:
            app.logger.info('Filtering by end date %s', args['expiration_date'])
            all_promotions = Promotion.find_by_expiration_date(args['expiration_date'])
        else:
            app.logger.info('Returning unfiltered list.')
            all_promotions = Promotion.all()
        results = [promo.serialize() for promo in all_promotions]
        app.logger.info("Returning %d promotions", len(results))
        return results, status.HTTP_200_OK

    # ------------------------------------------------------------------
    # CREATE A PROMOTION
    # ------------------------------------------------------------------
    @api.doc('create_promotions')
    @api.response(400, 'The posted data was not valid')
    @api.expect(create_model)
    @api.marshal_with(promotion_model, code=201)
    def post(self):
        """
        Creates a Promotion
        This endpoint will create an Promotion based the data in the body that is posted
        """
        app.logger.info("Request to create a Promotion")
        check_content_type("application/json")
        args = request.get_json()
        promotion_exist = Promotion.find_by_name(args['name'])

        if promotion_exist:
            abort(
                status.HTTP_409_CONFLICT,
                f"Promotion with id {args['id']} and name {args['name']} already exists",
            )



        # Create the promotion
        promotion = Promotion()
        promotion = promotion.deserialize(args)
        if args['type'] == "BOGO":
            promotion.value = 0
        promotion.create()
        # Create a message to return
        message = promotion.serialize()
        location_url = api.url_for(PromotionResource, promotion_id=promotion.id, _external=True)
        app.logger.info("Promotion with ID [%s] created.", promotion.id)
        return message, status.HTTP_201_CREATED, {"Location": location_url}

######################################################################
# PATH /promotions/{promotion_id}
######################################################################
@api.route('/promotions/<promotion_id>')
@api.param('promotion_id', 'The Promotion identifier')
class PromotionResource(Resource):
    """
    PromotionResource class
    Allows the manipulation of a single Promotion
    GET /promotion{id} - Returns a Promotion with the id
    PUT /promotion{id} - Update a Promotion with the id
    DELETE /promotion{id} -  Deletes a Promotion with the id
    """
    #------------------------------------------------------------------
    # RETRIEVE A PROMOTION
    #------------------------------------------------------------------
    @api.doc('get_promotion')
    @api.response(404, 'Promotion not found')
    @api.marshal_with(promotion_model)
    def get(self, promotion_id):
        """
        Retrieve a single Promotion
        This endpoint will return a Promotion based on it's id
        """
        app.logger.info("Request for promotion with id: %s", promotion_id)
        promotion = Promotion.find(promotion_id)
        if not promotion:
            raise NotFound("Promotion with id '{}' was not found.".format(promotion_id))
        return promotion.serialize(), status.HTTP_200_OK

    #------------------------------------------------------------------
    # UPDATE AN EXISTING PROMOTION
    #------------------------------------------------------------------

    @api.doc('update_promotion')
    @api.response(404, 'Promotion not found')
    @api.response(400, 'The posted Promotion data was not valid')
    @api.expect(promotion_model)
    @api.marshal_with(promotion_model)
    def put(self, promotion_id):
        """
        Update a Promotion
        This endpoint will update a Promotion based the body that is posted
        """
        app.logger.info('Request to Update a Promotion with id [%s]', promotion_id)
        promotion = Promotion.find(promotion_id)
        if not promotion:
            abort(
                status.HTTP_404_NOT_FOUND, f"Promotion with id '{promotion_id}' was not found."
            )

        app.logger.debug('Payload = %s', api.payload)
        # Update from the json in the body of the request
        data = api.payload
        promotion = promotion.deserialize(data)
        promotion.update()

        app.logger.info(
            f"Promotion with id {id} updated"
        )

        return promotion.serialize(), status.HTTP_200_OK
    
    #------------------------------------------------------------------
    # DELETE A PROMOTION
    #------------------------------------------------------------------
    @api.doc('delete_promotion')
    @api.response(204, 'Promotion deleted')
    def delete(self, promotion_id):
        """
        Delete a Promotion
        This endpoint will delete an Promotion based the id specified in the path
        """
        app.logger.info('Request to Delete a Promotion with id [%s]', promotion_id)
        promotion = Promotion.find(promotion_id)
        if promotion:
            promotion.delete()
            app.logger.info('Promotion with id [%s] was deleted', promotion_id)

        return '', status.HTTP_204_NO_CONTENT

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

    promotion.active = not promotion.active
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
