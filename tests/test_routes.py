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

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/testdb"
)

######################################################################
#  T E S T   C A S E S
######################################################################
class TestYourResourceServer(unittest.TestCase):
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
        db.session.query(Promotion).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """ This runs after each test """
        db.session.remove()

    ######################################################################
    #  TEST CASES
    ######################################################################

    def test_index(self):
        """ It should call the home page """
        resp = self.app.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)



'''

 ######################################################################
    #  H E L P E R   M E T H O D S
    ######################################################################

    def _create_accounts(self, count):
        """Factory method to create accounts in bulk"""
        accounts = []
        for _ in range(count):
            account = AccountFactory()
            resp = self.client.post(BASE_URL, json=account.serialize())
            self.assertEqual(
                resp.status_code,
                status.HTTP_201_CREATED,
                "Could not create test Account",
            )
            new_account = resp.get_json()
            account.id = new_account["id"]
            accounts.append(account)
        return accounts

 ######################################################################
    # SAMPLE   T E S T   C A S E S
    ######################################################################

    def test_get_account_list(self):
        """It should Get a list of Accounts"""
        self._create_accounts(5)
        resp = self.client.get(BASE_URL)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 5)

    def test_get_account_by_name(self):
        """It should Get an Account by Name"""
        accounts = self._create_accounts(3)
        resp = self.client.get(BASE_URL, query_string=f"name={accounts[1].name}")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data[0]["name"], accounts[1].name)

    def test_get_account(self):
        """It should Read a single Account"""
        # get the id of an account
        account = self._create_accounts(1)[0]
        resp = self.client.get(
            f"{BASE_URL}/{account.id}", content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data["name"], account.name)

    def test_get_account_not_found(self):
        """It should not Read an Account that is not found"""
        resp = self.client.get(f"{BASE_URL}/0")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_account(self):
        """It should Create a new Account"""
        account = AccountFactory()
        resp = self.client.post(
            BASE_URL, json=account.serialize(), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # Make sure location header is set
        location = resp.headers.get("Location", None)
        self.assertIsNotNone(location)

        # Check the data is correct
        new_account = resp.get_json()
        self.assertEqual(new_account["name"], account.name, "Names does not match")
        self.assertEqual(
            new_account["addresses"], account.addresses, "Address does not match"
        )
        self.assertEqual(new_account["email"], account.email, "Email does not match")
        self.assertEqual(
            new_account["phone_number"], account.phone_number, "Phone does not match"
        )
        self.assertEqual(
            new_account["date_joined"],
            str(account.date_joined),
            "Date Joined does not match",
        )

        # Check that the location header was correct by getting it
        resp = self.client.get(location, content_type="application/json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        new_account = resp.get_json()
        self.assertEqual(new_account["name"], account.name, "Names does not match")
        self.assertEqual(
            new_account["addresses"], account.addresses, "Address does not match"
        )
        self.assertEqual(new_account["email"], account.email, "Email does not match")
        self.assertEqual(
            new_account["phone_number"], account.phone_number, "Phone does not match"
        )
        self.assertEqual(
            new_account["date_joined"],
            str(account.date_joined),
            "Date Joined does not match",
        )

    def test_update_account(self):
        """It should Update an existing Account"""
        # create an Account to update
        test_account = AccountFactory()
        resp = self.client.post(BASE_URL, json=test_account.serialize())
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # update the pet
        new_account = resp.get_json()
        new_account["name"] = "Happy-Happy Joy-Joy"
        new_account_id = new_account["id"]
        resp = self.client.put(f"{BASE_URL}/{new_account_id}", json=new_account)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        updated_account = resp.get_json()
        self.assertEqual(updated_account["name"], "Happy-Happy Joy-Joy")

    def test_delete_account(self):
        """It should Delete an Account"""
        # get the id of an account
        account = self._create_accounts(1)[0]
        resp = self.client.delete(f"{BASE_URL}/{account.id}")
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    def test_bad_request(self):
        """It should not Create when sending the wrong data"""
        resp = self.client.post(BASE_URL, json={"name": "not enough data"})
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unsupported_media_type(self):
        """It should not Create when sending wrong media type"""
        account = AccountFactory()
        resp = self.client.post(
            BASE_URL, json=account.serialize(), content_type="test/html"
        )
        self.assertEqual(resp.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_method_not_allowed(self):
        """It should not allow an illegal method call"""
        resp = self.client.put(BASE_URL, json={"not": "today"})
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
'''