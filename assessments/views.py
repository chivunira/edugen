# assessments/views.py
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db import transaction
from .models import Assessment, Question, StudentAnswer, AssessmentSummary
from .serializers import (
    AssessmentSerializer,
    StudentAnswerSerializer,
    AssessmentSummarySerializer
)
from edugen_tutor_model.models import Topic
from openai import OpenAI
import os
import logging
import re
import json

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

logger = logging.getLogger(__name__)


class StartAssessmentView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request, topic_id):
        try:
            # Log the start of the process
            logger.info(f"Starting assessment for topic {topic_id} by user {request.user.id}")

            # Get active questions first to ensure they exist
            available_questions = Question.objects.filter(
                topic_id=topic_id,
                is_active=True
            )

            # Log available questions
            logger.info(f"Found {available_questions.count()} available questions for topic {topic_id}")

            if not available_questions.exists():
                logger.error(f"No active questions found for topic {topic_id}")
                return Response(
                    {'error': 'No questions available for this topic'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Get 5 random questions
            selected_questions = list(available_questions.order_by('?')[:5])
            logger.info(f"Selected {len(selected_questions)} questions for the assessment")

            # Create assessment with explicit transaction
            assessment = Assessment.objects.create(
                topic_id=topic_id,
                user=request.user,
                status='in_progress'
            )

            # Explicitly attach questions
            assessment.questions.add(*selected_questions)

            # Verify questions were attached
            question_count = assessment.questions.count()
            logger.info(f"Attached {question_count} questions to assessment {assessment.id}")

            if question_count == 0:
                logger.error(f"Failed to attach questions to assessment {assessment.id}")
                raise ValueError("Failed to attach questions to assessment")

            # Re-fetch the assessment to ensure we have the latest data
            assessment.refresh_from_db()

            # Serialize and verify response
            serializer = AssessmentSerializer(assessment)
            response_data = serializer.data

            # Verify serialized data
            if not response_data.get('questions'):
                logger.error(f"Questions missing from serialized data for assessment {assessment.id}")
                logger.error(f"Serialized data: {response_data}")
                raise ValueError("Assessment serialization failed - missing questions")

            logger.info(
                f"Successfully created assessment {assessment.id} with {len(response_data['questions'])} questions")
            return Response(response_data)

        except Exception as e:
            logger.error(f"Error in StartAssessmentView: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SubmitAnswerView(APIView):
    permission_classes = [IsAuthenticated]

    def extract_json_from_response(self, content):
        """
        Extracts JSON from GPT response, handling various response formats.
        """
        # Try to find JSON content within markdown code blocks
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', content, re.DOTALL)
        if json_match:
            content = json_match.group(1)

        # Clean up the content and try to parse it
        try:
            # Remove any remaining markdown or unwanted characters
            content = re.sub(r'```.*?```', '', content, flags=re.DOTALL)
            content = content.strip()
            return json.loads(content)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from content: {content}")
            raise ValueError(f"Invalid JSON response from GPT: {str(e)}")

    def post(self, request, assessment_id):
        try:
            # Log the incoming request
            logger.info(f"Processing answer submission for assessment {assessment_id}")

            assessment = Assessment.objects.get(
                id=assessment_id,
                user=request.user,
                status='in_progress'
            )

            question_id = request.data.get('questionId')
            answer_text = request.data.get('answer')

            if not question_id or not answer_text:
                return Response(
                    {'error': 'Question ID and answer are required'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            question = Question.objects.get(id=question_id)

            # Format the prompt for GPT-4
            prompt = f"""
            You are evaluating a Grade 6 student's answer to a science question.
            Remember these key guidelines:
            
            1. Evaluation Process:
               - First, analyze the model answer to identify:
                  * Core concepts that must be understood
                  * Key supporting details that enhance understanding
                  * Alternative valid explanations or approaches
               - Then, compare the student's answer to identify:
                  * Whether they've grasped the core concepts, even if expressed differently
                  * Which key points they've included, even if phrased simply
                  * Any valid alternatives they've provided that aren't in the model answer

            2. Scoring Guidelines:
               - 1.0 (100%): 
                  * Shows clear understanding of core concepts from the model answer
                  * May use different but valid examples or explanations
                  * Doesn't need to match the model answer word-for-word
               - 0.75 (75%):
                  * Demonstrates understanding of main concepts
                  * Might miss some supporting details
                  * Uses correct but simplified explanations
               - 0.5 (50%):
                  * Shows partial understanding
                  * Misses significant details but has some correct points
               - 0.0 (0%):
                  * Completely incorrect or irrelevant
        
                3. Consider that students may:
                   - Use simple language but still demonstrate understanding
                   - Give partial answers that are technically correct
                   - Miss some details while grasping the main concept

            Question: {question.question_text}
            Model Answer: {question.model_answer}
            Student's Answer: {answer_text}

            Evaluate the answer considering the student's grade level and provide:
            1. A score that reflects understanding, not just completeness
            2. Specific, encouraging feedback that:
               - Acknowledges what they got right
               - Suggests what could be added
               - Provides an example or hint for improvement
               - Uses grade-appropriate language

            Return ONLY a JSON object in this exact format, with no other text:
            {{
                "score": (number between 0 and 1),
                "feedback": "your feedback here"
            }}
            """

            # Get GPT-4 evaluation
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
            )

            # Extract and parse the response
            gpt_response = response.choices[0].message.content
            logger.debug(f"GPT Response: {gpt_response}")

            try:
                evaluation = self.extract_json_from_response(gpt_response)
            except ValueError as e:
                logger.error(f"Failed to parse GPT response: {str(e)}")
                return Response(
                    {'error': 'Invalid response format from evaluation system'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            # Validate the evaluation structure
            if not isinstance(evaluation, dict) or 'score' not in evaluation or 'feedback' not in evaluation:
                logger.error(f"Invalid evaluation structure: {evaluation}")
                return Response(
                    {'error': 'Invalid evaluation format'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            # Create the student answer record
            student_answer = StudentAnswer.objects.create(
                assessment=assessment,
                question=question,
                answer_text=answer_text,
                score=float(evaluation['score']),
                feedback=evaluation['feedback']
            )

            return Response({
                'isCorrect': float(evaluation['score']) == 1.0,
                'score': float(evaluation['score']) * 100,
                'feedback': evaluation['feedback']
            })

        except Assessment.DoesNotExist:
            return Response(
                {'error': 'Assessment not found or already completed'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Question.DoesNotExist:
            return Response(
                {'error': 'Question not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error processing answer submission: {str(e)}")
            return Response(
                {'error': 'Failed to process answer submission'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CompleteAssessmentView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request, assessment_id):
        try:
            assessment = Assessment.objects.get(
                id=assessment_id,
                user=request.user,
                status='in_progress'
            )

            # Calculate total score
            answers = StudentAnswer.objects.filter(assessment=assessment)
            total_score = sum(answer.score for answer in answers) / answers.count() * 100

            # Update assessment
            assessment.status = 'completed'
            assessment.end_time = timezone.now()
            assessment.total_score = total_score
            assessment.save()

            # Update or create assessment summary
            summary, created = AssessmentSummary.objects.get_or_create(
                user=request.user,
                topic=assessment.topic,
                defaults={
                    'total_attempts': 1,
                    'best_score': total_score,
                    'last_score': total_score,
                    'last_attempt_date': timezone.now(),
                    'average_score': total_score
                }
            )

            if not created:
                summary.total_attempts += 1
                summary.best_score = max(summary.best_score, total_score)
                summary.last_score = total_score
                summary.last_attempt_date = timezone.now()
                summary.average_score = (
                        (summary.average_score * (summary.total_attempts - 1) + total_score) /
                        summary.total_attempts
                )
                summary.save()

            return Response({
                'assessmentId': assessment.id,
                'topicId': assessment.topic.id,
                'score': total_score,
                'completedAt': assessment.end_time,
                'questionResults': [{
                    'questionId': answer.question.id,
                    'score': answer.score * 100,
                    'isCorrect': answer.score == 1.0,
                    'userAnswer': answer.answer_text,
                    'feedback': answer.feedback
                } for answer in answers]
            })

        except Assessment.DoesNotExist:
            return Response(
                {'error': 'Assessment not found or already completed'},
                status=status.HTTP_404_NOT_FOUND
            )


class AssessmentSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, topic_id):
        try:
            # Try to get existing summary
            summary = AssessmentSummary.objects.get(
                user=request.user,
                topic_id=topic_id
            )
            serializer = AssessmentSummarySerializer(summary)
            return Response(serializer.data)
        except AssessmentSummary.DoesNotExist:
            # Return empty summary instead of 404
            return Response({
                'topic_id': topic_id,
                'total_attempts': 0,
                'best_score': 0,
                'last_score': 0,
                'average_score': 0,
                'last_attempt_date': None
            })


class AssessmentResultView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, assessment_id):
        try:
            # Get the assessment and verify ownership
            assessment = Assessment.objects.get(
                id=assessment_id,
                user=request.user,
                status='completed'
            )

            # Get all answers for this assessment
            answers = StudentAnswer.objects.filter(assessment=assessment)

            return Response({
                'assessmentId': assessment.id,
                'topicId': assessment.topic.id,
                'score': float(assessment.total_score),
                'completedAt': assessment.end_time,
                'questionResults': [{
                    'questionId': answer.question.id,
                    'questionText': answer.question.question_text,
                    'score': float(answer.score) * 100,
                    'isCorrect': float(answer.score) == 1.0,
                    'userAnswer': answer.answer_text,
                    'feedback': answer.feedback
                } for answer in answers]
            })

        except Assessment.DoesNotExist:
            return Response(
                {'error': 'Assessment not found or not completed'},
                status=status.HTTP_404_NOT_FOUND
            )