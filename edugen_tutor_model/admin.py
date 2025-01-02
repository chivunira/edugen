from django.contrib import admin
from .models import Subject, Topic, Chat

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'order', 'is_active')
    list_editable = ('order', 'is_active')
    search_fields = ('name', )


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ('name', 'subject', 'order', 'is_active')
    list_editable = ('order', 'is_active')
    list_filter = ('subject',)
    search_fields = ('name', 'subject__name')


@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = ('user', 'topic', 'timestamp')
    list_filter = ('user', 'topic', 'timestamp')
    search_fields = ('user__email', 'topic__name', 'prompt', 'response')

