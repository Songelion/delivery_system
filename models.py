class Customer:

    def __init__(self, id=None, name='', phone=None, address=None):
        self.id = id
        self.name = name
        self.phone = phone
        self.address = address

    @classmethod
    def from_row(cls, row):
        return cls(id=row[0], name=row[1], phone=row[2], address=row[3])

    def to_dict(self):
        return {'id': self.id, 'name': self.name, 'phone': self.phone, 'address': self.address}

    def __str__(self):
        return f'Customer(id={self.id}, name={self.name!r})'

    def __repr__(self):
        return self.__str__()

class OrderItem:

    def __init__(self, id=None, order_id=None, product_name='', quantity=0, price=0.0):
        self.id = id
        self.order_id = order_id
        self.product_name = product_name
        self.quantity = quantity
        self.price = price

    @property
    def total(self):
        return self.quantity * self.price

    @classmethod
    def from_row(cls, row):
        return cls(id=row[0], order_id=row[1], product_name=row[2], quantity=row[3], price=row[4])

    def to_dict(self):
        return {'id': self.id, 'order_id': self.order_id, 'product_name': self.product_name, 'quantity': self.quantity, 'price': self.price}

    def __str__(self):
        return f'OrderItem({self.product_name!r}, {self.quantity} x {self.price})'

    def __repr__(self):
        return self.__str__()

class Order:
    STATUSES = ('новый', 'в доставке', 'выполнен', 'отменён')

    def __init__(self, id=None, customer_id=None, order_date='', status='новый', total=0.0, items=None):
        self.id = id
        self.customer_id = customer_id
        self.order_date = order_date
        self.status = status
        self.total = total
        self.items = items if items is not None else []

    @classmethod
    def from_row(cls, row):
        return cls(id=row[0], customer_id=row[1], order_date=row[2], status=row[3], total=row[4])

    def to_dict(self):
        return {'id': self.id, 'customer_id': self.customer_id, 'order_date': self.order_date, 'status': self.status, 'total': self.total, 'items': [item.to_dict() for item in self.items]}

    def __str__(self):
        return f'Order(id={self.id}, status={self.status!r}, total={self.total})'

    def __repr__(self):
        return self.__str__()
