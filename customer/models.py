from django.db import models

# Create your models here.

class Usertype(models.Model):
    user_id = models.AutoField(primary_key=True)
    user_name = models.CharField(max_length=25)
    user_email = models.EmailField(max_length=20)
    user_number = models.IntegerField()
    user_pass=models.CharField(max_length=20)
    user_typee=models.CharField(max_length=20)


class Customer(models.Model):
    cust_id =models.AutoField(primary_key=True) 
    cust_name = models.CharField(max_length=25)
    cust_email = models.EmailField(max_length=20)
    cust_number = models.IntegerField()
    cust_pass=models.CharField(max_length=20)
    userid=models.ForeignKey(Usertype,on_delete=models.CASCADE)

class Employee(models.Model):
    emp_id = models.AutoField(primary_key=True)
    emp_name = models.CharField(max_length=25)
    emp_email = models.EmailField(max_length=20)
    emp_number = models.IntegerField()
    emp_pass=models.CharField(max_length=20)
    userid=models.ForeignKey(Usertype,on_delete=models.CASCADE)

class Vendor(models.Model):
    vend_id = models.AutoField(primary_key=True)
    vend_name = models.CharField(max_length=25)
    vend_email = models.EmailField(max_length=20)
    vend_number = models.IntegerField()
    vend_pass=models.CharField(max_length=20)
    userid=models.ForeignKey(Usertype,on_delete=models.CASCADE)

class Product(models.Model):
    pro_id =models.AutoField(primary_key=True) 
    name = models.CharField(max_length=200)  # Product name
    quantiy = models.DecimalField(max_digits=10, decimal_places=2)  # Price with 2 decimal places
    category= models.CharField(max_length=200)
   

class Order(models.Model):
    order_id =models.AutoField(primary_key=True)
    customerfk=models.ForeignKey(Customer,on_delete=models.CASCADE)
    productfk=models.ForeignKey(Product,on_delete=models.CASCADE)
    created_att = models.DateField()
    total_qt = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    

class InventoryItem(models.Model):
    inven_id =models.AutoField(primary_key=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)  # Link to Product
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)    # Link to Vendor
    quantity = models.DecimalField(max_digits=10, decimal_places=2) # Quantity of the product
    created_at = models.DateField()             # Date the item was added
