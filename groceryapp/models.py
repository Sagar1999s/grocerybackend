from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User



class Role(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Admin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="admin")
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    role = models.ForeignKey(Role, on_delete=models.CASCADE )

    def __str__(self):
        return self.name


class Customer(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, unique=True)
    password = models.CharField(max_length=255)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="customer")
    role = models.ForeignKey(Role, on_delete=models.CASCADE )
    def __str__(self):
        return self.name




class Product(models.Model):
    name = models.CharField(max_length=255)
    price = models.CharField(max_length=255)
    seller_name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Cart(models.Model):
    products = models.ManyToManyField(
        Product
    )  # Many-to-many relation with Product model
    

    def __str__(self):
        return f"Cart ID: {self.id}"




class CartProduct(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
  

    def __str__(self):
        return f"{self.product.name} x {self.quantity} in Cart {self.cart.id}"


class Address(models.Model):
    home_address = models.CharField(max_length=255)
    pincode = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)

    
    def __str__(self):
        return f"{self.home_address} "


class Order(models.Model):
    STATUS_CHOICES = [
        ("placed", "Placed"),
        ("cancelled", "Cancelled"),
        ("rejected", "Rejected"),
    ]

    cartproduct = models.ManyToManyField(
        CartProduct
    )  # Many-to-many relation with Cart
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="placed")
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    total_amount= models.CharField(max_length=255)
    address = models.ForeignKey(Address, on_delete=models.CASCADE)

    def __str__(self):
        return f"Order ID: {self.total_amount} - Status: {self.status}"
