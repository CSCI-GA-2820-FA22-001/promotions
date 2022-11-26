"""
Test cases for Promotion Model

"""
import logging
import os
import unittest
from datetime import datetime, timedelta
from itertools import product

from service import app
from service.models import DataValidationError, Promotion, PromotionType, db

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
        prom = Promotion(name="Promo1",product_id=1,type=PromotionType.PERCENTAGE,value=20,active=True,
        start_date = datetime(2022, 11, 10), expiration_date = datetime(2022, 11, 20))
        self.assertEqual(prom.name,"Promo1")
        self.assertEqual(prom.product_id,1)
        self.assertEqual(prom.type,PromotionType.PERCENTAGE)
        self.assertEqual(prom.value,20)
        self.assertTrue(prom.active)
        self.assertTrue(prom is not None)
        self.assertEqual(prom.start_date, datetime(2022, 11, 10))
        self.assertEqual(prom.expiration_date, datetime(2022, 11, 20))

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
        prom = Promotion(name="Promo1",type=PromotionType.PERCENTAGE,value=20,active=True,
        start_date = datetime(2022, 11, 10), expiration_date = datetime(2022, 11, 20))
        self.assertRaises(DataValidationError, prom.create)

    def test_update_promotion(self):
        prom = Promotion(name="Promo1",product_id=1,type=PromotionType.BOGO,value=20,active=True,
        start_date = datetime(2022, 11, 10), expiration_date = datetime(2022, 11, 20))
        prom.create()
        initial_id = prom.id
        prom.name = "Promo2"
        prom.update()
        self.assertEqual(prom.id, initial_id)
        self.assertEqual(prom.name,"Promo2")

    def test_update_promotion_with_no_prod_id(self):
        """ Update a promotion with no product id """
        prom = Promotion(name="Promo1",type=PromotionType.FIXED,value=20,active=True,
        start_date = datetime(2022, 11, 10), expiration_date = datetime(2022, 11, 20))
        prom.id=1
        self.assertRaises(DataValidationError, prom.update)

    def test_update_promotion_with_no_id(self):
        """ Update a promotion with no id """
        prom = Promotion(name="Promo1",type=PromotionType.BOGO,value=20,active=True,
        start_date = datetime(2022, 11, 10), expiration_date = datetime(2022, 11, 20))

        prom.id= None
        self.assertRaises(DataValidationError, prom.update)

    def test_delete_promotion(self):
        prom = Promotion(name="Promo1",product_id=1,type=PromotionType.BOGO,value=20,active=True,
        start_date = datetime(2022, 11, 10), expiration_date = datetime(2022, 11, 20))
        prom.create()
        self.assertEqual(len(Promotion.all()), 1)
        prom.delete()
        self.assertEqual(len(Promotion.all()), 0)

    def test_serialize_deserialize_promotion(self):
        prom = Promotion(name="Promo1",product_id=1,type=PromotionType.BOGO,value=20,active=True,
        start_date = datetime(2022, 11, 10), expiration_date = datetime(2022, 11, 20))

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
        self.assertIn("start", data)
        self.assertEqual(datetime.fromisoformat(data["start"]), prom.start_date)
        self.assertIn("end", data)
        self.assertEqual(datetime.fromisoformat(data["end"]), prom.expiration_date)

        data["name"]="Promo2"
        data["product_id"]=2
        data["value"]=10
        data["start"]=datetime(2022, 12, 10)
        data["end"]=datetime(2022, 12, 20)
        prom.deserialize(data)
        self.assertEqual(prom.name,"Promo2")
        self.assertEqual(prom.product_id,2)
        self.assertEqual(prom.value,10)
        self.assertEqual(prom.start_date,datetime(2022, 12, 10))
        self.assertEqual(prom.expiration_date,datetime(2022, 12, 20))

        #test invalid deserial:
        invalid_data = "..."
        prom2 = Promotion()
        self.assertRaises(TypeError, prom2.deserialize, invalid_data)

        #test missing
        missing_data = {"id": 1, "name": "Promotion"}
        prom3 = Promotion()
        self.assertRaises(DataValidationError, prom3.deserialize, missing_data)

    def test_deserialize_with_missing_product_id(self):
        prom = Promotion(name="Promo1",type=PromotionType.BOGO,value=20,active=True,
        start_date = datetime(2022, 5, 10), expiration_date = datetime(2022, 5, 20))
        data= prom.serialize()
        self.assertRaises(DataValidationError, prom.deserialize, data)

    def test_find_promos(self):
        prom1 = Promotion(name="Promo1",product_id=1,type=PromotionType.BOGO,value=20,active=True,
        start_date = datetime(2022, 5, 10), expiration_date = datetime(2022, 5, 20))

        prom2 = Promotion(name="Promo2",product_id=2,type=PromotionType.FIXED,value=30,active=False,
        start_date = datetime(2022, 6, 10), expiration_date = datetime(2022, 6, 20))

        prom3 = Promotion(name="Promo3",product_id=3,type=PromotionType.PERCENTAGE,value=40,active=True,
        start_date = datetime(2022, 7, 10), expiration_date = datetime(2022, 7, 20))

        prom4 = Promotion(name="Promo4",product_id=4,type=PromotionType.PERCENTAGE,value=50,active=True,
        start_date = datetime(2022, 8, 10), expiration_date = datetime(2022, 8, 20))

        prom5 = Promotion(name="Promo5",product_id=5,type=PromotionType.PERCENTAGE,value=60,active=True,
        start_date = datetime(2022, 9, 10), expiration_date = datetime(2022, 9, 20))

        prom1.create()
        prom2.create()
        prom3.create()
        prom4.create()
        prom5.create()
        self.assertEqual(len(Promotion.all()),5)

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


        search5 = Promotion.find_by_start_date(prom4.start_date)
        self.assertIsNot(search5, None)
        self.assertEqual(search5[0].name, prom4.name)
        self.assertEqual(search5[0].start_date, prom4.start_date)

        search6 = Promotion.find_by_expiration_date(prom5.expiration_date)
        self.assertIsNot(search6, None)
        self.assertEqual(search6[0].name, prom5.name)
        self.assertEqual(search6[0].start_date, prom5.expiration_date)
'''
 def test_find_by_availability(self):
        """Find promotions by Availability"""
        current_date = datetime.now()
        Promotion(
            name="Macbook", 
            category=TypeOfPromo.Discount, 
            product_id=11111, amount=10, 
            description="Gread Deal", 
            from_date=current_date - timedelta(days=1), 
            to_date=current_date + timedelta(days=5)
            ).create()
        Promotion(
            product_name="iwatch", 
            category=TypeOfPromo.BOGOF, 
            product_id=11112, amount=20, 
            description="Gread Deal", 
            from_date=datetime(2021, 10, 7), 
            to_date=datetime(2021, 10, 13)
            ).create()
        Promotion(
            product_name="iphone", 
            category=TypeOfPromo.BOGOF, 
            product_id=11113, amount=30, 
            description="Gread Deal", 
            from_date=current_date + timedelta(days=1), 
            to_date=current_date + timedelta(days=7)
            ).create() 
        promotions = Promotion.find_by_availability(True)
        promotion_list = [promotion for promotion in promotions]
        self.assertEqual(len(promotion_list), 1)
        self.assertEqual(promotions[0].category, TypeOfPromo.Discount)
        self.assertEqual(promotions[0].product_name, "Macbook")
        self.assertEqual(promotions[0].product_id, 11111)
        self.assertEqual(promotions[0].amount, 10)
        self.assertEqual(promotions[0].description, "Gread Deal")
        self.assertEqual(promotions[0].from_date, current_date - timedelta(days=1)) 
        self.assertEqual(promotions[0].to_date, current_date + timedelta(days=5)) 
        promotions = Promotion.find_by_availability(False)
        promotion_list = [promotion for promotion in promotions]
        self.assertEqual(len(promotion_list), 2)
'''

