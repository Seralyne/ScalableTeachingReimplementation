from django.shortcuts import render
from django.http import HttpResponse
from .models import Course, CourseUser
from django.contrib.auth.decorators import login_required


# Create your views here.

@login_required
def index(request):
    return render(request, "courses_list.html", {
        "course_users": CourseUser.objects.filter(user=request.user)
    })


@login_required
def course(request, id):
    course = Course.objects.get(id=id)
    return render(request, "course_page.html", {
        "course": course,
        "course_user": CourseUser.objects.get(user=request.user, course=course)

    })