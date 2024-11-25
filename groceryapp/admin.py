# groceryapp/admin.py
from django.contrib import admin
from .models import Product, Cart, Order,  CartProduct, Customer,Admin,Role,Address, OTP

# Register the Product model
admin.site.register(Product)

# Register the Cart model
admin.site.register(Cart)

# Register the Order model
admin.site.register(Order)


admin.site.register(CartProduct)

admin.site.register(Customer)

admin.site.register(Admin)

admin.site.register(Role)

admin.site.register(Address)

admin.site.register(OTP)
