from django.shortcuts import render, redirect
from .forms import SignupForm
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from courses.models import CourseUser, Achievement

# Create your views here.

def index(request):
    return render(request, 'home.html')

def user_profile(request):
    best_accomplishment = CourseUser.objects.filter(user=request.user).order_by('-points').first() # Get course user objects and order by points in descending order, take the first element to get best accomplishment
    all_achievements = Achievement.objects.filter(courseuser__user=request.user).distinct()
    context = {"best_accomplishment": best_accomplishment, "all_achievements": all_achievements}

    return render(request, "user_profile.html", context)

def signup(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password1")
            new_user = authenticate(username=username, password=password)
            if new_user is not None:
                login(request, new_user)
                messages.success(request, ("Registration Successful"))
                return redirect('courses')
        else:
            print(form.errors)
    else:
        form = SignupForm()

    context = {
        "form": form
    }
    return render(request, "signup.html", context)


def login_user(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('courses')
        else:
            messages.success(request, ("There was an error logging you in. Double check your credentials and try again."))
            return redirect('login')
    else:
        return render(request, 'login.html')


