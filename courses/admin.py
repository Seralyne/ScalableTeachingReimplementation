from django.contrib import admin

# Register your models here.
from .models import Achievement, QueuedAchievementToast, Course, AchievementTrigger, CourseUser

admin.site.register(Achievement)
admin.site.register(QueuedAchievementToast)
#admin.site.register(Course)
admin.site.register(AchievementTrigger)


class CourseUserInline(admin.TabularInline):
    model = CourseUser
    extra = 1

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    inlines = [CourseUserInline]