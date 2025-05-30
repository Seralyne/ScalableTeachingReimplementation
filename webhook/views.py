from django.shortcuts import render
import datetime, json
from secrets import compare_digest

from django.conf import settings
from django.db.transaction import atomic, non_atomic_requests
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseNotFound, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.core.exceptions import BadRequest
from django.utils import timezone
from .models import WebhookMessage
from courses.models import Achievement, QueuedAchievementToast, CourseUser, AchievementTrigger, CourseUserTriggerProgress
from http import HTTPStatus
import requests

# Create your views here.



# Test Webhook Functionality
@require_POST
@non_atomic_requests
@csrf_exempt
def webhook_test(request):
    given_token = request.headers.get("Achievement-Webhook-Token", "")
    if not compare_digest(given_token, settings.ACHIEVEMENT_WEBHOOK_TOKEN): # Protect against weaponized autism (also known as timing attacks)
        return HttpResponseForbidden("Incorrect token in Webhook-Token header.", content_type="text/plain")
    
    WebhookMessage.objects.filter(
        received_at__lte=timezone.now() - datetime.timedelta(days=7) # Delete Webhook messages older than a week
    ).delete()

    payload = json.loads(request.body)
    WebhookMessage.objects.create(received_at=timezone.now(), payload=payload)
    return HttpResponse("Message received okay.", content_type="text/plain")


# Actual Implementation
@require_POST
@non_atomic_requests
@csrf_exempt
def achievement_webhook(request):
    given_token = request.headers.get("Achievement-Webhook-Token", "")
    if not compare_digest(given_token, settings.ACHIEVEMENT_WEBHOOK_TOKEN): # Protect against weaponized autism (also known as timing attacks)
        return HttpResponseForbidden("Incorrect token in Webhook-Token header.", content_type="text/plain")
    
    WebhookMessage.objects.filter(
        received_at__lte=timezone.now() - datetime.timedelta(days=7) # Delete Webhook messages older than a week
    ).delete()

    payload = json.loads(request.body)
    WebhookMessage.objects.create(received_at=timezone.now(), payload=payload)
    message, status = process_achievement_webhook_payload(payload)
    
    # A returned response will always follow the format (Message: string, HTTPStatus)

    return HttpResponse(message, status=status, content_type="text/plain")


@require_POST
@non_atomic_requests
@csrf_exempt
def gitlab_receive(request):
    given_token = request.headers.get('X-Gitlab-Token')
    if not compare_digest(given_token,  settings.GITLAB_WEBHOOK_TOKEN):
        return HttpResponseForbidden("Incorrect token in X-Gitlab-Token header.", content_type="text/plain")
    event_type = request.headers.get("X-Gitlab-Event")
    if event_type != "Pipeline Hook": # For this project, I don't care about anything other than Pipeline Hooks.
        return HttpResponseBadRequest("Not Applicable")
    
    payload = json.loads(request.body)

    #print(payload)

    process_gitlab_pipeline(payload.get("project").get("id"))
    
    #print(payload)

    return HttpResponse(request.body)


    
    
    # Not ideal. Behaviour is different based off test environment or not. Too bad!


@atomic 
def process_gitlab_pipeline(project_id):
    #print(project_id)
    gitlab_api_url = settings.GITLAB_URL + "/api/v4/projects/{project_id}/jobs".format(project_id=project_id)
    #print(gitlab_api_url)
    try:
        req = requests.get(gitlab_api_url)
        output_obj = req.json()
        #print()
        #print(output_obj)
        tests_isolated = isolate_test_and_result(output_obj)
        #print(tests_isolated)
        res = add_achievement_progress_from_tests(tests_isolated)
    except requests.HTTPError as e:
        if e.response_status_code == HTTPStatus.NOT_FOUND:
            return ('Project not found or service not running', HTTPStatus.NOT_FOUND)
        else:
            return ('Unknown Error, See Status Code: ', e.response_status_code)
        

# Future Work: Make this only consider recent jobs.
@atomic
def isolate_test_and_result(jobs):
    """"Reduces output to something more manageable - ie. test name and status of test"""
    list_of_processed_jobs = []
    for job in jobs:
        status = job.get("status")
        if status == "pending": # If job hasn't finished processing, skip for now.
            continue
        name = job.get("name")
        gitlab_user_id = job.get("user").get("id")
        #print(gitlab_user_id)
        succeeding = True if status == "success" else False # Convert to boolean
        #print("Test ", name , " Succeeding", succeeding)
        list_of_processed_jobs.append({"name": name,"succeeding": succeeding, "gitlab_user_id": gitlab_user_id})
        
    #print(list_of_processed_jobs)
    return list_of_processed_jobs        

# Future Work: Generalize beyond a single achievement.
@atomic
def add_achievement_progress_from_tests(isolated_tests):
    for entry in isolated_tests:
        gitlab_user_id=entry.get("gitlab_user_id")
        test_name = entry.get("name")
        #print(test_name)
        #print(gitlab_user_id)
        user = CourseUser.objects.get(gitlab_user_id=gitlab_user_id)
        #print(user.id, user.gitlab_user_id)
        try:
            test_triggers = AchievementTrigger.objects.filter(triggering_test_name=test_name)
            for trigger in test_triggers:
                if trigger.triggering_status == entry.get("succeeding"):
                    #print(trigger.triggering_test_name, trigger.triggering_status)
                    add_progress(trigger, user)
                    #print("Looking up user progress")
                    progress = CourseUserTriggerProgress.objects.filter(user=user)
                    #for progressed_trigger in progress:
                        #print("User ID: ", progressed_trigger.user.id, "Trigger Test:", progressed_trigger.trigger.triggering_test_name,"Trigger Criteria:",progressed_trigger.trigger.triggering_status, "Fulfilled:", progressed_trigger.fulfilled)
                if trigger.achievement.is_earned_by(user):
                    #print("Reached earned by on achievement", trigger.achievement.name)
                    award_achievement_and_queue_toast(trigger.achievement, user)
        except AchievementTrigger.DoesNotExist:
            continue # No triggers involving this test. Move on.
        #print(test_triggers)
    #print(Achievement.objects.all())
    pass
    

# This was ugly enough to spin out into its own method
@atomic
def add_progress(trigger, user):
    try:
        progress_entry = CourseUserTriggerProgress.objects.get(trigger=trigger,user=user)
        progress_entry.fulfilled = True
        progress_entry.save()
    except CourseUserTriggerProgress.DoesNotExist:
        progress_entry = CourseUserTriggerProgress.objects.create(user=user, trigger=trigger, fulfilled=True)
        progress_entry.save()
    

@atomic
def award_achievement_and_queue_toast(achievement, user):
    award_achievement(achievement, user)
    queue_toast(achievement, user)

@atomic
def award_achievement(achievement, user):
    try:
        user = CourseUser.objects.get(id=user.id)
        achievement = Achievement.objects.get(id=achievement.id)
        user.achievements.add(achievement)
        user.points += achievement.point_value
        user.save()
    except CourseUser.DoesNotExist:
        return ("User not found", HTTPStatus.NOT_FOUND)
    except Achievement.DoesNotExist:
        return ("Achievement not found", HTTPStatus.NOT_FOUND)

@atomic    
def queue_toast(achievement, user):
    try:
        delete_old_toasts()
        QueuedAchievementToast.objects.create(user=user, achievement=achievement)
        return ("Achievement granted successfully", HTTPStatus.OK)
    except CourseUser.DoesNotExist:
        return ("User not found", HTTPStatus.NOT_FOUND)
    except Achievement.DoesNotExist:
        return ("Achievement not found", HTTPStatus.NOT_FOUND)

@atomic
def delete_old_toasts():
    QueuedAchievementToast.objects.filter(
        received_at__lte=timezone.now() - datetime.timedelta(days=30) # Delete toasts older than a month. 
    ).delete()

@atomic
def process_achievement_webhook_payload(payload):
    username = payload.get("user")
    achievement_id = payload.get("id")
    if not achievement_id or not username:
        return ("Ensure you've formatted your request properly.", HTTPStatus.BAD_REQUEST)
    
    try:
        user = CourseUser.objects.get(id=username)
        achievement = Achievement.objects.get(id=achievement_id)
        user.achievements.add(achievement)
        user.points += achievement.point_value
        user.save()
    except CourseUser.DoesNotExist:
        return ("User not found", HTTPStatus.NOT_FOUND)
    except Achievement.DoesNotExist:
        return ("Achievement not found", HTTPStatus.NOT_FOUND)
    
    # If this succeeds, create a achievement toast in the queue.
    # If we've made it this far, both the user and the achievement are known good.

    QueuedAchievementToast.objects.filter(
        received_at__lte=timezone.now() - datetime.timedelta(days=30) # Delete toasts older than a month. 
    ).delete()

    QueuedAchievementToast.objects.create(user=user, achievement=achievement)
    return ("Achievement granted successfully", HTTPStatus.OK)
    

