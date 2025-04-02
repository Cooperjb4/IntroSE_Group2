from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User, Group

# Create your views here.

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
    return render(request, 'home.html')

def cart(request):
    return render(request, 'cart.html')

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
        return render(request, 'admin_dashboard.html', {'users': users})
    else:
        return redirect('home')
    
