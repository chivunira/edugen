# assessments/serializers.py
from rest_framework import serializers
from .models import Assessment, Question, StudentAnswer, AssessmentSummary


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = [
            'id',
            'question_text',
            'difficulty'
        ]


class AssessmentSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)
    topic_name = serializers.CharField(source='topic.name', read_only=True)
    topic_id = serializers.PrimaryKeyRelatedField(source='topic', read_only=True)

    class Meta:
        model = Assessment
        fields = [
            'id',
            'topic_id',
            'topic_name',
            'questions',
            'start_time',
            'status',
            'total_score'
        ]

    def to_representation(self, instance):
        # Add explicit validation of questions
        representation = super().to_representation(instance)
        questions = representation.get('questions', [])
        if not questions:
            raise serializers.ValidationError("Assessment must have questions attached")
        return representation


class StudentAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentAnswer
        fields = [
            'id',
            'question',
            'answer_text',
            'score',
            'feedback'
        ]


class AssessmentSummarySerializer(serializers.ModelSerializer):
    topic_name = serializers.CharField(source='topic.name', read_only=True)
    topic_id = serializers.PrimaryKeyRelatedField(source='topic', read_only=True)

    class Meta:
        model = AssessmentSummary
        fields = [
            'id',
            'topic_id',
            'topic_name',
            'total_attempts',
            'best_score',
            'last_score',
            'last_attempt_date',
            'average_score'
        ]