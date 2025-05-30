from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.


# Course Related Model
class Course(models.Model):
    name = models.CharField(max_length=200)
    students = models.ManyToManyField(User,  through="CourseUser")
    
    #class Meta:
    #    permissions = [
    #        ('create_task','Create Task'),
    #        ('create_')
    #    ]

    def __str__(self):
        return self.name




# Achievement Models - might spin these out later

class AchievementRarity(models.TextChoices):
    COMMON = 'CM', 'Common'
    RARE = 'RA', 'Rare'
    EPIC = 'EP', 'Epic'
    LEGENDARY = 'LG', 'Legendary'


class Achievement(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="achievements")
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=200)
    rarity = models.CharField(max_length=2, choices=AchievementRarity.choices, default=AchievementRarity.COMMON)
    point_value = models.IntegerField("Point Value",default=5)

    def is_earned_by(self, user):
        triggers = self.triggers.all()
        #print(triggers)
        return all( # Return all completed tests
            CourseUserTriggerProgress.objects.filter(user=user, trigger=trigger, fulfilled=True).exists() for trigger in triggers
        )
    
    def __str__(self):
        return self.name




class AchievementTrigger(models.Model):
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE, related_name="triggers")
    triggering_test_name = models.CharField(max_length=200)
    triggering_status = models.BooleanField("Trigger on Test Success",default=True)

    def __str__(self):
        return self.achievement.name + " Trigger: " + self.triggering_test_name + " " + str(self.triggering_status)
    


# If I spin out the achievement models, spin out the
class CourseUser(models.Model):
    # This is a through model. It handles the relation.
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    gitlab_user_id = models.IntegerField(default=0)
    #started_tasks = models.OneToMany()
    achievements = models.ManyToManyField(Achievement, blank=True)
    points = models.IntegerField(default=0)
    leaderboard_optin = models.BooleanField(default=False)


class CourseUserTriggerProgress(models.Model):
    user = models.ForeignKey(CourseUser, on_delete=models.CASCADE, related_name="achievement_progress")
    trigger = models.ForeignKey(AchievementTrigger, on_delete=models.CASCADE)
    fulfilled = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user','trigger'],name="unique_user_trigger_progress")
        ]        

class TaskGroup(models.Model):
    name = models.CharField(max_length=200)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

class Task(models.Model): # This needs more
    name = models.CharField(max_length=200)
    task_group = models.ForeignKey(TaskGroup, on_delete=models.CASCADE, related_name='tasks')
    #base_repo_link = models.
    # Should have a base repo link to clone from but let's create the cloning functionality later. It is superfluous for a prototype
    

class StartedTask(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="started_tasks")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="started_tasks")
    started_at = models.DateTimeField(auto_now_add=True)

class QueuedAchievementToast(models.Model):
    received_at = models.DateTimeField(default=timezone.now)
    user = models.ForeignKey(CourseUser, on_delete=models.CASCADE)
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE)


    # Wouldn't make sense to queue up the same achievement twice. 
    # Queue will be cleared, though. So will need to check if user has achievement before queueing
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user','achievement'], name="unique_user_achievement_toast")
        ]
    
    def __str__(self):
        return self.user.user.username + ": " + self.achievement.name



#class Subtask(models.Model):
