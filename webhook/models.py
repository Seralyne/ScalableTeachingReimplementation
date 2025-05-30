from django.db import models

# Create your models here.


class WebhookMessage(models.Model):
    received_at = models.DateTimeField(help_text="When the Webhook event was received")
    payload = models.JSONField(default=None,null=True)


    # Indexed because assumed clearing these out eventually. Helps with scalable performance, but isn't great for storage.
    class Meta:
        indexes = [
            models.Index(fields=["received_at"]),
        ]