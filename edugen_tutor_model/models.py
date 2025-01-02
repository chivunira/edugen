from django.db import models
from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError


def validate_image_size(image):
    filesize = image.size
    megabyte_limit = 5.0
    if filesize > megabyte_limit*1024*1024:
        raise ValidationError("Max file size is %sMB" % str(megabyte_limit))


class Subject(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(
        upload_to='subjects/',
        validators=[validate_image_size],
        help_text="Upload a subject cover image (max 5MB)",
        blank=True,
        null=True
    )
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class Topic(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='topics')
    image = models.ImageField(
        upload_to='topics/',
        validators=[validate_image_size],
        help_text="Upload a topic cover image (max 5MB)",
        blank=True,
        null=True
    )
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order', 'name']

    def __str__(self):
        return f'{self.name} - {self.subject.name}'


class Chat(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    prompt = models.TextField()
    response = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.email} - {self.topic.name} - {self.timestamp}'