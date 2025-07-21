from django.http import HttpResponse
from ratelimit.decorators import ratelimit
from django.contrib.auth import authenticate, login

# Step 4: Define a function that returns rate limit based on user auth status
def dynamic_rate_limit(request):
    if request.user.is_authenticated:
        return '10/m'  # 10 requests per minute for authenticated users
    else:
        return '5/m'   # 5 requests per minute for anonymous users

# Apply the dynamic rate limit to your login view

@ratelimit(key='ip', rate= dynamic_rate_limit, block=True)  # default limit, will override below
def login_view(request):
    if request.method == 'POST':
        # Limit based on user auth status dynamically:
        # You can check if user is authenticated and adjust rate limit
        user = authenticate(username=request.POST['username'], password=request.POST['password'])
        if user is not None:
            login(request, user)
            return HttpResponse("Logged in")
        else:
            return HttpResponse("Invalid credentials", status=401)
    return HttpResponse("Login page")
