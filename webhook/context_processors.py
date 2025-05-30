from django.conf import settings

def achievement_webhook_token(request):
    return {
        'ACHIEVEMENT_WEBHOOK_TOKEN': settings.ACHIEVEMENT_WEBHOOK_TOKEN
    }