"""
Test cases for Promotion Model

"""
from itertools import product
import os
import logging
import unittest
from service.models import Promotion,PromotionType, DataValidationError, db
from service import app


DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/testdb"
)

######################################################################
#  <your resource name>   M O D E L   T E S T   C A S E S
######################################################################
class TestPromotion(unittest.TestCase):
    """ Test Cases for Promotion Model """

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
        db.session.query(Promotion).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """ This runs after each test """
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_promotion(self):
        prom = Promotion(name="Promo1",product_id=1,type=PromotionType.PERCENTAGE,value=20,active=True)
        self.assertEqual(prom.name,"Promo1")
        self.assertEqual(prom.product_id,1)
        self.assertEqual(prom.type,PromotionType.PERCENTAGE)
        self.assertEqual(prom.value,20)
        self.assertTrue(prom.active)
        self.assertTrue(prom is not None)

        promos = Promotion.all()
        self.assertEqual([],promos)
        self.assertEqual(prom.id, None)
        prom.create()
        self.assertIsNotNone(prom.id)
        promos = Promotion.all()
        self.assertEqual(len(promos), 1)
        print(repr(promos))
        #self.assertEqual(repr(promos),)

    def create_promotion_with_no_product_id(self):
        """ Create an promotion with no product id """
        prom = Promotion(name="Promo1",type=PromotionType.PERCENTAGE,value=20,active=True)
        self.assertRaises(DataValidationError, prom.create)

    def test_update_promotion(self):
        prom = Promotion(name="Promo1",product_id=1,type=PromotionType.BOGO,value=20,active=True)
        prom.create()
        initial_id = prom.id
        prom.name = "Promo2"
        prom.update()
        self.assertEqual(prom.id, initial_id)
        self.assertEqual(prom.name,"Promo2")

    def test_update_promotion_with_no_prod_id(self):
        """ Update a promotion with no product id """
        prom = Promotion(name="Promo1",type=PromotionType.FIXED,value=20,active=True)
        prom.id=1
        self.assertRaises(DataValidationError, prom.update)

    def test_update_promotion_with_no_id(self):
        """ Update a promotion with no id """
        prom = Promotion(name="Promo1",type=PromotionType.BOGO,value=20,active=True)
        prom.id= None
        self.assertRaises(DataValidationError, prom.update)

    def test_delete_promotion(self):
        prom = Promotion(name="Promo1",product_id=1,type=PromotionType.BOGO,value=20,active=True)
        prom.create()
        self.assertEqual(len(Promotion.all()), 1)
        prom.delete()
        self.assertEqual(len(Promotion.all()), 0)

    def test_serialize_deserialize_promotion(self):
        prom = Promotion(name="Promo1",product_id=1,type=PromotionType.BOGO,value=20,active=True)
        data= prom.serialize()
        self.assertNotEqual(data, None)
        self.assertIn("id", data)
        self.assertEqual(data["id"], prom.id)
        self.assertIn("name", data)
        self.assertEqual(data["name"], prom.name)
        self.assertIn("product_id", data)
        self.assertEqual(data["product_id"], prom.product_id)
        self.assertIn("type", data)
        self.assertEqual(data["type"], prom.type.name)
        self.assertIn("value", data)
        self.assertEqual(data["value"], prom.value)

        data["name"]="Promo2"
        data["product_id"]=2
        data["value"]=10
        prom.deserialize(data)
        self.assertEqual(prom.name,"Promo2")
        self.assertEqual(prom.product_id,2)
        self.assertEqual(prom.value,10)

        #test invalid deserial:
        invalid_data = "..."
        prom2 = Promotion()
        self.assertRaises(TypeError, prom2.deserialize, invalid_data)

        #test missing
        missing_data = {"id": 1, "name": "Promotion"}
        prom3 = Promotion()
        self.assertRaises(DataValidationError, prom3.deserialize, missing_data)

    def test_deserialize_with_missing_product_id(self):
        prom = Promotion(name="Promo1",type=PromotionType.BOGO,value=20,active=True)
        data= prom.serialize()
        self.assertRaises(DataValidationError, prom.deserialize, data)

    def test_find_promos(self):
        prom1 = Promotion(name="Promo1",product_id=1,type=PromotionType.BOGO,value=20,active=True)
        prom2 = Promotion(name="Promo2",product_id=2,type=PromotionType.FIXED,value=30,active=False)
        prom3 = Promotion(name="Promo3",product_id=3,type=PromotionType.PERCENTAGE,value=40,active=True)
        prom1.create()
        prom2.create()
        prom3.create()
        self.assertEqual(len(Promotion.all()),3)

        #find by id
        search2 = Promotion.find(prom2.id)
        self.assertIsNot(search2, None)
        self.assertEqual(search2.name, prom2.name)

        #find by name
        search3 = Promotion.find_by_name("Promo3")
        self.assertIsNot(search2, None)
        self.assertEqual(search3[0].name, prom3.name)
        self.assertEqual(search3[0].product_id, prom3.product_id)

        #find by product id
        search4 = Promotion.find_by_product_id(prom1.product_id)
        self.assertIsNot(search4, None)
        self.assertEqual(search4[0].name, prom1.name)
        self.assertEqual(search4[0].product_id, prom1.product_id)


