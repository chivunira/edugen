# assessments/admin.py
from django.contrib import admin
from .models import Assessment, Question, StudentAnswer, AssessmentSummary

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('topic', 'question_text_preview', 'difficulty', 'is_active', 'created_at')
    list_filter = ('topic', 'difficulty', 'is_active')
    search_fields = ('question_text', 'model_answer', 'topic__name')
    ordering = ('topic', 'difficulty', '-created_at')
    readonly_fields = ('created_at', 'updated_at')

    def question_text_preview(self, obj):
        return obj.question_text[:50] + '...' if len(obj.question_text) > 50 else obj.question_text
    question_text_preview.short_description = 'Question'

    fieldsets = (
        ('Question Details', {
            'fields': ('topic', 'question_text', 'model_answer', 'difficulty')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'topic', 'start_time', 'end_time', 'total_score', 'status')
    list_filter = ('status', 'topic', 'start_time')
    search_fields = ('user__email', 'topic__name')
    ordering = ('-start_time',)
    readonly_fields = ('start_time', 'user')

    fieldsets = (
        ('Assessment Details', {
            'fields': ('user', 'topic', 'status')
        }),
        ('Results', {
            'fields': ('total_score', 'start_time', 'end_time')
        })
    )

@admin.register(StudentAnswer)
class StudentAnswerAdmin(admin.ModelAdmin):
    list_display = ('assessment', 'question_preview', 'score', 'submitted_at')
    list_filter = ('score', 'submitted_at')
    search_fields = ('assessment__user__email', 'question__question_text')
    ordering = ('-submitted_at',)
    readonly_fields = ('submitted_at',)

    def question_preview(self, obj):
        return obj.question.question_text[:50] + '...' if len(obj.question.question_text) > 50 else obj.question.question_text
    question_preview.short_description = 'Question'

    fieldsets = (
        ('Answer Details', {
            'fields': ('assessment', 'question', 'answer_text')
        }),
        ('Evaluation', {
            'fields': ('score', 'feedback')
        }),
        ('Timestamp', {
            'fields': ('submitted_at',),
            'classes': ('collapse',)
        })
    )

@admin.register(AssessmentSummary)
class AssessmentSummaryAdmin(admin.ModelAdmin):
    list_display = ('user', 'topic', 'total_attempts', 'best_score', 'last_score', 'last_attempt_date')
    list_filter = ('topic', 'last_attempt_date')
    search_fields = ('user__email', 'topic__name')
    ordering = ('-last_attempt_date',)

    fieldsets = (
        ('Summary Details', {
            'fields': ('user', 'topic', 'total_attempts')
        }),
        ('Scores', {
            'fields': ('best_score', 'last_score', 'average_score')
        }),
        ('Timestamps', {
            'fields': ('last_attempt_date',)
        })
    )