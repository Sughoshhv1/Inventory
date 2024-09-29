from typing import Any
from django.shortcuts import render,redirect #type:ignore
from django.http import HttpResponse #type:ignore
from rest_framework.views import APIView #type:ignore
from django.http import JsonResponse #type:ignore
from customer.models import *
from django.views.generic import TemplateView
from .models import Order, Usertype, Product, Customer
from .models import Order
from .models import Customer, Product, Order
from .models import InventoryItem, Usertype
from decimal import Decimal, InvalidOperation


# Create your views here.
def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")

def landing(request):
    request.session["user_data"] = ""
    return render(request, 'customer/home.html')

def login(request):
    return render(request, 'customer/login.html')

def signup(request):
    return render(request, 'customer/signup1.html')

def admin1(request):
    return render(request, 'customer/admin1.html')

# class login_check(APIView):
#     def post(self,request):
#         username = request.POST["username"]
#         password = request.POST["password"]
#         if username =='test':
#             return JsonResponse({"status":"pass"})
#         else:
#             return JsonResponse({"status":"fail"})
class login_check(APIView):
    def post(self, request):
        name = request.POST['name']
        password = request.POST['password']
        ent = Usertype.objects.filter(user_name=name,user_pass=password).values()
        if(len(ent) > 0):
            request.session["user_data"] = ent[0]["user_name"]
            request.session['user_id'] = ent[0]['user_id']
            return JsonResponse({"status":"pass", "uid": ent[0]["user_id"], "role": ent[0]["user_typee"], "name": ent[0]["user_name"]})
        else:
            return JsonResponse({"status":"fail"})   

# class logout(APIView):
#     def post(self, request):
#         self.request.session["user_data"] = ""
#         return JsonResponse({"status":"pass"})

class logout(APIView):
    def get(self, request):
        # Clear the session data for the user
        request.session.flush()  # This clears all session data
        return redirect('landing')  # Redirect to the 'landing' page     

class create(APIView):
    def post(self, request):
        # Use request.data for JSON data
        username = request.data.get("username")
        password = request.data.get("password")
        email = request.data.get("email")
        phone = request.data.get("phone")
        usertype = request.data.get("usertype")

        # Create Usertype object
        usr = Usertype()
        usr.user_name = username
        usr.user_email = email
        usr.user_pass = password
        usr.user_typee = usertype
        usr.user_number = phone
        usr.save()


        # Create Customer object
        if usr.user_typee=='customer':
            cust = Customer.objects.create(
                cust_name=usr.user_name,
                cust_email=usr.user_email,  # corrected this line
                cust_number=usr.user_number,
                cust_pass=usr.user_pass,
                userid=usr
            )
        
        if usr.user_typee=='vendor':
            vend = Vendor.objects.create(
                vend_name=usr.user_name,
                vend_email=usr.user_email,  # corrected this line
                vend_number=usr.user_number,
                vend_pass=usr.user_pass,
                userid=usr
            )

        if usr.user_typee=='employee':
            emp = Employee.objects.create(
                emp_name=usr.user_name,
                emp_email=usr.user_email,  # corrected this line
                emp_number=usr.user_number,
                emp_pass=usr.user_pass,
                userid=usr
            )
        # Return success response
        return JsonResponse({"status": "pass"})



class create_product(APIView):
    def post(self,request):
        product_name = request.POST["product_name"]
        product_qt=request.POST["product_qt"]
        product_cat=request.POST["product_cat"]
        psr=Product()
        psr.name=product_name
        psr.quantiy=product_qt
        psr.category=product_cat
        psr.save()
        return JsonResponse({"status":"pass"})
    


class CreateOrder(APIView):
    def post(self, request):
        try:
            # Fetch data from the request
            customer_id = request.POST.get("customer_id")
            product_id = request.POST.get("product_id")
            order_created = request.POST.get("order_created")
            order_qt = request.POST.get("order_qt")


            # Debugging logs
            print(f"Customer ID: {customer_id}")
            print(f"Product ID: {product_id}")
            print(f"Order Created: {order_created}")
            print(f"Order Quantity: {order_qt}")

            # Validate the data
            if not customer_id or not product_id or not order_created or not order_qt:
                return JsonResponse({"status": "fail", "message": "All fields are required"})

            # Fetch the customer and product from the database
            try:
                customer = Customer.objects.get(cust_id=customer_id)
            except Customer.DoesNotExist:
                return JsonResponse({"status": "fail", "message": "Customer not found"})
            
            try:
                product = Product.objects.get(pro_id=product_id)
            except Product.DoesNotExist:
                return JsonResponse({"status": "fail", "message": "Product not found"})

            # Convert the order quantity to Decimal and validate
            try:
                order_qt = Decimal(order_qt)
            except InvalidOperation:
                return JsonResponse({"status": "fail", "message": "Invalid order quantity format"})

            # Check if there's enough stock for the product

            if product.quantiy == 0:
                return JsonResponse({"status": "fail", "message": "Out of stock"})

            if product.quantiy < order_qt:
                return JsonResponse({"status": "fail", "message": f"Only {product.quantiy} in stock, please adjust the order quantity"})

            # Create a new order
            order = Order(
                customerfk=customer,
                productfk=product,
                created_att=order_created,
                total_qt=order_qt,
            )
            order.save()

            # Update the product's quantity by reducing the ordered quantity
            product.quantiy -= order_qt
            product.save()
        
            return JsonResponse({"status": "pass", "message": "Order placed successfully."})

        except Exception as e:
            # Log the exception (optional) and return a generic error message
            print(f"An error occurred: {e}")
            return JsonResponse({"status": "fail", "message": "An unexpected error occurred"}, status=500)
         

class create_inventory(APIView):
    def post(self, request):
        vendor_id = request.data.get("vendor_id")
        product_id = request.data.get("product_id")
        quantity = request.data.get("quantity")
        date_added = request.data.get("date_added")

        # Validate the data
        if not vendor_id or not product_id or not quantity:
            return JsonResponse({"status": "fail", "message": "Vendor, Product, and Quantity are required"}, status=400)

        # Fetch the vendor and product from the database
        try:
            vendor = Vendor.objects.get(vend_id=vendor_id)
        except Vendor.DoesNotExist:
            return JsonResponse({"status": "fail", "message": "Vendor not found"}, status=400)

        try:
            product = Product.objects.get(pro_id=product_id)
        except Product.DoesNotExist:
            return JsonResponse({"status": "fail", "message": "Product not found"}, status=400)

        # Convert the quantity input to Decimal
        try:
            quantity = Decimal(quantity)
        except InvalidOperation:
            return JsonResponse({"status": "fail", "message": "Invalid quantity format"}, status=400)

        # Create a new inventory item
        inventory_item = InventoryItem(
            vendor=vendor,
            product=product,
            quantity=quantity,
            created_at=date_added
        )
        inventory_item.save()

        # Update the product's quantity by adding the new quantity from inventory
        product.quantiy = product.quantiy + quantity
        product.save()

        return JsonResponse({"status": "pass"})

    
class delete_user(APIView):
    def post(self, request):
        user_id = request.POST["user_id"]
        Usertype.objects.filter(user_id=user_id).delete()
        return JsonResponse({"status":"pass"})

class delete_inventory(APIView):
    def post(self, request):
        inventory_id = request.POST["item_id"]
        inv=InventoryItem.objects.get(inven_id=inventory_id)
        product1=inv.product
        product1.quantiy -= inv.quantity
        product1.save()
        InventoryItem.objects.filter(inven_id =inventory_id).delete()
        return JsonResponse({"status":"pass"})
    
class delete_product(APIView):
    def post(self, request):
        product_id = request.POST["product_id"]
        Product.objects.filter(pro_id=product_id).delete()
        return JsonResponse({"status":"pass"})

class delete_order(APIView):
    def post(self, request):
        order_id = request.POST["order_id"]
        try:
            order = Order.objects.get(order_id=order_id)
        except Order.DoesNotExist:
            return JsonResponse({"status": "fail", "message": "Order not found"}, status=400)

        # Access the associated product
        product = order.productfk

        # Restore the product quantity by adding back the order's quantity
        product.quantiy += order.total_qt
        product.save()

        # Delete the order
        Order.objects.filter(order_id=order_id).delete()
        return JsonResponse({"status":"pass"})

from django.views.generic import TemplateView

class userview(TemplateView):
    template_name = "customer/view_user.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_data = Usertype.objects.all()
        order_count=Order.objects.all().count()
        vendor_count=Usertype.objects.filter(user_typee ="vendor").count()
        cust_count = Usertype.objects.filter(user_typee="customer").count()
        employee_count = Usertype.objects.filter(user_typee="employee").count()
        product_count = Product.objects.all().count()
        current_user = self.request.session.get("user_data", None)        
        context.update({
            "userdata": user_data,
            "order_count":order_count,
            "vendor_count": vendor_count,
            "cust_count": cust_count,
            "employee_count": employee_count,
            "product_count": product_count,
            "currentuser" :current_user
        })
        return context

class vendor_user(TemplateView):
    template_name="customer/vendor.html"

    def get_context_data(self,**kwargs):
        context=super().get_context_data(**kwargs)
        user_data = Vendor.objects.all()
        order_count=Order.objects.all().count()
        vendor_count=Usertype.objects.filter(user_typee ="vendor").count()
        cust_count = Usertype.objects.filter(user_typee="customer").count()
        employee_count = Usertype.objects.filter(user_typee="employee").count()
        product_count = Product.objects.all().count()
        current_user = self.request.session.get("user_data", None)
                
        context.update({
            "userdata": user_data,
            "order_count":order_count,
            "vendor_count": vendor_count,
            "cust_count": cust_count,
            "employee_count": employee_count,
            "product_count": product_count,
            "currentuser" :current_user
        })
        return context


class customer_user(TemplateView):
    template_name = "customer/customer1.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Fetch user data for customers
        user_data = Customer.objects.all()

        # Count various entities
        order_count = Order.objects.count()
        vendor_count = Usertype.objects.filter(user_typee="vendor").count()
        cust_count = user_data.count()  # Count customers from user_data
        employee_count = Usertype.objects.filter(user_typee="employee").count()
        product_count = Product.objects.count()
        current_user = self.request.session.get("user_data", None)

        # Update context with all the gathered data
        context.update({
            "userdata": user_data,  # Updated to include customer IDs
            "order_count": order_count,
            "vendor_count": vendor_count,
            "cust_count": cust_count,
            "employee_count": employee_count,
            "product_count": product_count,
            "currentuser" :current_user
        })

        return context

class employee_user(TemplateView):
    template_name="customer/employee1.html"

    def get_context_data(self,**kwargs):
        context=super().get_context_data(**kwargs)
        user_data = Employee.objects.all()
        order_count=Order.objects.all().count()
        vendor_count=Usertype.objects.filter(user_typee ="vendor").count()
        cust_count = Usertype.objects.filter(user_typee="customer").count()
        employee_count = Usertype.objects.filter(user_typee="employee").count()
        product_count = Product.objects.all().count()
        current_user = self.request.session.get("user_data", None)
                
        context.update({
            "userdata": user_data,
            "order_count":order_count,
            "vendor_count": vendor_count,
            "cust_count": cust_count,
            "employee_count": employee_count,
            "product_count": product_count,
            "currentuser" :current_user
        })
        return context

class u_product(TemplateView):
    template_name="customer/product1.html"

    def get_context_data(self,**kwargs):
        context=super().get_context_data(**kwargs)
        user_data=Product.objects.all()
        order_count=Order.objects.all().count()
        vendor_count=Usertype.objects.filter(user_typee ="vendor").count()
        cust_count = Usertype.objects.filter(user_typee="customer").count()
        employee_count = Usertype.objects.filter(user_typee="employee").count()
        product_count = Product.objects.all().count()
        current_user = self.request.session.get("user_data", None)
        products = Product.objects.all()
        categorized_products = {
        'Fruits': products.filter(category='Fruits'),
        'Vegetables': products.filter(category='Vegetables'),
        'Essentials': products.filter(category='Essentials'),
        }
                     
        context.update({
            "userdata": user_data,
            "order_count":order_count,
            "vendor_count": vendor_count,
            "cust_count": cust_count,
            "employee_count": employee_count,
            "product_count": product_count,
            "currentuser" :current_user,
            'categorized_products': categorized_products
        })
        return context
    
class u_order(TemplateView):
    template_name = "customer/order.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Existing data fetching
        user_data = Order.objects.all()
        order_count = Order.objects.all().count()
        vendor_count = Usertype.objects.filter(user_typee="vendor").count()
        cust_count = Usertype.objects.filter(user_typee="customer").count()
        employee_count = Usertype.objects.filter(user_typee="employee").count()
        product_count = Product.objects.all().count()
        current_user = self.request.session.get("user_data", None)

        # Fetch customers and products for dropdowns
        customers = Customer.objects.all()
        products = Product.objects.all()
        order_data = Order.objects.all()

        # Update the context
        context.update({
            "userdata": user_data,
            "order_count": order_count,
            "vendor_count": vendor_count,
            "cust_count": cust_count,
            "employee_count": employee_count,
            "product_count": product_count,
            "customers": customers,  # Pass customer data for dropdown
            "products": products,  # Pass product data for dropdown
            "orders": order_data,
            "currentuser" :current_user
        })

        return context


class u_inventory(TemplateView):
    template_name = "customer/inventory.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Fetching inventory items
        user_data = InventoryItem.objects.all()  # All inventory items
        order_count = Order.objects.count()  # Total orders
        vendor_count = Usertype.objects.filter(user_typee="vendor").count()  # Total vendors
        cust_count = Usertype.objects.filter(user_typee="customer").count()  # Total customers
        employee_count = Usertype.objects.filter(user_typee="employee").count()  # Total employees
        product_count = Product.objects.count()  # Total products
        current_user = self.request.session.get("user_data", None)

        inventory_items = InventoryItem.objects.all()
        vendor = Vendor.objects.all()
        products = Product.objects.all()

        # Updating context
        context.update({
            "userdata": user_data,
            "order_count": order_count,
            "vendor_count": vendor_count,
            "cust_count": cust_count,
            "employee_count": employee_count,
            "product_count": product_count,
            "vendor": vendor,
            "products": products,
            'inventory_items': inventory_items,
            "currentuser" :current_user
        })

        return context

class edit_user(APIView):
    def post(self, request):
        uid = request.POST['id']
        fullname1 = request.POST['fullname']
        email1 = request.POST['email']
        password1 = request.POST['password']
        number1 = request.POST['number']
        ty = request.POST['type']
        userdata= Usertype.objects.filter(user_id=uid).update(
            user_name=fullname1,
            user_email=email1,
            user_number=number1,
            user_pass=password1,
            user_typee=ty)

        user = Usertype.objects.get(user_id=uid)
        if ty=='customer':
            Customer.objects.filter(userid=uid).update(
            cust_name=user.user_name,
            cust_email=user.user_email,
            cust_number= user.user_number,
            cust_pass=user.user_pass)

        if ty=='vendor':
            Vendor.objects.filter(userid=uid).update(
            vend_name=user.user_name,
            vend_email=user.user_email,
            vend_number= user.user_number,
            vend_pass=user.user_pass)

        if ty=='employee':
            Employee.objects.filter(userid=uid).update(
            emp_name=user.user_name,
            emp_email=user.user_email,
            emp_number= user.user_number,
            emp_pass=user.user_pass)

        return JsonResponse({"status":"pass"})  

class edit_inventory(APIView):
    def post(self, request):
        inv_id = request.POST.get('id')
        inv_total = request.POST.get('quantity')
        product_id = request.POST.get('product_id')
        i_date = request.POST.get('inv_date')
        i_vendor = request.POST.get('vendor_id')
        inv_total = Decimal(inv_total)  

        inventory_item = InventoryItem.objects.get(inven_id=inv_id)
        old_quantity = inventory_item.quantity

        product = Product.objects.get(pro_id=product_id) 

        InventoryItem.objects.filter(inven_id=inv_id).update(
                quantity=inv_total,
                product=product_id, # Assuming productfk is a ForeignKey
                created_at=i_date,
                vendor=i_vendor
            )
        
        # Calculate the difference and update the product's quantity accordingly
        quantity_difference = inv_total - old_quantity

        product.quantiy += quantity_difference
        product.save()

        return JsonResponse({"status": "success"})   
    
class edit_order(APIView):
    def post(self, request):
        order_id = request.POST.get('id')
        order_total = request.POST.get('ordertotal')
        product_id = request.POST.get('product_id')
        O_date = request.POST.get('ctdate')
        O_customer = request.POST.get('customer_id')
        order_total = Decimal(order_total)
        product = Product.objects.get(pro_id=product_id) 

        order_item = Order.objects.get(order_id=order_id)
        old_quantity = order_item.total_qt 

        quantity_difference = order_total - old_quantity 

        if product.quantiy < quantity_difference:
            return JsonResponse({"status": "out_of_stock", "message": f"Only {product.quantiy} in stock, please adjust the order quantity"})

        if product.quantiy == 0:
            return JsonResponse({"status": "out_of_stock", "message": "Out of stock"})

        # if product.quantiy < quantity_difference:
        #     return JsonResponse({"status": "fail", "message": f"Only {product.quantiy} in stock, please adjust the order quantity"})

        Order.objects.filter(order_id=order_id).update(
                total_qt=order_total,
                productfk_id=product_id, # Assuming productfk is a ForeignKey
                created_att=O_date,
                customerfk=O_customer
            )

        product.quantiy -= quantity_difference
        product.save()

        return JsonResponse({"status": "success"}) 

class edit_product(APIView):
    def post(self, request):
        uid = request.POST['id']
        pname = request.POST['pname']
        pqt=request.POST['pqt']
        userdata= Product.objects.filter(pro_id=uid).update(
            name=pname,
            quantiy=pqt
            )
        return JsonResponse({"status":"pass"})     

class login_check_ajax(APIView):
    def post(self, request):
        name = request.POST['name']
        password = request.POST['password']
        ent = Usertype.objects.filter(user_name=name,user_pass=password).values()
        if(len(ent) > 0):
            request.session["user_data"] = ent[0]["user_name"]
            request.session['user_id'] = ent[0]['user_id']
            return JsonResponse({"status":"pass", "uid": ent[0]["user_id"], "role": ent[0]["user_typee"], "name": ent[0]["user_name"]})
        else:
            return JsonResponse({"status":"fail"})
# from here customer page operations starts

class u1_order(TemplateView):
    template_name = "customer2/order.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Fetch the current user's ID from the session
        current_user_id = self.request.session.get("user_id")

        # Fetch orders only for the current user using the correct ForeignKey field names
        user_orders = Order.objects.filter(customerfk__userid__user_id=current_user_id)

        # Fetch other counts
        order_count = user_orders.count()
        vendor_count = Usertype.objects.filter(user_typee="vendor").count()
        cust_count = Usertype.objects.filter(user_typee="customer").count()
        employee_count = Usertype.objects.filter(user_typee="employee").count()
        product_count = Product.objects.all().count()

        # Fetch customers and products for dropdowns
        customers = Customer.objects.all()
        products = Product.objects.all()

        # Update the context
        context.update({
            "orders": user_orders,  # Pass only current user's orders
            "order_count": order_count,
            "vendor_count": vendor_count,
            "cust_count": cust_count,
            "employee_count": employee_count,
            "product_count": product_count,
            "customers": customers,
            "products": products,
            "currentuser": self.request.session.get("user_data"),
            "currentid": current_user_id,
        })

        return context

class CreateOrdercust(APIView):
    def post(self, request):
        try:
            # Fetch data from the request
            current_user_id = request.session.get("user_id")  # Get current logged-in user's ID from the session
            product_id = request.POST.get("product_id")
            order_created = request.POST.get("order_created")
            order_qt = request.POST.get("order_qt")

            # Debugging logs
            print(f"Current User ID: {current_user_id}")
            print(f"Product ID: {product_id}")
            print(f"Order Created: {order_created}")
            print(f"Order Quantity: {order_qt}")

            # Validate the data
            if not current_user_id or not product_id or not order_created or not order_qt:
                return JsonResponse({"status": "fail", "message": "All fields are required"})

            # Fetch the customer using the current user ID
            try:
                customer = Customer.objects.get(userid__user_id=current_user_id)
            except Customer.DoesNotExist:
                return JsonResponse({"status": "fail", "message": "Customer not found"})

            # Fetch the product from the database
            try:
                product = Product.objects.get(pro_id=product_id)
            except Product.DoesNotExist:
                return JsonResponse({"status": "fail", "message": "Product not found"})

            # Convert the order quantity to Decimal and validate
            try:
                order_qt = Decimal(order_qt)
            except InvalidOperation:
                return JsonResponse({"status": "fail", "message": "Invalid order quantity format"})

            # Check if there's enough stock for the product
            if product.quantiy == 0:
                return JsonResponse({"status": "fail", "message": "Out of stock"})

            if product.quantiy < order_qt:
                return JsonResponse({"status": "fail", "message": f"Only {product.quantiy} in stock, please adjust the order quantity"})

            # Create a new order
            order = Order(
                customerfk=customer,
                productfk=product,
                created_att=order_created,
                total_qt=order_qt,
            )
            order.save()

            # Update the product's quantity by reducing the ordered quantity
            product.quantiy -= order_qt
            product.save()
        
            return JsonResponse({"status": "pass", "message": "Order placed successfully."})

        except Exception as e:
            # Log the exception (optional) and return a generic error message
            print(f"An error occurred: {e}")
            return JsonResponse({"status": "fail", "message": "An unexpected error occurred"}, status=500)
        
class edit_ordercust(APIView):
    def post(self, request):
        order_id = request.POST.get('id')
        order_total = request.POST.get('ordertotal')
        product_id = request.POST.get('product_id')
        O_date = request.POST.get('ctdate')
        order_total = Decimal(order_total)
        product = Product.objects.get(pro_id=product_id) 

        order_item = Order.objects.get(order_id=order_id)
        old_quantity = order_item.total_qt 

        quantity_difference = order_total - old_quantity 

        if product.quantiy < quantity_difference:
            return JsonResponse({"status": "out_of_stock", "message": f"Only {product.quantiy} in stock, please adjust the order quantity"})

        if product.quantiy == 0:
            return JsonResponse({"status": "out_of_stock", "message": "Out of stock"})

        # if product.quantiy < quantity_difference:
        #     return JsonResponse({"status": "fail", "message": f"Only {product.quantiy} in stock, please adjust the order quantity"})

        Order.objects.filter(order_id=order_id).update(
                total_qt=order_total,
                productfk_id=product_id, # Assuming productfk is a ForeignKey
                created_att=O_date,
            )

        product.quantiy -= quantity_difference
        product.save()

        return JsonResponse({"status": "success"}) 
    
#profile page information

class customer_usercust(TemplateView):
    template_name = "customer2/profile.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Fetch the current user's ID from the session
        current_user_id = self.request.session.get("user_id")
        
        # Fetch the customer data for the logged-in user
        try:
            user_data = Customer.objects.get(userid__user_id=current_user_id)
        except Customer.DoesNotExist:
            user_data = None

        # Count various entities
        order_count = Order.objects.filter(customerfk=user_data).count() if user_data else 0
        vendor_count = Usertype.objects.filter(user_typee="vendor").count()
        cust_count = Customer.objects.count()
        employee_count = Usertype.objects.filter(user_typee="employee").count()
        product_count = Product.objects.count()

        # Update context with the data
        context.update({
            "userdata": user_data,
            "order_count": order_count,
            "vendor_count": vendor_count,
            "cust_count": cust_count,
            "employee_count": employee_count,
            "product_count": product_count,
            "currentuser": self.request.session.get("user_data"),
        })

        return context

# from here vendor page operations starts

class create_inventoryvend(APIView):
    def post(self, request):
        vendor_id = request.session.get("user_id")  # Get current logged-in user's ID from the session
        product_id = request.data.get("product_id")
        quantity = request.data.get("quantity")
        date_added = request.data.get("date_added")

        # Validate the data
        if not vendor_id or not product_id or not quantity:
            return JsonResponse({"status": "fail", "message": "Vendor, Product, and Quantity are required"}, status=400)

        # Fetch the vendor and product from the database
        try:
            vendor = Vendor.objects.get(userid__user_id=vendor_id)
        except Vendor.DoesNotExist:
            return JsonResponse({"status": "fail", "message": "Vendor not found"}, status=400)

        try:
            product = Product.objects.get(pro_id=product_id)
        except Product.DoesNotExist:
            return JsonResponse({"status": "fail", "message": "Product not found"}, status=400)

        # Convert the quantity input to Decimal
        try:
            quantity = Decimal(quantity)
        except InvalidOperation:
            return JsonResponse({"status": "fail", "message": "Invalid quantity format"}, status=400)

        # Create a new inventory item
        inventory_item = InventoryItem(
            vendor=vendor,
            product=product,
            quantity=quantity,
            created_at=date_added
        )
        inventory_item.save()

        # Update the product's quantity by adding the new quantity from inventory
        product.quantiy = product.quantiy + quantity
        product.save()

        return JsonResponse({"status": "pass"})
    
class u_inventoryvend(TemplateView):
    template_name = "vendor/inventory.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        current_user_id = self.request.session.get("user_id")

        # Fetch orders only for the current user using the correct ForeignKey field names
        user_orders = InventoryItem.objects.filter(vendor__userid__user_id=current_user_id)

        # Fetching inventory items
        order_count = Order.objects.count()  # Total orders
        vendor_count = Usertype.objects.filter(user_typee="vendor").count()  # Total vendors
        cust_count = Usertype.objects.filter(user_typee="customer").count()  # Total customers
        employee_count = Usertype.objects.filter(user_typee="employee").count()  # Total employees
        product_count = Product.objects.count()  # Total products
        current_user = self.request.session.get("user_data", None)

        vendor = Vendor.objects.all()
        products = Product.objects.all()

        # Updating context
        context.update({
            "userdata": user_orders,
            "order_count": order_count,
            "vendor_count": vendor_count,
            "cust_count": cust_count,
            "employee_count": employee_count,
            "product_count": product_count,
            "vendor": vendor,
            "products": products,
            "currentuser" :current_user
        })

        return context
    
class vendor_uservend(TemplateView):
    template_name="vendor/profile.html"

    def get_context_data(self,**kwargs):
        context=super().get_context_data(**kwargs)

        # Fetch the current user's ID from the session
        current_user_id = self.request.session.get("user_id")


        # Fetch the vendor data for the logged-in user

        userdata = Vendor.objects.get(userid__user_id=current_user_id)

        vendor_count=Usertype.objects.filter(user_typee ="vendor").count()
        cust_count = Usertype.objects.filter(user_typee="customer").count()
        employee_count = Usertype.objects.filter(user_typee="employee").count()
        product_count = Product.objects.all().count()
        inv_count = InventoryItem.objects.filter(vendor=userdata).count() if userdata else 0
                
        context.update({
            "userdata": userdata,
            "inv_count":inv_count,
            "vendor_count": vendor_count,
            "cust_count": cust_count,
            "employee_count": employee_count,
            "product_count": product_count,
            "currentuser": self.request.session.get("user_data"),
        })
        return context
        
class edit_inventoryvend(APIView):
    def post(self, request):
        inv_id = request.POST.get('id')
        inv_total = request.POST.get('quantity')
        product_id = request.POST.get('product_id')
        i_date = request.POST.get('inv_date')

        inv_total = Decimal(inv_total)  

        inventory_item = InventoryItem.objects.get(inven_id=inv_id)
        old_quantity = inventory_item.quantity

        product = Product.objects.get(pro_id=product_id) 

        InventoryItem.objects.filter(inven_id=inv_id).update(
                quantity=inv_total,
                product=product_id, # Assuming productfk is a ForeignKey
                created_at=i_date,
            )
        
        # Calculate the difference and update the product's quantity accordingly
        quantity_difference = inv_total - old_quantity

        product.quantiy += quantity_difference
        product.save()

        return JsonResponse({"status": "success"}) 

# from here Employee page operations starts
class employee_user11(TemplateView):
    template_name="employee/profile.html"

    def get_context_data(self,**kwargs):
        context=super().get_context_data(**kwargs)

         # Fetch the current user's ID from the session
        current_user_id = self.request.session.get("user_id")


        # Fetch the vendor data for the logged-in user

        userdata = Employee.objects.get(userid__user_id=current_user_id)

        inv_count = InventoryItem.objects.all().count()

        order_count=Order.objects.all().count()
        vendor_count=Usertype.objects.filter(user_typee ="vendor").count()
        cust_count = Usertype.objects.filter(user_typee="customer").count()
        employee_count = Usertype.objects.filter(user_typee="employee").count()
        product_count = Product.objects.all().count()
        current_user = self.request.session.get("user_data", None)
                
        context.update({
            "userdata": userdata,
            "order_count":order_count,
            "vendor_count": vendor_count,
            "cust_count": cust_count,
            "employee_count": employee_count,
            "product_count": product_count,
            "currentuser" :current_user,
            "inv_count":inv_count
        })
        return context  
    
# below is the code for the employee page opertaion

class vendor_user11(TemplateView):
    template_name="employee/vendor.html"

    def get_context_data(self,**kwargs):
        context=super().get_context_data(**kwargs)
        user_data = Vendor.objects.all()
        order_count=Order.objects.all().count()
        vendor_count=Usertype.objects.filter(user_typee ="vendor").count()
        cust_count = Usertype.objects.filter(user_typee="customer").count()
        employee_count = Usertype.objects.filter(user_typee="employee").count()
        product_count = Product.objects.all().count()
        current_user = self.request.session.get("user_data", None)
                
        context.update({
            "userdata": user_data,
            "order_count":order_count,
            "vendor_count": vendor_count,
            "cust_count": cust_count,
            "employee_count": employee_count,
            "product_count": product_count,
            "currentuser" :current_user
        })
        return context


class customer_user11(TemplateView):
    template_name = "employee/customer1.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Fetch user data for customers
        user_data = Customer.objects.all()

        # Count various entities
        order_count = Order.objects.count()
        vendor_count = Usertype.objects.filter(user_typee="vendor").count()
        cust_count = user_data.count()  # Count customers from user_data
        employee_count = Usertype.objects.filter(user_typee="employee").count()
        product_count = Product.objects.count()
        current_user = self.request.session.get("user_data", None)

        # Update context with all the gathered data
        context.update({
            "userdata": user_data,  # Updated to include customer IDs
            "order_count": order_count,
            "vendor_count": vendor_count,
            "cust_count": cust_count,
            "employee_count": employee_count,
            "product_count": product_count,
            "currentuser" :current_user
        })

        return context

class u_product11(TemplateView):
    template_name="employee/product1.html"

    def get_context_data(self,**kwargs):
        context=super().get_context_data(**kwargs)
        user_data=Product.objects.all()
        order_count=Order.objects.all().count()
        vendor_count=Usertype.objects.filter(user_typee ="vendor").count()
        cust_count = Usertype.objects.filter(user_typee="customer").count()
        employee_count = Usertype.objects.filter(user_typee="employee").count()
        product_count = Product.objects.all().count()
        current_user = self.request.session.get("user_data", None)
        products = Product.objects.all()
        categorized_products = {
        'Fruits': products.filter(category='Fruits'),
        'Vegetables': products.filter(category='Vegetables'),
        'Essentials': products.filter(category='Essentials'),
        }
                     
        context.update({
            "userdata": user_data,
            "order_count":order_count,
            "vendor_count": vendor_count,
            "cust_count": cust_count,
            "employee_count": employee_count,
            "product_count": product_count,
            "currentuser" :current_user,
            'categorized_products': categorized_products
        })
        return context
    
class u_order11(TemplateView):
    template_name = "employee/order.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Existing data fetching
        user_data = Order.objects.all()
        order_count = Order.objects.all().count()
        vendor_count = Usertype.objects.filter(user_typee="vendor").count()
        cust_count = Usertype.objects.filter(user_typee="customer").count()
        employee_count = Usertype.objects.filter(user_typee="employee").count()
        product_count = Product.objects.all().count()
        current_user = self.request.session.get("user_data", None)

        # Fetch customers and products for dropdowns
        customers = Customer.objects.all()
        products = Product.objects.all()
        order_data = Order.objects.all()

        # Update the context
        context.update({
            "userdata": user_data,
            "order_count": order_count,
            "vendor_count": vendor_count,
            "cust_count": cust_count,
            "employee_count": employee_count,
            "product_count": product_count,
            "customers": customers,  # Pass customer data for dropdown
            "products": products,  # Pass product data for dropdown
            "orders": order_data,
            "currentuser" :current_user
        })

        return context


class u_inventory11(TemplateView):
    template_name = "employee/inventory.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Fetching inventory items
        user_data = InventoryItem.objects.all()  # All inventory items
        order_count = Order.objects.count()  # Total orders
        vendor_count = Usertype.objects.filter(user_typee="vendor").count()  # Total vendors
        cust_count = Usertype.objects.filter(user_typee="customer").count()  # Total customers
        employee_count = Usertype.objects.filter(user_typee="employee").count()  # Total employees
        product_count = Product.objects.count()  # Total products
        current_user = self.request.session.get("user_data", None)

        inventory_items = InventoryItem.objects.all()
        vendor = Vendor.objects.all()
        products = Product.objects.all()

        # Updating context
        context.update({
            "userdata": user_data,
            "order_count": order_count,
            "vendor_count": vendor_count,
            "cust_count": cust_count,
            "employee_count": employee_count,
            "product_count": product_count,
            "vendor": vendor,
            "products": products,
            'inventory_items': inventory_items,
            "currentuser" :current_user
        })

        return context

