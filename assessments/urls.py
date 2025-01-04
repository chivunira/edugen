# assessments/urls.py
from django.urls import path
from .views import (
    StartAssessmentView,
    SubmitAnswerView,
    CompleteAssessmentView,
    AssessmentSummaryView,
    AssessmentResultView
)

urlpatterns = [
    # Start a new assessment for a topic
    path(
        '<int:topic_id>/start/',
        StartAssessmentView.as_view(),
        name='start-assessment'
    ),

    # Submit an answer for a question in an assessment
    path(
        '<int:assessment_id>/submit/',
        SubmitAnswerView.as_view(),
        name='submit-answer'
    ),

    # Complete an assessment and get results
    path(
        '<int:assessment_id>/complete/',
        CompleteAssessmentView.as_view(),
        name='complete-assessment'
    ),

    # Get assessment summary for a topic
    path(
        '<int:topic_id>/summary/',
        AssessmentSummaryView.as_view(),
        name='assessment-summary'
    ),

    # Get assessment review details
    path(
        '<int:assessment_id>/results/',
        AssessmentResultView.as_view(),
        name='assessment-results'
    ),
]