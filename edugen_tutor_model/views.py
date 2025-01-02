from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from .models import Subject, Topic, Chat
from django.shortcuts import get_object_or_404
from .rag.combined_generator import generate_response_with_retrieval, generate_topic_overview
import os
from django.conf import settings

class SubjectListView(APIView):
    def get(self, request):
        subjects = Subject.objects.filter(is_active=True)
        data = []
        for subject in subjects:
            image_url = None
            if subject.image:
                image_url = request.build_absolute_uri(subject.image.url)
                print(f"Image URL for {subject.name}: {image_url}")  # Debug print

            subject_data = {
                'id': subject.id,
                'name': subject.name,
                'description': subject.description,
                'imageUrl': image_url,
                'topicCount': subject.topics.filter(is_active=True).count()
            }
            data.append(subject_data)

        print("Full response data:", data)  # Debug print
        return Response(data, status=HTTP_200_OK)


class TopicListView(APIView):
    def get(self, request, subject_id):
        subject = get_object_or_404(Subject, id=subject_id, is_active=True)
        topics = subject.topics.filter(is_active=True)

        subject_data = {
            'id': subject.id,
            'name': subject.name,
            'description': subject.description,
            'imageUrl': request.build_absolute_uri(subject.image.url) if subject.image else None
        }

        topics_data = [{
            'id': topic.id,
            'name': topic.name,
            'description': topic.description,
            'imageUrl': request.build_absolute_uri(topic.image.url) if topic.image else None,
            'subjectId': subject.id
        } for topic in topics]

        return Response({
            'subject': subject_data,
            'topics': topics_data
        }, status=HTTP_200_OK)


class ChatView(APIView):
    def post(self, request, topic_id):
        try:
            user = request.user
            topic = get_object_or_404(Topic, id=topic_id)

            # Log the incoming request data for debugging
            print("Received request data:", request.data)

            prompt = request.data.get('prompt', '')
            is_initial_overview = request.data.get('isInitialOverview', False)

            # Use default paths relative to your project
            BASE_DIR = settings.BASE_DIR
            faiss_index_path = os.path.join(BASE_DIR, 'edugen_tutor_model', 'rag_preprocessing', 'faiss_index')
            corpus_path = os.path.join(BASE_DIR, 'edugen_tutor_model', 'rag_preprocessing', 'corpus.csv')

            # Check if files exist
            if not os.path.exists(faiss_index_path) or not os.path.exists(corpus_path):
                print(
                    f"Missing required files:\nFAISS Index exists: {os.path.exists(faiss_index_path)}\nCorpus exists: {os.path.exists(corpus_path)}")
                return Response({
                    'error': 'Required model files not found. Please check server configuration.'
                }, status=HTTP_400_BAD_REQUEST)

            if not prompt and not is_initial_overview:
                return Response({
                    'error': 'Prompt is required for non-overview messages.'
                }, status=HTTP_400_BAD_REQUEST)

            try:
                if is_initial_overview:
                    response = generate_topic_overview(topic.name, faiss_index_path, corpus_path)
                    prompt = f"Hi, this is my first lesson and I'm super excited to be here, Give me an overview of {topic.name}"
                else:
                    response = generate_response_with_retrieval(
                        prompt,
                        faiss_index_path,
                        corpus_path,
                        topic_name=topic.name
                    )

                # Save chat history
                chat = Chat.objects.create(
                    user=user,
                    topic=topic,
                    prompt=prompt,
                    response=response
                )

                return Response({
                    'id': chat.id,
                    'prompt': prompt,
                    'response': response,
                    'timestamp': chat.timestamp.isoformat()  # Format timestamp
                }, status=HTTP_200_OK)

            except Exception as e:
                print(f"Error generating response: {str(e)}")  # Add logging
                return Response({
                    'error': f'Error generating response: {str(e)}'
                }, status=HTTP_400_BAD_REQUEST)

        except Exception as e:
            print(f"General error in ChatView: {str(e)}")  # Add logging
            return Response({
                'error': f'An error occurred: {str(e)}'
            }, status=HTTP_400_BAD_REQUEST)


class ChatHistoryView(APIView):
    def get(self, request, topic_id):
        user = request.user
        topic = get_object_or_404(Topic, id=topic_id)
        chats = Chat.objects.filter(user=user, topic=topic).order_by('timestamp')
        data = [{
            'id': chat.id,
            'prompt': chat.prompt,
            'response': chat.response,
            'timestamp': chat.timestamp
        } for chat in chats]
        return Response(data, status=HTTP_200_OK)


class TopicDetailView(APIView):
    """
    View to get detailed information on specific topic
    """
    def get(self, request, topic_id):
        topic = get_object_or_404(Topic, id=topic_id, is_active=True)
        topic_data = {
            'id': topic.id,
            'name': topic.name,
            'description': topic.description,
            'imageUrl': request.build_absolute_uri(topic.image.url) if topic.image else None,
            'subjectId': topic.subject.id,
            'subjectName': topic.subject.name,
            'is_active': topic.is_active,
            'order': topic.order
        }
        return Response(topic_data, status=HTTP_200_OK)