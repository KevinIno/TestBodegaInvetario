from django.db import models
from django.forms import ValidationError
from inventory.models import Product

class Buyer(models.Model):
    name = models.CharField(max_length=200, verbose_name="Nombre", unique=True)
    address = models.CharField(max_length=500, verbose_name="Dirección")
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def clean(self):
        if Buyer.objects.filter(name=self.name).exclude(id=self.id).exists():
            raise ValidationError(f"El comprador '{self.name}' ya existe.")



class Supplier(models.Model):
    name = models.CharField(max_length=200, verbose_name="Nombre", unique=True)
    address = models.CharField(max_length=500, verbose_name="Dirección")
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def clean(self):
        if Supplier.objects.filter(name=self.name).exclude(id=self.id).exists():
            raise ValidationError(f"El proveedor '{self.name}' ya existe.")


class Order(models.Model):
    INPUT = 'I'
    OUTPUT = 'O'
    TYPE_CHOICES = [
        (INPUT, 'In'),
        (OUTPUT, 'Out')
    ]
    type = models.CharField(max_length=1, choices=TYPE_CHOICES)
    date = models.DateField()
    supplier = models.ForeignKey(Supplier, on_delete=models.DO_NOTHING, null=True, blank=True)
    buyer = models.ForeignKey(Buyer, on_delete=models.DO_NOTHING, null=True, blank=True)
    observation = models.CharField(max_length=300)
    user = models.IntegerField(null=True, blank=True)

    def clean(self):
        if not self.buyer:
            raise ValidationError("El cliente es obligatorio.")
        if not self.supplier and self.type == self.INPUT:
            raise ValidationError("El proveedor es obligatorio para pedidos de entrada.")
        if not self.orderdetail_set.exists():
            raise ValidationError("Debe agregar al menos un producto al pedido.")

    @property
    def total(self):
        return sum(round(detail.quantity * detail.price, 2) for detail in self.orderdetail_set.all())


class OrderDetail(models.Model):
    order = models.ForeignKey(Order, on_delete=models.DO_NOTHING)
    product = models.ForeignKey(Product, on_delete=models.DO_NOTHING)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    price = models.DecimalField(max_digits=10, decimal_places=2)

