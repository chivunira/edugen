from django.urls import path
from .views import SubjectListView, TopicListView, ChatHistoryView, ChatView, TopicDetailView

urlpatterns = [
    path('subjects/', SubjectListView.as_view(), name='subject-list'),
    path('topics/<int:subject_id>/', TopicListView.as_view(), name='topic-list'),
    path('topics/detail/<int:topic_id>/', TopicDetailView.as_view(), name='topic-detail'),
    path('chat/<int:topic_id>/', ChatHistoryView.as_view(), name='chat-history'),
    path('chat/<int:topic_id>/post/', ChatView.as_view(), name='chat'),
]