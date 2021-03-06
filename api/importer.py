import django
import os
import sys
project_path = os.path.join(os.path.dirname(__file__), '../')
sys.path.append(os.path.abspath(project_path))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "unisport_project.settings")
django.setup()

from api.serializers import ProductSerializer
from django.db import IntegrityError, transaction
from api.models import Product
import requests
import logging

logger = logging.getLogger('unisport')


def import_unisport_data():
    """Import unisport data from their api to the db."""

    unisport_api_uri = "https://www.unisport.dk/api/products/batch/"
    products_list_param = "?list=194742,193638,197237,188894,188896,189214,\
    194824,197250,194368,194477,194986,185253,197236,185117,187424,185866,\
    187743,194813,193639,187972,194923,194646,173445,193637,187744,200197,\
    193539,170478,194753,188893,181372,187477,193959,189188,197235,187812,\
    197242,168029,187425,194823"
    import_url = f"{unisport_api_uri}{products_list_param}"

    response = requests.get(
        url=import_url,
        timeout=5
    )

    def product_generator(products):
        for product in products:
            yield product
    with transaction.atomic():
        Product.objects.all().delete()
        for product in product_generator(response.json().get('products')):
            product_serializer = ProductSerializer(data=product)
            try:
                product_serializer.is_valid()
            except AssertionError as e:
                logger.info(product_serializer.errors)
            try:
                product_serializer.save()
                logger.info(f"product {product.get('id')} imported")
            except IntegrityError:
                logger.error(f"could not import product {product.get('id')}")
                continue
        return True


if __name__ == "__main__":
    import_unisport_data()
