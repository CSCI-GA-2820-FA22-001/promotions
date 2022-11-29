
"""
Test Factory to make fake objects for testing
"""

import factory
from service.models import Promotion, PromotionType
from factory.fuzzy import FuzzyChoice
import random
from datetime import datetime, timedelta

class PromotionFactory(factory.Factory):
    """Creates fake Accounts"""

    # pylint: disable=too-few-public-methods
    class Meta:
        model = Promotion

        """
        "id": self.id, 
        "name": self.name,
        "product_id": self.product_id,
        "type": self.type,
        "value": self.value,
        "active": self.active,
        "start": self.start_date,
        "end": self.expiration_date
        """

    id = factory.Sequence(lambda n: n)

    name = factory.Sequence(lambda n: 'Promotion{}'.format(n))

    product_id = random.randint(0, 100000)

    type = random.choice(["BOGO","Flat","Percentage"])
    type = FuzzyChoice(choices=[PromotionType.BOGO, PromotionType.PERCENTAGE, PromotionType.FIXED])
    if type == "BOGO":
        value = 0
    else:
        value = random.choice([5,10,15,20,25, 30])
    
    active = False
    start_date = factory.Sequence(lambda n: datetime.now() + timedelta(days = n - 20))
    expiration_date = factory.Sequence(lambda n: datetime.now() + timedelta(days = n - 10))
