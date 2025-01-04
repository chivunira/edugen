# assessments/models.py
from django.db import models
from django.conf import settings
from edugen_tutor_model.models import Topic


class Question(models.Model):
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]

    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    model_answer = models.TextField()
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default='medium')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['topic', 'difficulty', '-created_at']

    def __str__(self):
        return f"{self.topic.name} - {self.question_text[:50]}..."


class Assessment(models.Model):
    STATUS_CHOICES = [
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]

    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='assessments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    questions = models.ManyToManyField(Question, related_name='assessments')
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    total_score = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_progress')

    class Meta:
        ordering = ['-start_time']
        unique_together = ['topic', 'user', 'start_time']

    def __str__(self):
        return f"{self.user.email} - {self.topic.name} - {self.start_time}"



class StudentAnswer(models.Model):
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer_text = models.TextField()
    score = models.DecimalField(max_digits=3, decimal_places=2)  # 0.0 to 1.0
    feedback = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['assessment', 'submitted_at']
        unique_together = ['assessment', 'question']

    def __str__(self):
        return f"{self.assessment.user.email} - {self.question.question_text[:30]}..."


class AssessmentSummary(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    total_attempts = models.IntegerField(default=0)
    best_score = models.DecimalField(max_digits=5, decimal_places=2)
    last_score = models.DecimalField(max_digits=5, decimal_places=2)
    last_attempt_date = models.DateTimeField()
    average_score = models.DecimalField(max_digits=5, decimal_places=2)

    class Meta:
        ordering = ['-last_attempt_date']
        unique_together = ['user', 'topic']

    def __str__(self):
        return f"{self.user.email} - {self.topic.name} Summary"