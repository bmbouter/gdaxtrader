import argparse
from decimal import Decimal, ROUND_DOWN

from django.core.management.base import BaseCommand

from gdaxtrader.common import get_auth_client, raise_exception_if_error
from gdaxtrader.models import Fund, BuyOrder


def main(fund_name, allow_fee, coin, buy_price, amount):
    fund = Fund.objects.get(name=fund_name)
    auth_client = get_auth_client()
    product = '%s-USD' % coin
    current_book = auth_client.get_product_order_book(product)

    # Check that no fees will be incurred unless they are allowed
    no_fee_price = Decimal(current_book['bids'][0][0]) - Decimal('0.01')
    if not allow_fee and no_fee_price < buy_price:
        msg = "This buy will likely incur a fee. Allow fees with the --allow-fee option."
        raise argparse.ArgumentTypeError(msg)

    size = amount / buy_price
    size_rounded = size.quantize(Decimal('.00000001'), rounding=ROUND_DOWN)
    price_rounded = buy_price.quantize(Decimal('.01'), rounding=ROUND_DOWN)

    order = BuyOrder(price=price_rounded, size=size_rounded, product=product, fund=fund)
    fund.validate_order(order)
    response = auth_client.buy(price=str(price_rounded), size=str(size_rounded), product_id=product)
    raise_exception_if_error(response)
    BuyOrder(id=response['id'], price=response['price'], size=response['size'],
             product=response['product_id'], created_at=response['created_at'],
             fund=fund).save()
    print('Order "%s" placed to buy $%s worth of %s when %s reaches $%s / %s' %
          (id, size_rounded, coin, coin, price_rounded, coin))



class Command(BaseCommand):
    help = 'Places a buy order. By default prevents buy orders that are market takers.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--coin',
            choices=['ETH', 'BTC', 'LTC', 'BCH'],
            required=True,
            help='Specify the coin type to buy.',
        )
        parser.add_argument(
            '--buy-price',
            dest='buy_price',
            type=Decimal,
            required=True,
            help='Specify the price to buy at in USD as a string, e.g. --price "247.32"',
        )
        parser.add_argument(
            '--amount',
            type=Decimal,
            required=True,
            help='Specify the amount of USD to spend. e.g. --price "263.64"',
        )
        parser.add_argument(
            '--fund',
            required='true',
            dest='fund_name',
            help='Specify the fund to use. Defaults to "manual-trader".',
        )
        parser.add_argument(
            '--allow-fee',
            default=False,
            dest='allow_fee',
            help='Specify if your trade allows fees. Defaults to False.',
        )

    def handle(self, *args, fund_name, allow_fee, coin, buy_price, amount, **options):
        main(fund_name, allow_fee, coin, buy_price, amount)
