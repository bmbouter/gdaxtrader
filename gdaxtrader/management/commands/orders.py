from django.core.management.base import BaseCommand

from gdaxtrader.models import Fund


def main():
    for fund in Fund.objects.all():
        if len(fund.buy_orders.filter(filled=False)) == 0 and len(fund.sell_orders.filter(filled=False)) == 0:
            print('\n%s:\nNo Open Orders' % fund)
            continue
        print('\n\n\n\n%s:\n' % fund)
        for buy_order in fund.buy_orders.filter(filled=False):
            print(buy_order)
        for sell_order in fund.sell_orders.filter(filled=False):
            print(sell_order)


class Command(BaseCommand):
    help = 'Prints orders from current database. By default only unfilled orders are printed.'

    def handle(self, *args, **options):
        main()
