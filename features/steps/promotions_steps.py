######################################################################
# Copyright 2016, 2021 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
######################################################################

"""
Promotion Steps

Steps file for Promotion.feature

For information on Waiting until elements are present in the HTML see:
    https://selenium-python.readthedocs.io/waits.html
"""
import requests
from behave import given
from compare import expect


@given('the following promotions')
def step_impl(context):
    """ Delete all Promos and load new ones """
    # List all of the promos and delete them one by one
    rest_endpoint = f"{context.BASE_URL}/promotions"
    context.resp = requests.get(rest_endpoint)
    expect(context.resp.status_code).to_equal(200)
    for promotion in context.resp.json():
        context.resp = requests.delete(f"{rest_endpoint}/{promotion['id']}")
        expect(context.resp.status_code).to_equal(204)

    # load the database with new promos
    for row in context.table:
        payload = {
            "id": int(row['id']),
            "name": row['name'],
            "product_id": int(row['product_id']),
            "type": row['type'],
            "value": row['value'],
            "start_date": row['start_date'],
            "expiration_date": row['expiration_date'],
            "active": row['active'] in ['True', 'true', '1']
        }
        context.resp = requests.post(rest_endpoint, json=payload)
        expect(context.resp.status_code).to_equal(201)
