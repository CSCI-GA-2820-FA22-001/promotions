
"""
Test Factory to make fake objects for testing
"""

import factory
from service.models import Promotion
import random

class PromotionFactory(factory.Factory):
    """Creates fake Accounts"""

    # pylint: disable=too-few-public-methods
    class Meta:
        model = Promotion

    id = factory.Sequence(lambda n: n)

    name = factory.Sequence(lambda n: 'Promotion{}'.format(n))

    product = random.choice(["milk","eggs","cheese","fruit","frozen foods","water",
    "alcohol","yogurt","steak","bacon","all"])

    type = random.choice(["BOGO","Flat","Percentage"])

    if type == "BOGO":
        value = 0
    else:
        value = random.choice(["5","10","15","20","25", "30"])
    
    active = False
