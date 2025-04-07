from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User, Group
from .models import Product, Cart
from django.db.models import Count
from django.db import transaction

# Define your functions here

#LOGIN - LOGOUT - SIGN UP
def entry(request):
    return render(request, 'entry.html')

def signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        role = request.POST.get('role')  # Expecting 'Admin', 'Seller', or 'User'
        
        if len(password) < 8:
            messages.error(request, 'Password must be at least 8 characters')
            return render(request, 'signup.html')
            
        # Check if username already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return render(request, 'signup.html')
            
        # Create the user
        user = User.objects.create_user(username=username, password=password)
        
        # Assign user to the selected group
        if role in ['Admin', 'Seller', 'User']:
            try:
                group, created = Group.objects.get_or_create(name=role)  # Ensure group exists
                user.groups.add(group)
            except Exception as e:
                messages.error(request, f"Error assigning role: {str(e)}")
                return render(request, 'signup.html')
        else:
            messages.error(request, 'Invalid role selected')
            return render(request, 'signup.html')

        login(request, user)  # Log the user in
        return redirect('home')
    
    return render(request, 'signup.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('home')  # Redirect to home page after login
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('entry')

def home(request):
    products = Product.objects.all()  # Fetch all products from the database
    return render(request, 'home.html', {'products': products})

def search(request):
    query = request.GET.get('query', '')  # Get the search query from the request
    products = Product.objects.filter(name__icontains=query)  # Filter products based on the query
    return render(request, 'home.html', {'products': products, 'query': query})

def cart(request):
    # Fetch all cart items for the logged-in user
    cart_items = Cart.objects.filter(user=request.user)
    return render(request, 'cart.html', {'cart_items': cart_items})

def checkout(request):
    return render(request, 'checkout.html')

def checkout_details(request):
    return render(request, 'checkoutDetails.html')

@login_required
def account(request):
    # Get the user's permissions
    permissions = request.user.get_all_permissions()

    # Get the user's group (role)
    groups = request.user.groups.all()  # A user can belong to multiple groups
    role = groups[0].name if groups else "No role assigned"  # Get the first group or a default message

    return render(request, 'account.html', {'permissions': permissions, 'role': role})

@login_required
def edit_account(request):
    if request.method == 'POST':
        new_username = request.POST.get('username')
        new_password = request.POST.get('password')
        new_role = request.POST.get('role')  # Expecting 'Admin', 'Seller', or 'User'
        
        user = request.user #gets the currently logge d in user

        #basically if the new username doesnt already exist, then update username
        if new_username:
            if User.objects.filter(username=new_username).exists():
                messages.error(request, 'Username already exists')
            else:
                user.username = new_username
        
        # Update the password if provided
        if new_password:
            if len(new_password) < 8:
                messages.error(request, 'Password must be at least 8 characters.')
            else:
                user.set_password(new_password)  # Use set_password to hash the password
        
        if new_role in ['Admin', 'Seller', 'User']:
            # Remove the user from all groups first
            user.groups.clear()
            try:
                group, created = Group.objects.get_or_create(name=new_role)  # Ensure group exists
                user.groups.add(group)
            except Exception as e:
                messages.error(request, f"Error assigning role: {str(e)}")

        user.save()

        if new_password:
            # If the password was changed, log the user out and redirect to login
            messages.success(request, 'Password changed successfully. Please log in again.')
            logout(request)
            return redirect('login')
        
        messages.success(request, 'Account updated successfully')
        return redirect('account')
    
    return render(request, 'account.html')

@login_required
def delete_account(request, user_id):
    if request.method == 'POST':
        try:
            user_to_delete = User.objects.get(id=user_id)
            if user_to_delete != request.user:  # Prevent self-deletion
                user_to_delete.delete()
                messages.success(request, f"User '{user_to_delete.username}' deleted successfully.")
            else:
                messages.error(request, "You cannot delete your own account.")
        except User.DoesNotExist:
            messages.error(request, "User not found.")
        return redirect('admin_dashboard')  # Redirect back to the admin dashboard

@login_required
def delete_own_account(request):
    if request.method == 'POST':
        user = request.user
        logout(request)  # Log the user out before deleting
        user.delete()
        messages.success(request, 'Account deleted successfully')
        return redirect('entry')
    return render(request, 'account.html')

@login_required
def admin_dashboard(request):
    if request.user.groups.filter(name='Admin').exists():  # Ensure only Admins can access
        users = User.objects.all()  # Fetch all users
        products = Product.objects.all()  # Fetch all products
        return render(request, 'admin_dashboard.html', {'users': users, 'products': products})
    else:
        return redirect('home')
    
@login_required
def seller_dashboard(request):
    if request.user.groups.filter(name='Seller').exists():
        # Fetch products related to the seller
        products = Product.objects.filter(seller=request.user)
        return render(request, 'seller_dashboard.html', {'products': products})
    
def add_product(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        price = request.POST.get('price')
        stock = request.POST.get('stock')
        image = request.FILES.get('image')  

        # Error checking for the product details
        try: 
            price = float(price)  # Convert price to float
            stock = int(stock)  # Convert stock to integer

            if price <= 0 or stock <= 0:
                raise ValueError("Price must be positive")
        except ValueError:
            messages.error(request, 'Invalid price. Please enter a positive number.')
            return redirect('seller_dashboard')
        
        # Create a new product instance
        product = Product(name=name, description=description, price=price, stock=stock, image=image, seller=request.user)
        product.save()
        
        messages.success(request, 'Product added successfully')
        return redirect('seller_dashboard')  # Redirect to the seller dashboard after adding the product
    
    return render(request, 'seller_dashboard.html')

def delete_product(request, product_id):
    if request.method == 'POST':
        try:
            product = Product.objects.get(id=product_id)
            product.delete()
            messages.success(request, 'Product deleted successfully')
        except Product.DoesNotExist:
            messages.error(request, 'Product not found')
        return redirect('admin_dashboard')  # Redirect back to the seller dashboard

def delete_own_product(request, product_id):
    if request.method == 'POST':
        try:
            product = Product.objects.get(id=product_id)
            product.delete()
            messages.success(request, 'Product deleted successfully')
        except Product.DoesNotExist:
            messages.error(request, 'Product not found')
        return redirect('seller_dashboard')  # Redirect back to the seller dashboard
    
def add_to_cart(request, product_id):
    if request.method == 'POST':
        product = Product.objects.get(id=product_id)

        cart_item, created = Cart.objects.get_or_create(user=request.user, product=product)
        if not created: #if item already exists
            cart_item.quantity += 1  # Increment quantity if already in cart
            cart_item.save()
        
        messages.success(request, f'{product.name} added to cart')
    return redirect('home')

def remove_from_cart(request, product_id):
    if request.method == 'POST':
        cart_item = Cart.objects.get(product__id=product_id, user=request.user)
        cart_item.delete()

        messages.success(request, 'Product removed from cart')
    return redirect('cart')

def checkout(request):
    if request.method == 'POST':
        cart_items = Cart.objects.filter(user=request.user)
        total_price = 0

        with transaction.atomic(): #makes sure all operations either happen or nothing happens             
            for item in cart_items:
                #adds the price of each item in the cart to the total price
                total_price += item.product.price * item.quantity 
                
                # deduct stock
                item.product.stock -= item.quantity  
                item.product.save()  # save after you mess with database

                item.delete()  # remove item from cart

            # add money to the seller's bank
            item.product.seller.profile.bank += total_price
            item.product.seller.profile.save()

            #update bank balance of user
            request.user.profile.bank -= total_price 
            request.user.profile.save()
        messages.success(request, 'Checkout successful')
        return redirect('home')
    
    return redirect('cart')

#get rid of this function at the end
@login_required
def clean_cart_duplicates(request):
    # Find duplicate cart items
    duplicates = Cart.objects.values('user', 'product').annotate(count=Count('id')).filter(count__gt=1)

    for duplicate in duplicates:
        user = duplicate['user']
        product = duplicate['product']
        cart_items = Cart.objects.filter(user=user, product=product)
        total_quantity = sum(item.quantity for item in cart_items)
        # Keep one entry and update its quantity
        first_item = cart_items.first()
        first_item.quantity = total_quantity
        first_item.save()
        # Delete the other duplicates
        cart_items.exclude(id=first_item.id).delete()

    messages.success(request, "Duplicate cart items have been cleaned up.")
    return redirect('home')  # Redirect to the homepage or any other page