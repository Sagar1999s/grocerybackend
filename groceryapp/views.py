from django.shortcuts import render

# Create your views here.
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Product
from .serializers import ProductSerializer


@api_view(["POST"])
def create_product(request):
    print(request.data)  # Prints the QueryDict with the incoming form data and file.

    """
    Create a new product.
    """
    if request.method == "POST":
        # Extracting data from QueryDict and combining it with files
        data = request.data.dict()  # Converts QueryDict to a regular dictionary
        files = request.FILES  # Handles file uploads

        # Combine the data and files for the serializer
        serializer = ProductSerializer(data={**data, **files})

        # Validate the data
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        # Return validation errors if any
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def get_products(request):
    # Fetch all products from the database
    products = Product.objects.all()

    # Serialize the data
    serializer = ProductSerializer(products, many=True)

    # Return the serialized data as a response
    return Response(serializer.data)


from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Product, Cart, CartProduct


@api_view(["POST"])
def add_to_cart(request):
    # Extract product_id and quantity from the request data
    product_id = request.data.get("product_id")
    quantity = int(
        request.data.get("quantity", 1)
    )  # Default to 1 if quantity not provided

    if not product_id:
        return Response(
            {"error": "product_id is required"}, status=status.HTTP_400_BAD_REQUEST
        )

    try:
        # Find the product using the product_id
        product = Product.objects.get(id=product_id)

        # Retrieve or create the cart (you can replace this with logic to handle user-specific carts)
        cart, created = Cart.objects.get_or_create(id=1)  # Assuming cart ID = 1 for now

        # Check if the product already exists in the cart
        cart_product, created = CartProduct.objects.get_or_create(
            cart=cart, product=product
        )

        if not created:
            # If the product already exists, update the quantity
            cart_product.quantity += quantity
            cart_product.save()
            message = f"{quantity} more of {product.name} added to cart."
        else:
            # If it's a new product in the cart, set the quantity
            cart_product.quantity = quantity
            cart_product.save()
            message = f"{product.name} added to cart with quantity {quantity}."

        return Response({"message": message}, status=status.HTTP_200_OK)

    except Product.DoesNotExist:
        return Response(
            {"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND
        )


from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import CartProduct
from .serializers import CartProductSerializer


@api_view(["GET"])
def get_cart_products(request):
    """
    Get all CartProducts.
    """
    try:
        cart_products = CartProduct.objects.all()  # Fetch all CartProduct instances
        serializer = CartProductSerializer(
            cart_products, many=True
        )  # Serialize the data
        return Response(
            serializer.data, status=status.HTTP_200_OK
        )  # Return the serialized data
    except CartProduct.DoesNotExist:
        return Response(
            {"error": "CartProducts not found"}, status=status.HTTP_404_NOT_FOUND
        )


from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth.models import User
from .models import Customer, Role
from rest_framework import status
from django.db import transaction


@api_view(["POST"])
def create_customer(request):
    try:
        # Extract data from request
        name = request.data.get("name")
        email = request.data.get("email")
        phone = request.data.get("phone")
        password = request.data.get("password")

        # Validate required fields
        if not all([name, email, phone, password]):
            return Response(
                {"error": "All fields are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check if user already exists
        if User.objects.filter(username=email).exists():
            return Response(
                {"error": "A user with this email already exists"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Ensure the 'customer' role exists
        try:
            customer_role = Role.objects.get(name="customer")
        except Role.DoesNotExist:
            return Response(
                {"error": "Customer role does not exist. Please create it first."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Use a transaction to ensure atomicity
        with transaction.atomic():
            # Create the User object
            user = User.objects.create_user(username=email, password=password)
            user.save()

            # Create the Customer object linked to the User
            customer = Customer.objects.create(
                name=name,
                email=email,
                phone=phone,
                password=password,
                user=user,
                role=customer_role,  # Assign the customer role
            )
            customer.save()

        # Successful response
        return Response(
            {
                "message": "Customer created successfully",
                "customer": {
                    "id": customer.id,
                    "name": customer.name,
                    "email": customer.email,
                    "phone": customer.phone,
                    "role": customer.role.name,
                },
            },
            status=status.HTTP_201_CREATED,
        )

    except Exception as e:
        # Log the error for debugging
        print("Error:", str(e))
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Customer

from django.contrib.auth import authenticate, login
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Customer, Admin


@api_view(["POST"])
def login_user(request):
    print(request.data)
    try:
        # Extract email and password from request data
        email = request.data.get("email")
        password = request.data.get("password")
        otp = request.data.get("otp", "")

        if not email or not password:
            return Response(
                {"error": "Both email and password are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if password or not otp:
            user = authenticate(request, username=email, password=password)
        if otp or not password:
            user = authenticate(request, username=email, password=None)



        # Authenticate user
        if not user:
            return Response(
                {"error": "Invalid email or password."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # Log the user in to create a session
        login(request, user)

        # Check if the user is an Admin or Customer
        if hasattr(user, "admin"):
            # The user is an Admin
            admin = Admin.objects.get(user=user)
            response_data = {
                "message": "Admin login successful.",
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "name": admin.name,
                    "phone": admin.phone,
                    "role": admin.role.name,
                },
                "session_id": request.session.session_key,
            }
        elif hasattr(user, "customer"):
            # The user is a Customer
            customer = Customer.objects.get(user=user)
            response_data = {
                "message": "Customer login successful.",
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "name": customer.name,
                    "phone": customer.phone,
                },
                "session_id": request.session.session_key,
            }
        else:
            return Response(
                {"error": "User role not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(response_data, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Customer
from .serializers import (
    CustomerSerializer,
)  # Assuming you have a CustomerSerializer for the Customer model


@api_view(["GET"])
def get_all_customers(request):
    try:
        # Retrieve all customers
        customers = Customer.objects.all()

        # Serialize the customer data
        serializer = CustomerSerializer(customers, many=True)

        # Return the serialized data
        return Response(serializer.data, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Order, CartProduct, Customer, Product, Address
from .serializers import OrderSerializer


@api_view(["POST"])
def create_order(request):
    """
    Create a new order. The request body should include selectedCustomer,
    cartProducts (list of products with quantity), and address.
    """
    data = request.data
    print(data)  # This will print the data as per your example

    # Ensure the required fields are present in the request
    if not all(k in data for k in ["selectedCustomer", "cartProducts", "address"]):
        return Response(
            {"error": "Missing required fields."}, status=status.HTTP_400_BAD_REQUEST
        )

    # Extract customer ID and get the customer instance
    customer_id = data["selectedCustomer"]
    try:
        customer = Customer.objects.get(id=customer_id)
    except Customer.DoesNotExist:
        return Response(
            {"error": "Customer not found."}, status=status.HTTP_404_NOT_FOUND
        )

    # Extract and process address
    address_data = data["address"]
    address = Address.objects.create(
        home_address=address_data["homeAddress"],
        city=address_data["city"],
        state=address_data["state"],
        pincode=address_data["pincode"],
        customer=customer,  # Associate the address with the customer
    )

    # Process CartProduct data and calculate total amount
    total_amount = 0
    cart_products = []

    for item in data["cartProducts"]:
        # Extract product and quantity from cartProduct item
        product_data = item["product"]
        quantity = item["quantity"]

        # Get or create the Product instance
        try:
            product = Product.objects.get(id=product_data["id"])
        except Product.DoesNotExist:
            return Response(
                {"error": f"Product {product_data['name']} not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Create CartProduct and add to the cart_products list
        cart_product = CartProduct.objects.create(
            cart_id=item["cart"]["id"],  # Assuming cart ID is valid and exists
            product=product,
            quantity=quantity,
        )

        # Add to the total amount (price * quantity)
        total_amount += float(product.price) * quantity
        cart_products.append(cart_product)

    # Create the order
    order = Order.objects.create(
        customer=customer,
        address=address,
        total_amount=str(total_amount),  # Store total amount as string
        status="placed",  # Default status
    )

    # Add CartProducts to the order (Many-to-Many relationship)
    order.cartproduct.set(cart_products)

    # Return response with order details
    return Response(
        {
            "order_id": order.id,
            "status": order.status,
            "total_amount": order.total_amount,
            "cart_products": [
                {
                    "product": cart_product.product.name,
                    "quantity": cart_product.quantity,
                }
                for cart_product in cart_products
            ],
        },
        status=status.HTTP_201_CREATED,
    )


@api_view(["GET"])
def get_orders(request):
    """
    Retrieve all orders
    """
    try:
        orders = Order.objects.all()
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Product


@api_view(["DELETE"])
def delete_product(request, product_id):
    # Try to get the product by ID, if not found return 404
    product = get_object_or_404(Product, id=product_id)

    # Delete the product
    product.delete()

    # Return a success message in JSON format
    return JsonResponse({"message": "Product deleted successfully."}, status=204)


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Product
import json


@api_view(["PUT"])
def edit_product(request, product_id):
    if request.method == "PUT":
        try:
            # Get the product by its ID
            product = Product.objects.get(id=product_id)

            # Parse the JSON data from the request body
            data = json.loads(request.body)

            # Update product fields
            if "name" in data:
                product.name = data["name"]
            if "price" in data:
                product.price = data["price"]
            if "seller_name" in data:
                product.seller_name = data["seller_name"]

            # Save the updated product
            product.save()

            # Return success response
            return JsonResponse(
                {
                    "message": "Product updated successfully",
                    "product": {
                        "id": product.id,
                        "name": product.name,
                        "price": product.price,
                        "seller_name": product.seller_name,
                    },
                },
                status=200,
            )

        except Product.DoesNotExist:
            # Return error if product does not exist
            return JsonResponse({"message": "Product not found"}, status=404)

        except json.JSONDecodeError:
            # Handle invalid JSON body
            return JsonResponse({"message": "Invalid JSON format"}, status=400)

    return JsonResponse({"message": "Invalid request method"}, status=400)


from django.core.mail import send_mail
from django.http import JsonResponse
from .models import OTP
import random


@api_view(["POST"])
def send_otp(request):
    if request.method == "POST":
        email = request.data.get("email")

        # Generate a 6-digit OTP
        otp = str(random.randint(100000, 999999))

        # Save OTP to the database
        OTP.objects.create(email=email, otp=otp)

        # Send OTP via email
        send_mail(
            "Your OTP for Login",
            f"Your OTP is {otp}. It will expire in 5 minutes.",
            "your_email@example.com",
            [email],
            fail_silently=False,
        )

        return JsonResponse({"message": "OTP sent successfully!"}, status=200)

    return JsonResponse({"error": "Invalid request!"}, status=400)





from django.contrib.auth import login
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.middleware.csrf import get_token
from rest_framework.decorators import api_view
from .models import OTP

@api_view(["POST"])
def verify_otp(request):
    if request.method == "POST":
        email = request.data.get("email")
        otp = request.data.get("otp")

        # Ensure both email and OTP are provided
        if not email or not otp:
            return JsonResponse({"error": "Email and OTP are required!"}, status=400)

        # Check if OTP exists and is valid
        otp_instance = OTP.objects.filter(email=email, otp=otp, is_used=False).first()

        if otp_instance and otp_instance.is_valid():
            # Mark OTP as used
            otp_instance.is_used = True
            otp_instance.save()

            # Check if the user exists for the email
            user = User.objects.filter(email=email).first()

            if user:
                # Directly log the user in
                login(request, user)

                # Get CSRF token and session ID
                csrf_token = get_token(request)
                session_id = request.session.session_key

                # Send response with user data, CSRF token, and session ID
                user_data = {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "is_staff": user.is_staff,
                    "is_active": user.is_active,
                }
                response = {
                    "message": "Login successful!",
                    "user": user_data,
                    "csrf_token": csrf_token,
                    "session_id": session_id,
                }
                return JsonResponse(response, status=200)
            else:
                return JsonResponse(
                    {"error": "No user associated with this email!"}, status=404
                )
        else:
            return JsonResponse({"error": "Invalid or expired OTP!"}, status=400)

    # Return error for invalid HTTP methods
    return JsonResponse({"error": "Invalid request method!"}, status=405)
