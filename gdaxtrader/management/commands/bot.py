import datetime
from decimal import Decimal, ROUND_DOWN
import time

from django.core.management.base import BaseCommand

from mint.common import get_auth_client, raise_exception_if_error
from mint.models import BuyOrder, Fund, SellOrder


spread = Decimal('0.02')
product = 'ETH-USD'
cancel_time_seconds = 60


def main():
    auth_client = get_auth_client()
    accounts = auth_client.get_accounts()
    accounts_by_currency = {}

    for account in accounts:
        accounts_by_currency[account['currency']] = account

    fund_name = 'Market Maker Test'
    fund = Fund.objects.get(name=fund_name)

    while True:
        ETH_details = auth_client.get_account(accounts_by_currency['ETH']['id'])
        print ('USD = %s  ETH = %s' % (fund.available, ETH_details['available']))

        # Update existing orders
        for buy_order in fund.buy_orders.filter(filled=False):
            response = auth_client.get_order(str(buy_order.id))
            if 'done_reason' in response and response['done_reason'] == 'filled':
                output_str = 'updating buy order %s as filled; removing %s from the "%s" fund'
                print(output_str % (buy_order.id, response['executed_value'], fund.name))
                buy_order.filled = True
                buy_order.save()
                fund.usd_balance -= Decimal(response['executed_value'])
                fund.save()

        # Update existing sell orders
        for sell_order in fund.sell_orders.filter(filled=False):
            response = auth_client.get_order(str(sell_order.id))
            if 'done_reason' in response and response['done_reason'] == 'filled':
                output_str = 'updating sell order %s as filled; adding %s to the "%s" fund'
                print(output_str % (sell_order.id, response['executed_value'], fund.name))
                sell_order.filled = True
                sell_order.save()
                fund.usd_balance += Decimal(response['executed_value'])
                fund.save()

        # Check the prices
        current_book = auth_client.get_product_order_book(product)

        for buy_order in fund.buy_orders.filter(filled=True, sell=None):
            # place a sell order
            current_sell_no_fee = Decimal(current_book['asks'][0][0]) + spread
            sell_price_from_buy_price = Decimal(buy_order.price) + spread
            sell_price = max(current_sell_no_fee, sell_price_from_buy_price)
            price_str = str(sell_price.quantize(Decimal('.01'), rounding=ROUND_DOWN))
            if Decimal(ETH_details['available']) > Decimal('0.001'):
                print('placing sell order')
                response = auth_client.sell(price=price_str, size=ETH_details['available'], product_id=product)
                raise_exception_if_error(response)
                sell_order = SellOrder(id=response['id'], price=response['price'],
                                       size=response['size'], product=response['product_id'],
                                       created_at=response['created_at'], fund=fund).save()
                buy_order.sell = sell_order
                buy_order.save()

        if len(fund.buy_orders.filter(filled=False)) == 0:
            # place a buy order
            buy_price = Decimal(current_book['bids'][0][0]) - Decimal('0.01')
            size = fund.available / buy_price
            if size > Decimal('0.001'):
                print('placing_buy_order')
                size_str = str(size.quantize(Decimal('.00000001'), rounding=ROUND_DOWN))
                price_str = str(buy_price.quantize(Decimal('.01'), rounding=ROUND_DOWN))
                response = auth_client.buy(price=price_str, size=size_str, product_id=product)
                raise_exception_if_error(response)
                BuyOrder(id=response['id'], price=response['price'], size=response['size'],
                         product=response['product_id'], created_at=response['created_at'],
                         fund=fund).save()

        for order in fund.buy_orders.filter(filled=False):
            # check to cancel one of the current buy orders
            order_age = datetime.datetime.now(datetime.timezone.utc) - order.created_at
            if order_age > datetime.timedelta(seconds=cancel_time_seconds):
                response = auth_client.cancel_order(str(order.id))
                raise_exception_if_error(response)
                order.delete()

        time.sleep(5)


class Command(BaseCommand):
    help = 'Runs the bot trader'

    def handle(self, *args, **options):
        main()
