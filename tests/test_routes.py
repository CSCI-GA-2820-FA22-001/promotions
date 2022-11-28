"""
TestYourResourceModel API Service Test Suite

Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
"""

import os
import logging
import unittest
from service.models import Promotion, DataValidationError, db
from service.common import status
from service import app
from .factory import PromotionFactory
from datetime import datetime, timedelta

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/testdb"
)

######################################################################
#  T E S T   C A S E S
######################################################################
class TestPromotionRoutes(unittest.TestCase):
    """ REST API Server Tests """

    @classmethod
    def setUpClass(cls):
        """ This runs once before the entire test suite """
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Promotion.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """ This runs once after the entire test suite """
        db.session.close()

    def setUp(self):
        """ This runs before each test """
        db.drop_all()  # clean up the last tests
        db.create_all()  # create new tables
        self.app = app.test_client()

    def tearDown(self):
        """ This runs after each test """
        db.session.remove()
        db.drop_all()

    def _create_promotions(self, count):
        """ Factory method to create promotions in bulk """
        promotions = []
        for _ in range(count):
            test_promotion = PromotionFactory()
            resp = self.app.post(
                "/promotions", json=test_promotion.serialize(), content_type="application/json"
            )
            self.assertEqual(
                resp.status_code, status.HTTP_201_CREATED, "Could not create test promotion"
            )
            new_promotion = resp.get_json()
            test_promotion.id = new_promotion["id"]
            test_promotion.active = new_promotion["active"]
            test_promotion.type = new_promotion["type"]
            test_promotion.value = new_promotion["value"]
            test_promotion.product_id = new_promotion["product_id"]
            test_promotion.start_date = new_promotion["start"]
            test_promotion.expiration_date = new_promotion["end"]
            promotions.append(test_promotion)
        return promotions

    ######################################################################
    # PLACE TEST CASES HERE
    ######################################################################

    def test_index(self):
        """ It should call the home page """
        resp = self.app.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_create_promotion(self):
        """ Create a new Promotion """
        test_promotion = PromotionFactory()
        logging.debug(test_promotion)
        resp = self.app.post(
            "/promotions", json=test_promotion.serialize(), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        # Check the data is correct
        new_promotion = resp.get_json()

        self.assertEqual(new_promotion["name"], test_promotion.name, "Name does not match")
        self.assertEqual(new_promotion["type"], test_promotion.type.name, "type does not match")
        self.assertEqual(new_promotion["value"], test_promotion.value, "value does not match")
        self.assertEqual(new_promotion["active"], test_promotion.active, "active status does not match")
        self.assertEqual(datetime.fromisoformat(new_promotion["start"]), test_promotion.start_date, "start date does not match")
        self.assertEqual(datetime.fromisoformat(new_promotion["end"]), test_promotion.expiration_date, "end date does not match")

    def test_create_duplicate(self):
        """It should not Create a duplicate Promotion"""
        test_item = PromotionFactory()
        response = self.app.post("/promotions", json=test_item.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        print(test_item.serialize())
        response = self.app.post("/promotions", json=test_item.serialize())
        print(test_item.serialize())
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

    def test_get_promotion(self):
        """ Get a single Promotion """
        # get the id of a promotion
        test_promotion = self._create_promotions(1)[0]
        logging.debug(test_promotion)
        resp = self.app.get(
            "/promotions/{}".format(test_promotion.id), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data["name"], test_promotion.name)
        
    def test_list_promotion(self):
        """ List all promotions in the database """
        # create two promotions
        test_promotion00 = self._create_promotions(1)[0]
        test_promotion01 = self._create_promotions(1)[0]

        # if it gets 200 status, we pass
        resp = self.app.get("/promotions")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        # check that the ID of test promos match JSON returned
        data = resp.get_json()
        print("Test List  ", data)
        self.assertEqual(data[0]['id'], test_promotion00.id)
        self.assertEqual(data[1]['id'], test_promotion01.id)

    def test_list_promotion_by_type(self):
        # get the type of a promotion
        test_promotion_type = self._create_promotions(1)[0]
        logging.debug(test_promotion_type)
        resp = self.app.get("/promotions", query_string="type={}".format(test_promotion_type.type))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data[0]['type'], test_promotion_type.type)

    def test_list_promotion_by_value(self):
        # get the type of a promotion
        test_promotion_value = self._create_promotions(1)[0]
        logging.debug(test_promotion_value)
        resp = self.app.get("/promotions", query_string="value={}".format(test_promotion_value.value))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data[0]['value'], test_promotion_value.value)

    def test_list_promotion_by_name(self):
        # get the type of a promotion
        test_promotion_name = self._create_promotions(1)[0]
        logging.debug(test_promotion_name)
        resp = self.app.get("/promotions", query_string="name={}".format(test_promotion_name.name))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data[0]['name'], test_promotion_name.name)

    def test_list_promotion_by_active(self):
        test_promotion_list = self._create_promotions(5)
        active_promotions = [promo for promo in test_promotion_list if promo.active is True]
        inactive_promotions = [promo for promo in test_promotion_list if promo.active is False]
        active_count = len(active_promotions)
        inactive_count = len(inactive_promotions)
        logging.debug("Active Promotions [%d] %s", active_count, active_promotions)
        logging.debug("Inactive Promotions [%d] %s", inactive_count, inactive_promotions)

        # test for active
        resp = self.app.get(
            "/promotions", query_string="active=true"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), active_count)
        # check the data just to be sure
        for promo in data:
            self.assertEqual(promo["active"], True)

         # test for unavailable
        resp = self.app.get(
            "/promotions", query_string="active=false"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), inactive_count)
        # check the data just to be sure
        for promo in data:
            self.assertEqual(promo["active"], False)

    def test_update_promotion(self):
        """ Update an existing Promotion """
        # create a promotion to update
        test_promotion = PromotionFactory()
        logging.debug(test_promotion)
        resp = self.app.post(
            "/promotions", json=test_promotion.serialize(), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        # update the promotion
        new_promotion = resp.get_json()
        new_promotion["name"] = "dummy_promo"
        resp = self.app.put(
            "/promotions/{}".format(new_promotion["id"]),
            json=new_promotion,
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        updated_promotion = resp.get_json()
        self.assertEqual(updated_promotion["name"], "dummy_promo")

        #try to update invalid promotion
        invalid_resp = self.app.put(
            "/promotions/9999",
            json=new_promotion,
            content_type="application/json",
        )
        self.assertEqual(invalid_resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_promotion(self):
        """ Delete a Promotion """
        test_promotion = self._create_promotions(1)[0]
        logging.debug(test_promotion)
        resp = self.app.delete(
            "/promotions/{}".format(test_promotion.id), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(resp.data), 0)
        # make sure they are deleted
        resp = self.app.get(
            "/promotions/{}".format(test_promotion.id), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_bad_request(self):
        """It should not Create when sending the wrong data"""
        test_promotion = PromotionFactory()
        test_promotion.name = 2
        resp = self.app.post("/promotions", json=test_promotion.serialize())
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_method_not_allowed(self):
        """It should not allow an illegal method call"""
        resp = self.app.put("/promotions", json={"not": "today"})
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_unsupported_media_type(self):
        """It should not Create when sending wrong media type"""
        account = PromotionFactory()
        resp = self.app.post(
            "/promotions", json=account.serialize(), content_type="test/html"
        )
        self.assertEqual(resp.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_health_check(self):
        """health endpoint should return {"status":"OK}, 200"""
        resp = self.app.get("/health")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_list_promotion_by_product_id(self):
        # get the product id of a promotion
        test_promotion_prod_id = self._create_promotions(1)[0]
        logging.debug(test_promotion_prod_id)
        resp = self.app.get("/promotions", query_string="product_id={}".format(test_promotion_prod_id.product_id))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data[0]['product_id'], test_promotion_prod_id.product_id)


    def test_activate_promotion(self):
        """ Activate an existing promotion """
        # create a promotion to activate
        test_promotion = self._create_promotions(1)[0]
        #Deactivate the promotion
        test_promotion.active = False
        # activate the promotion using service
        print("In test ", test_promotion.id)
        resp_activate = self.app.put(
            "/promotions/{}/activate".format(test_promotion.id),
            content_type="application/json"
        )

        self.assertEqual(resp_activate.status_code, status.HTTP_200_OK)
        self.assertEqual(resp_activate.get_json()['active'], True)

    def test_deactivate_promotion(self):
        """ Deactivate an existing promotion """
        # create a promotion to activate
        test_promotion = self._create_promotions(1)[0]
        #activate the promotion
        test_promotion.active = True
        # deactivate the promotion using endpoint
        resp_deactivate = self.app.put(
            "/promotions/{}/deactivate".format(test_promotion.id),
            content_type="application/json"
        )

        self.assertEqual(resp_deactivate.status_code, status.HTTP_200_OK)
        self.assertEqual(resp_deactivate.get_json()['active'], False)

    def test_activate_promotion_not_found(self):
        """ Activate a non existing promotion """
        # create a promotion to activate
        test_promotion = self._create_promotions(1)[0]
        #Deactivate the promotion
        test_promotion.active = False
        test_id = test_promotion.id + 1
        # activate the promotion using service
        resp_activate = self.app.put(
            "/promotions/{}/activate".format(test_id),
            content_type="application/json"
        )
        self.assertEqual(resp_activate.status_code, status.HTTP_404_NOT_FOUND)

    def test_deactivate_promotion_not_found(self):
        """ Deactivate a non existing promotion """
        # create a promotion to activate
        test_promotion = self._create_promotions(1)[0]
        #activate the promotion
        test_promotion.active = True
        test_id = test_promotion.id + 1
        # deactivate the promotion using endpoint
        resp_deactivate = self.app.put(
            "/promotions/{}/deactivate".format(test_id),
            content_type="application/json"
        )

        self.assertEqual(resp_deactivate.status_code, status.HTTP_404_NOT_FOUND)
