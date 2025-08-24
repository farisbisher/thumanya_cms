from django.db import models

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Program(models.Model):
    MEDIA_TYPES = (
        ("podcast", "Podcast"),
        ("documentary", "Documentary"),
        ("show", "Show"),
        ("other", "Other"),
    )

    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name="programs")
    language = models.CharField(max_length=50)
    duration = models.DurationField()
    publish_date = models.DateField()
    media_type = models.CharField(max_length=20, choices=MEDIA_TYPES, default="other")

    media_url = models.URLField(help_text="Direct link to the media (e.g., YouTube video)")

    thumbnail_url = models.URLField(blank=True, null=True, help_text="Optional: link to program thumbnail/cover")

    metadata = models.JSONField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
