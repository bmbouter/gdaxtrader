from django.db import models


class AbstractOrder(models.Model):
    id = models.UUIDField(primary_key=True, editable=False)
    price = models.DecimalField(max_digits=20, decimal_places=12)
    size = models.DecimalField(max_digits=20, decimal_places=12)
    product = models.CharField(max_length=7)
    filled = models.BooleanField(default=False)
    created_at = models.DateTimeField()

    class Meta:
        abstract = True


class SellOrder(AbstractOrder):
    fund = models.ForeignKey('Fund', related_name='sell_orders', on_delete=models.PROTECT)

    def __str__(self):
        return 'SellOrder(size=%s, price=%s, id="%s")' % (self.size, self.price, self.id)


class BuyOrder(AbstractOrder):
    sell = models.ForeignKey('SellOrder', related_name='buy', on_delete=models.SET_NULL, null=True)
    fund = models.ForeignKey('Fund', related_name='buy_orders', on_delete=models.PROTECT)

    def __str__(self):
        return 'BuyOrder(size=%s, price=%s, id="%s")' % (self.size, self.price, self.id)


class Fund(models.Model):
    name = models.CharField(max_length=32)
    usd_balance = models.DecimalField(max_digits=20, decimal_places=12)

    def __str__(self):
        return 'Fund "%s": USD=%s' % (self.name, self.usd_balance)

    @property
    def eth_balance(self):
        raise NotImplemented()

    @property
    def available(self):
        outstanding_buy_order_balance = 0
        for buy_order in self.buy_orders.filter(filled=False):
            outstanding_buy_order_balance += (buy_order.price * buy_order.size)
        return self.usd_balance - outstanding_buy_order_balance

    def validate_order(self, order):
        if isinstance(order, BuyOrder):
            if self.usd_balance < (order.price * order.size):
                msg = 'Current wallet has %s, but order amount is %s'
                raise ValueError(msg % (self.usd_balance, order.price * order.size))
        elif isinstance(order, SellOrder):
            return
            raise NotImplemented('validating sell order is not implemented')
