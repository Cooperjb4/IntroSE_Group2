from django.urls import path
from . import views  # Import views from the current app

urlpatterns = [
    path('', views.entry, name='entry'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.login_view, name='logout'),
    path('signup/', views.signup, name='signup'),
    path('edit-account/', views.edit_account, name='edit_account'),
    path('delete-own-account/', views.delete_own_account, name='delete_own_account'),
    path('delete-account/<int:user_id>/', views.delete_account, name='delete_account'),
    path('home/', views.home, name='home'),
    path('search/', views.search, name='search'),
    path('cart/', views.cart, name='cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('checkout-details/', views.checkout_details, name='checkout_details'),
    path('account/', views.account, name='account'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('seller-dashboard/', views.seller_dashboard, name='seller_dashboard'),
    path('add-product/', views.add_product, name='add_product'),
    path('delete-product/<int:product_id>/', views.delete_product, name='delete_product'),
    path('delete-own-product/<int:product_id>/', views.delete_own_product, name='delete_own_product'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove-from-cart/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('clean-cart-duplicates/', views.clean_cart_duplicates, name='clean_cart_duplicates'),
]