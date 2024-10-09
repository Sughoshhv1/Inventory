from django.urls import path #type:ignore

from . import views
# from .views import landing, login,signup, admin1,login_check,vendor_user,employee_user,customer_user

urlpatterns = [
    path("", views.landing, name="landing"),
    path("login/", views.login, name="login"),
    path("signup/", views.signup, name="signup"),
    path("admin1/", views.admin1, name="admin1"),
    path('login_check/',views.login_check.as_view(),name='login_check'),
    path('create/',views.create.as_view(),name='create'),
    path('userview/',views.userview.as_view(),name='userview'),
    path('delete_user',views.delete_user.as_view(),name='delete_user'),
    path('vendor_user/',views.vendor_user.as_view(),name='vendor_user'),
    path('customer_user/',views.customer_user.as_view(),name='customer_user'),
    path('employee_user/',views.employee_user.as_view(),name='employee_user'),
    path('create_product/',views.CreateProduct.as_view(),name='create_product'),
    path('u_product/',views.u_product.as_view(),name='u_product'),
    path('delete_product/',views.delete_product.as_view(),name='delete_product'),
    path('create_order/',views.CreateOrder.as_view(),name='create_order'),
    path('u_order/',views.u_order.as_view(),name='u_order'),
    path('delete_order/',views.delete_order.as_view(),name='delete_order'),
    path('create_inventory',views.create_inventory.as_view(),name='create_inventory'),
    path('u_inventory/',views.u_inventory.as_view(),name='u_inventory'),
    path('delete_inventory/',views.delete_inventory.as_view(),name='delete_inventory'),
    path('edit_user/', views.edit_user.as_view(), name='edit_user'),
    path('edit_inventory/', views.edit_inventory.as_view(), name='edit_inventory'),
    path('edit_order/', views.edit_order.as_view(), name='edit_order'),
    path('edit_product/', views.edit_product.as_view(), name='edit_product'),
    path('logout/', views.logout.as_view(), name='logout'),
    path('u1_order/',views.u1_order.as_view(),name='u1_order'),
    path('CreateOrdercust/',views.CreateOrdercust.as_view(),name='CreateOrdercust'),
    path('edit_ordercust/', views.edit_ordercust.as_view(), name='edit_ordercust'),
    path('customer_usercust/',views.customer_usercust.as_view(),name='customer_usercust'),
    path('u_orderhistory/', views.u_orderhistory.as_view(), name='u_orderhistory'),

    path('create_inventoryvend/',views.create_inventoryvend.as_view(),name='create_inventoryvend'),
    path('u_inventoryvend/', views.u_inventoryvend.as_view(), name='u_inventoryvend'),
    path('vendor_uservend/',views.vendor_uservend.as_view(),name='vendor_uservend'),
    path('edit_inventoryvend/', views.edit_inventoryvend.as_view(), name='edit_inventoryvend'),
    path('u_inventoryvendhistory/', views.u_inventoryvendhistory.as_view(), name='u_inventoryvendhistory'),

    path('employee_user11/', views.employee_user11.as_view(), name='employee_user11'),
    path('vendor_user11/', views.vendor_user11.as_view(), name='vendor_user11'),
    path('customer_user11/', views.customer_user11.as_view(), name='customer_user11'),
    path('u_product11/', views.u_product11.as_view(), name='u_product11'),
    path('u_order11/', views.u_order11.as_view(), name='u_order11'),
    path('u_inventory11/', views.u_inventory11.as_view(), name='u_inventory11'),

    path('search_products/', views.ProductSearchView.as_view(), name='search_products'),
    path('get_product_cost/', views.GetProductCost.as_view(), name='get_product_cost'),
    path('confirm_payment/', views.confirm_payment, name='confirm_payment'),
    
]