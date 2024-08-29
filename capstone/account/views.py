from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages

# Create your views here.


def auth_view(request):
    if request.method == 'POST':
        # Determine if the request is for sign-up or login based on the button clicked
        if 'signup' in request.POST:
            username = request.POST.get('username').lower()
            email = request.POST.get('email').lower()
            password = request.POST.get('password')

            # Check if the username already exists
            if User.objects.filter(username=username).exists():
                messages.error(request, "Username already exists!")
            elif User.objects.filter(email=email).exists():
                messages.error(request, "Email already Exists!")
            else:
                # Create a new user
                user = User.objects.create_user(
                    username=username, email=email, password=password)
                messages.success(
                    request, "Account created successfully! You can now log in.")
                # Redirect to dashboard or wherever
                return redirect('dashboard')

        elif 'signin' in request.POST:
            email = request.POST.get('email').lower()
            password = request.POST.get('password')

            # Authenticate using email
            try:
                user = User.objects.get(email=email)
                user = authenticate(
                    request, username=user.username, password=password)
                if user is not None:
                    login(request, user)
                    # Redirect to the dashboard or another page
                    return redirect('dashboard')
                else:
                    messages.error(request, "Invalid email or password!")
            except User.DoesNotExist:
                messages.error(request, "Email does not exist!")
    return render(request, 'pages/auth.html')


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required(login_url="login")
def dashboard_view(request):
    return render(request, 'pages/dashboard.html')
