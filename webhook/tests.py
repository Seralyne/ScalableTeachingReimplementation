from django.test import TestCase, Client, override_settings
from django.utils import timezone
import datetime 
from http import HTTPStatus
from django.contrib.auth import get_user_model
from .models import WebhookMessage
from courses.models import Course, CourseUser, Achievement, QueuedAchievementToast, AchievementRarity, AchievementTrigger, CourseUserTriggerProgress
import json
import requests
# Create your tests here.

@override_settings(ACHIEVEMENT_WEBHOOK_TOKEN="Tell me, for whom do you fight?", GITLAB_WEBHOOK_TOKEN="GitDeezNuts", GITLAB_URL="http://localhost:5000")
class WebhookTests(TestCase):
    def setUp(self):
        self.client = Client(enforce_csrf_checks=True)
    
    def test_if_post_is_mandated(self):
        response = self.client.get("/webhooks/test")
        assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED
    
    def test_missing_header_token(self):
        response = self.client.post("/webhooks/test")
        assert response.status_code == HTTPStatus.FORBIDDEN

        assert (response.content.decode() == "Incorrect token in Webhook-Token header.")

    def test_bad_token(self):
        response = self.client.post("/webhooks/test", HTTP_ACHIEVEMENT_WEB_TOKEN="Hmph! How very glib! And do you believe in Eorzea?")
        assert response.status_code == HTTPStatus.FORBIDDEN
        assert (response.content.decode() == "Incorrect token in Webhook-Token header.")

    def test_webhook_recieveability(self):
        start = timezone.now()
        old_message = WebhookMessage.objects.create(received_at=start - datetime.timedelta(days=100)) # Create very old message for test

        response = self.client.post("/webhooks/test", 
                                    HTTP_ACHIEVEMENT_WEBHOOK_TOKEN="Tell me, for whom do you fight?", 
                                    content_type="application/json", 
                                    data={
                                        "eorzea": [
                                            "'s unity is forged on falsehoods",
                                            "'s' city states are built on deceit", 
                                            "'s faith is an instrument of deception.",
                                            " is naught but a cobweb of lies."
                                            ]
                                        }
                                    )
        
        #print(response.content.decode())
        assert response.status_code == HTTPStatus.OK
        assert response.content.decode() == "Message received okay."
        assert not WebhookMessage.objects.filter(id=old_message.id).exists()
        webhookmessage = WebhookMessage.objects.get()
        assert webhookmessage.received_at >= start 
        assert webhookmessage.payload == {
                                        "eorzea": [
                                            "'s unity is forged on falsehoods",
                                            "'s' city states are built on deceit", 
                                            "'s faith is an instrument of deception.",
                                            " is naught but a cobweb of lies."
                                            ]
                                        }
        


    def test_award_achievement_no_user(self):
        start = timezone.now()
        User = get_user_model()
        user = User.objects.create_user(username="testuser", password="testpassword")
        course = Course.objects.create(name="Test")
        test_achievement = Achievement.objects.create(course=course, name="Test", description="Test", rarity=AchievementRarity.COMMON, point_value=5)
        response = self.client.post("/webhooks/achievement/award", 
                                    HTTP_ACHIEVEMENT_WEBHOOK_TOKEN="Tell me, for whom do you fight?", 
                                    content_type="application/json", 
                                    data={
                                        "id": test_achievement.id,
                                        }
                                    )
        
        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert response.content.decode() == "Ensure you've formatted your request properly."



    def test_award_achievement_no_achievement(self):
        start = timezone.now()
        User = get_user_model()
        user = User.objects.create_user(username="testuser", password="testpassword")
        course = Course.objects.create(name="Test")
        course.students.add(user)
        course.students.get()
        course_user = CourseUser.objects.get(user=user, course=course)
        response = self.client.post("/webhooks/achievement/award", 
                                    HTTP_ACHIEVEMENT_WEBHOOK_TOKEN="Tell me, for whom do you fight?", 
                                    content_type="application/json", 
                                    data={
                                        "user": course_user.id,
                                        }
                                    )
        
        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert response.content.decode() == "Ensure you've formatted your request properly."
        


    def test_award_achievement_nonexistent_user(self):
        start = timezone.now()
        User = get_user_model()
        user = User.objects.create_user(username="testuser", password="testpassword")
        course = Course.objects.create(name="Test")
        course.students.add(user)
        course.students.get()
        course_user = CourseUser.objects.get(user=user, course=course)
        test_achievement = Achievement.objects.create(course=course, name="Test", description="Test", rarity=AchievementRarity.COMMON, point_value=5)
        test_achievement_another = Achievement.objects.create(course=course, name="Test two", description="Test two", rarity=AchievementRarity.COMMON, point_value=5)
        old_achievement_toast = QueuedAchievementToast.objects.create(user=course_user, achievement=test_achievement_another, received_at=start - datetime.timedelta(days=100))

        response = self.client.post("/webhooks/achievement/award", 
                                    HTTP_ACHIEVEMENT_WEBHOOK_TOKEN="Tell me, for whom do you fight?", 
                                    content_type="application/json", 
                                    data={
                                        "id": test_achievement.id,
                                        "user": -1
                                        }
                                    )
        
        
        assert response.status_code == HTTPStatus.NOT_FOUND
        assert response.content.decode() == "User not found"


    def test_award_achievement_nonexistent_achievement(self):
        start = timezone.now()
        User = get_user_model()
        user = User.objects.create_user(username="testuser", password="testpassword")
        course = Course.objects.create(name="Test")
        course.students.add(user)
        course.students.get()
        course_user = CourseUser.objects.get(user=user, course=course)
        test_achievement = Achievement.objects.create(course=course, name="Test", description="Test", rarity=AchievementRarity.COMMON, point_value=5)
        test_achievement_another = Achievement.objects.create(course=course, name="Test two", description="Test two", rarity=AchievementRarity.COMMON, point_value=5)
        old_achievement_toast = QueuedAchievementToast.objects.create(user=course_user, achievement=test_achievement_another, received_at=start - datetime.timedelta(days=100))

        response = self.client.post("/webhooks/achievement/award", 
                                    HTTP_ACHIEVEMENT_WEBHOOK_TOKEN="Tell me, for whom do you fight?", 
                                    content_type="application/json", 
                                    data={
                                        "id": -1,
                                        "user": course_user.id
                                        }
                                    )
        
        
        assert response.status_code == HTTPStatus.NOT_FOUND
        assert response.content.decode() == "Achievement not found"


    def test_award_achievement(self):
        start = timezone.now()
        User = get_user_model()
        user = User.objects.create_user(username="testuser", password="testpassword")
        course = Course.objects.create(name="Test")
        course.students.add(user)
        course.students.get()
        course_user = CourseUser.objects.get(user=user, course=course)
        test_achievement = Achievement.objects.create(course=course, name="Test", description="Test", rarity=AchievementRarity.COMMON, point_value=5)
        test_achievement_another = Achievement.objects.create(course=course, name="Test two", description="Test two", rarity=AchievementRarity.COMMON, point_value=5)
        old_achievement_toast = QueuedAchievementToast.objects.create(user=course_user, achievement=test_achievement_another, received_at=start - datetime.timedelta(days=100))

        response = self.client.post("/webhooks/achievement/award", 
                                    HTTP_ACHIEVEMENT_WEBHOOK_TOKEN="Tell me, for whom do you fight?", 
                                    content_type="application/json", 
                                    data={
                                        "id": test_achievement.id,
                                        "user": course_user.id
                                        }
                                    )
        
        
        #print(response.content.decode())
        assert response.status_code == HTTPStatus.OK
        assert response.content.decode() == "Achievement granted successfully"
        assert not QueuedAchievementToast.objects.filter(id=old_achievement_toast.id).exists()
        assert course_user.achievements.filter(id=test_achievement.id).exists()
        assert QueuedAchievementToast.objects.filter(user=course_user, achievement=test_achievement).exists()
        
    

    def test_gitlab_webhook_single_test_award_fail(self):
        # Ensure not user error.
        api_online = requests.get("http://localhost:5000/ping")
        assert api_online.status_code == HTTPStatus.OK, "Flask API unreachable. Ensure that the Flask API is running. You can do this by running `flask --app gitlab_mock run` in the project root."
        assert api_online.json() == {"data": "Pong!"}
        
        # Set up test database for what code expects.
        start = timezone.now()
        User = get_user_model()
        user = User.objects.create_user(username="testuser", password="testpassword")
        course = Course.objects.create(name="Test")
        course.students.add(user)
        course.students.get()
        course_user = CourseUser.objects.get(user=user, course=course)
        course_user.gitlab_user_id = 1531 # User ID from mocked response.
        course_user.save()
        test_achievement = Achievement.objects.create(course=course, name="Single Award Fail", description="Test", rarity=AchievementRarity.COMMON, point_value=5)
        test_trigger = AchievementTrigger.objects.create(achievement=test_achievement, triggering_test_name="testStory", triggering_status=True) # Fails in mock
        test_trigger.save()
        test_achievement_another = Achievement.objects.create(course=course, name="Single Award Fail two", description="Test two", rarity=AchievementRarity.COMMON, point_value=5)
        old_achievement_toast = QueuedAchievementToast.objects.create(user=course_user, achievement=test_achievement_another, received_at=start - datetime.timedelta(days=100))

        # Now for actual test.
        pipeline_output = self.client.get("/gitlab/pipeline_output").content.decode()
        #print(pipeline_output)
        objectified_pipeline_output = json.loads(pipeline_output)
        #print(objectified_pipeline_output)
        response = self.client.post("/webhooks/gitlab/receive",
                                    HTTP_X_GITLAB_TOKEN="GitDeezNuts",
                                    HTTP_X_GITLAB_EVENT="Pipeline Hook",
                                    data = json.dumps(objectified_pipeline_output),
                                    content_type="application/json"
                                    )

        assert not course_user.achievements.filter(id=test_achievement.id).exists()        
        #assert course_user.achievements.get()
        
        #assert response.status_code  == HTTPStatus.OK
        #assert 


    

    # Depends on the flask endpoint running on port 5000
    def test_gitlab_webhook_single_test_award(self):
         # Ensure not user error.
        api_online = requests.get("http://localhost:5000/ping")
        assert api_online.status_code == HTTPStatus.OK, "Flask API unreachable. Ensure that the Flask API is running. You can do this by running `flask --app gitlab_mock run` in the project root."
        assert api_online.json() == {"data": "Pong!"}
        
        # Set up test database for what code expects.
        start = timezone.now()
        User = get_user_model()
        user = User.objects.create_user(username="testuser", password="testpassword")
        course = Course.objects.create(name="Test")
        course.students.add(user)
        course.students.get()
        course_user = CourseUser.objects.get(user=user, course=course)
        course_user.gitlab_user_id = 1531 # User ID from mocked response.
        course_user.save()
        test_achievement = Achievement.objects.create(course=course, name="Single Award Success", description="Test", rarity=AchievementRarity.COMMON, point_value=5)
        test_trigger = AchievementTrigger.objects.create(achievement=test_achievement, triggering_test_name="testComparison", triggering_status=True)
        test_trigger.save()
        test_achievement_another = Achievement.objects.create(course=course, name="Single Award Success two", description="Test two", rarity=AchievementRarity.COMMON, point_value=5)
        old_achievement_toast = QueuedAchievementToast.objects.create(user=course_user, achievement=test_achievement_another, received_at=start - datetime.timedelta(days=100))

        # Now for actual test.
        pipeline_output = self.client.get("/gitlab/pipeline_output").content.decode()
        #print(pipeline_output)
        objectified_pipeline_output = json.loads(pipeline_output)
        #print(objectified_pipeline_output)
        response = self.client.post("/webhooks/gitlab/receive",
                                    HTTP_X_GITLAB_TOKEN="GitDeezNuts",
                                    HTTP_X_GITLAB_EVENT="Pipeline Hook",
                                    data = json.dumps(objectified_pipeline_output),
                                    content_type="application/json"
                                    )

        assert course_user.achievements.filter(id=test_achievement.id).exists()        
        #assert course_user.achievements.get()
        
        #assert response.status_code  == HTTPStatus.OK
        #assert 



    
    


    def test_gitlab_webhook_multi_test_award_fail(self):

        # Ensure not user error.
        api_online = requests.get("http://localhost:5000/ping")
        assert api_online.status_code == HTTPStatus.OK, "Flask API unreachable. Ensure that the Flask API is running. You can do this by running `flask --app gitlab_mock run` in the project root."
        assert api_online.json() == {"data": "Pong!"}
        
        # Set up test database for what code expects.
        start = timezone.now()
        User = get_user_model()
        user = User.objects.create_user(username="testuser", password="testpassword")
        course = Course.objects.create(name="Test")
        course.students.add(user)
        course.students.get()
        course_user = CourseUser.objects.get(user=user, course=course)
        course_user.gitlab_user_id = 1531 # User ID from mocked response.
        course_user.save()
        test_achievement = Achievement.objects.create(course=course, name="Multi Award Fail", description="Test 2", rarity=AchievementRarity.COMMON, point_value=5)
        # This one is failing in mocked response
        test_trigger = AchievementTrigger.objects.create(achievement=test_achievement, triggering_test_name="testStory", triggering_status=True) # This one is failing in mocked response
        test_trigger.save()
        test_trigger2 = AchievementTrigger.objects.create(achievement=test_achievement, triggering_test_name="testComparison", triggering_status=True)
        test_trigger2.save()
        test_achievement_another = Achievement.objects.create(course=course, name="Test two", description="Test two", rarity=AchievementRarity.COMMON, point_value=5)
        old_achievement_toast = QueuedAchievementToast.objects.create(user=course_user, achievement=test_achievement_another, received_at=start - datetime.timedelta(days=100))

        # Now for actual test.
        pipeline_output = self.client.get("/gitlab/pipeline_output").content.decode()
        #print(pipeline_output)
        objectified_pipeline_output = json.loads(pipeline_output)
        #print(objectified_pipeline_output)
        response = self.client.post("/webhooks/gitlab/receive",
                                    HTTP_X_GITLAB_TOKEN="GitDeezNuts",
                                    HTTP_X_GITLAB_EVENT="Pipeline Hook",
                                    data = json.dumps(objectified_pipeline_output),
                                    content_type="application/json"
                                    )

        assert not course_user.achievements.filter(id=test_achievement.id).exists()        
        #assert course_user.achievements.get()
        
        #assert response.status_code  == HTTPStatus.OK
        #assert 


    def test_gitlab_webhook_multi_test_award_succeed(self):

        # Ensure not user error.
        api_online = requests.get("http://localhost:5000/ping")
        assert api_online.status_code == HTTPStatus.OK, "Flask API unreachable. Ensure that the Flask API is running. You can do this by running `flask --app gitlab_mock run` in the project root."
        assert api_online.json() == {"data": "Pong!"}
        
        # Set up test database for what code expects.
        start = timezone.now()
        User = get_user_model()
        user = User.objects.create_user(username="testuser", password="testpassword")
        course = Course.objects.create(name="Test")
        course.students.add(user)
        course.students.get()
        course_user = CourseUser.objects.get(user=user, course=course)
        course_user.gitlab_user_id = 1531 # User ID from mocked response.
        course_user.save()
        test_achievement = Achievement.objects.create(course=course, name="Multi Award Success", description="Test 2", rarity=AchievementRarity.COMMON, point_value=5)
        # This one is failing in mocked response
        test_trigger = AchievementTrigger.objects.create(achievement=test_achievement, triggering_test_name="testStory", triggering_status=False) # This one is failing in mocked response
        test_trigger.save()
        test_trigger2 = AchievementTrigger.objects.create(achievement=test_achievement, triggering_test_name="testComparison", triggering_status=True)
        test_trigger2.save()
        test_achievement_another = Achievement.objects.create(course=course, name="Test two", description="Test two", rarity=AchievementRarity.COMMON, point_value=5)
        old_achievement_toast = QueuedAchievementToast.objects.create(user=course_user, achievement=test_achievement_another, received_at=start - datetime.timedelta(days=100))

        # Now for actual test.
        pipeline_output = self.client.get("/gitlab/pipeline_output").content.decode() # This is because it's too much of a mess to have in here. Easier to just store as constant output out of sight
        #print(pipeline_output)
        objectified_pipeline_output = json.loads(pipeline_output)
        #print(objectified_pipeline_output)
        response = self.client.post("/webhooks/gitlab/receive",
                                    HTTP_X_GITLAB_TOKEN="GitDeezNuts",
                                    HTTP_X_GITLAB_EVENT="Pipeline Hook",
                                    data = json.dumps(objectified_pipeline_output),
                                    content_type="application/json"
                                    )

        assert course_user.achievements.filter(id=test_achievement.id).exists()        
        #assert course_user.achievements.get()
        
        #assert response.status_code  == HTTPStatus.OK
        #assert 


    def test_polling_endpoint_not_get(self):
        #print("polling test")
        response = self.client.post("/webhooks/poll_achievements/35") # Random User ID to prevent 404
        #print(response.status_code)
        #print(response.body)
        #print(response.status_code)
        assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED
        #assert response.content.decode() == json.dumps({"error": "Only GET requests allowed"})

 

    def test_polling_endpoint_wrong_token(self):
        response = self.client.get("/webhooks/poll_achievements/35", HTTP_ACHIEVEMENT_WEBHOOK_TOKEN="Hmph! How very glib! And do you believe in Eorzea?")
        assert response.status_code == HTTPStatus.FORBIDDEN
        assert (response.content.decode() == json.dumps({"error": "Incorrect Token"}))


    def test_polling_endpoint_wrong_user(self):
        response = self.client.get("/webhooks/poll_achievements/35", HTTP_ACHIEVEMENT_WEBHOOK_TOKEN="Tell me, for whom do you fight?")
        assert response.status_code == HTTPStatus.NOT_FOUND
        assert (response.content.decode() == json.dumps({"error": "User not found"}))
    

    def test_polling_endpoint_no_user(self):
        obj = {"eorzea": "Bruh"}
        serialized_obj = json.dumps(obj)
        response = self.client.get("/webhooks/poll_achievements/", HTTP_ACHIEVEMENT_WEBHOOK_TOKEN="Tell me, for whom do you fight?")
        #print(response.content.decode())
        assert response.status_code == HTTPStatus.NOT_FOUND
        #assert (response.content.decode() == json.dumps({"error": "Malformed JSON"}))


    def test_polling_endpoint_user_not_in_any_courses(self):
        obj = {"eorzea": "Bruh"}

        start = timezone.now()
        User = get_user_model()
        user = User.objects.create_user(username="testuser", password="testpassword")
        response = self.client.get("/webhooks/poll_achievements/{user_id}".format(user_id=user.id), 
                                   HTTP_ACHIEVEMENT_WEBHOOK_TOKEN="Tell me, for whom do you fight?",
                                   content_type="application/json")
        #print(response.content.decode())
        #print(response.content.decode())
        assert response.status_code == HTTPStatus.NOT_FOUND


    def test_polling_endpoint_success(self):
        obj = {"eorzea": "Bruh"}

        start = timezone.now()
        User = get_user_model()
        user = User.objects.create_user(username="testuser", password="testpassword")
        course = Course.objects.create(name="Test")
        course.students.add(user)
        course.students.get()
        course_user = CourseUser.objects.get(user=user, course=course)
        test_achievement = Achievement.objects.create(course=course, name="Test", description="Test", rarity=AchievementRarity.COMMON, point_value=5)
        response = self.client.post("/webhooks/achievement/award", 
                                    HTTP_ACHIEVEMENT_WEBHOOK_TOKEN="Tell me, for whom do you fight?", 
                                    content_type="application/json", 
                                    data={
                                        "id": test_achievement.id,
                                        "user": course_user.id
                                        }
                                    )
        
        
        assert response.status_code == HTTPStatus.OK
        assert response.content.decode() == "Achievement granted successfully"
        assert QueuedAchievementToast.objects.filter(user=course_user, achievement=test_achievement).exists()
        
        response = self.client.get("/webhooks/poll_achievements/{user_id}".format(user_id=user.id), 
                                   HTTP_ACHIEVEMENT_WEBHOOK_TOKEN="Tell me, for whom do you fight?",
                                   content_type="application/json")
        #print(response.content.decode())
        #print(response.content.decode())
        assert response.status_code == HTTPStatus.OK
        assert not QueuedAchievementToast.objects.filter(user=course_user).exists() # User should have no queued toasts afterwards
        #assert (response.content.decode() == json.dumps({"error": "Malformed JSON"}))
