from rest_framework import viewsets, status
from .permissions import IsChannelMemberOrReadOnly
from .models import Video, Transcript, VideoSegment, City, Participant, Monument, Topic, ImportantPerson
from .serializers import VideoSerializer, TranscriptSerializer, VideoSegmentSerializer,ParticipantSerializer,VideoPageSerializer, MonumentSerializer, CitySerializer,TopicSerializer,ImportantPersonSerializer
from rest_framework.response import Response
from rest_framework.decorators import action
from datetime import datetime
from rest_framework.permissions import AllowAny, IsAuthenticated
from ..media.services import create_media_with_category
from django.db import transaction
from .services import create_or_get_city, create_or_get_monument
from .utils import create_or_get_important_person,create_or_get_topic
from rest_framework.pagination import PageNumberPagination
from ..playlist.models import Playlist, PlaylistMedia
import json

class VideoPageViewSet(viewsets.ModelViewSet):
    serializer_class = VideoPageSerializer
    queryset = Video.objects.all()
    permission_classes = [AllowAny]


class VideoViewSet(viewsets.ModelViewSet):
    queryset = Video.objects.all()
    serializer_class = VideoSerializer

    def get_permissions(self):
        if self.action == 'create_complex_video':
            return [IsChannelMemberOrReadOnly()]
        return [IsAuthenticated()]

    @action(detail=False, methods=['post'], url_path='create-complex-video')
    def create_complex_video(self, request, *args, **kwargs):
        with transaction.atomic(): 
            try:
                print("before try",request.data)
                video_data = json.loads(request.data.get('video', '{}'))
                participants = json.loads(request.data.get('participants', '[]'))
                transcript_data = json.loads(request.data.get('transcript', '{}'))
                segments_with_transcripts = json.loads(request.data.get('segments', '[]'))
                
                media_data = video_data.get('mediaID', {})
                city_data = video_data.get('city',{})
                monument_data = video_data.get('monument',{})
                topics_data = video_data.get('topics', []) 
                important_persons_data = video_data.get('important_persons', [])
                monument_image = request.FILES.get('monument_image')
                city_image = request.FILES.get('city_image')
                playlist_id = request.data.get('playlist','')  

                if city_data:
                    city_data['city_image']=city_image
                    city, city_error = create_or_get_city(city_data)
                    if city_error:
                        raise ValueError("City creation/retrieval failed", city_error)
                    video_data['city'] = city.id
                    video_data['monument'] = None
                elif monument_data:
                    monument_data['monument_image']=monument_image
                    monument, monument_error = create_or_get_monument(monument_data)
                    if monument_error:
                        raise ValueError("Monument creation/retrieval failed", monument_error)
                    video_data['monument'] = monument.id
                    video_data['city'] = None
                else:
                    raise ValueError("Either a city or monument must be provided.")


                media_data['uploaderID'] = request.user.id

                media, media_errors = create_media_with_category(media_data, media_data.get('categoryID'))
                if media_errors:  
                    raise ValueError("Media creation failed", media_errors)

                video_data['mediaID'] = media.id
                
                topic_objects = []
                for topic_name in topics_data:
                    topic, topic_error = create_or_get_topic(topic_name)
                    if topic_error:
                        raise ValueError("Topic creation/retrieval failed", topic_error)
                    topic_objects.append(topic)

                important_person_objects = []
                for person_name in important_persons_data:
                    person, person_error = create_or_get_important_person(person_name)
                    if person_error:
                        raise ValueError("Important person creation/retrieval failed", person_error)
                    important_person_objects.append(person)

                
                video_serializer = VideoSerializer(data=video_data)

                if not video_serializer.is_valid():
                    raise ValueError("Video data validation failed", video_serializer.errors)

                video = video_serializer.save()
                
                video.topics.set(topic_objects)
                video.important_persons.set(important_person_objects)

                
                participant_errors = []

                for participant in participants:
                    participant['VideoId'] = video.id
                    participant_serializer = ParticipantSerializer(data=participant)

                    if participant_serializer.is_valid():                        
                        participant_serializer.save()
                    else:
                        participant_errors.append(participant_serializer.errors)

                if participant_errors:
                    raise ValueError("Participant data validation failed", participant_errors) 
                segn=0
                print("before seg")
                for segment_data in segments_with_transcripts:
                    # Create segment
                    print("before seg loop",segment_data)
                    segment_data['videoSegmentID'] = segn
                    segment_data['VideoID'] = video.id
                    segment_serializer = VideoSegmentSerializer(data=segment_data)
                    if segment_serializer.is_valid():
                        segment = segment_serializer.save()
                        segn+=1
                    else:
                        raise ValueError("Segment data validation failed", segment_serializer.errors)
                    print("wst loop")
                    # Create transcript for segment
                    transcriptseg__data = segment_data.get('transcript', [])
                    print("adter data",transcriptseg__data)
                    if transcriptseg__data:
                        transcription = transcriptseg__data.get('transcription', '')
                        transcription_language = transcriptseg__data.get('transcriptionLanguage', '')
                        
                        # Check if both fields are filled
                        if transcription and transcription_language:
                            transcriptseg__data.update({
                                'videoID': video.id,
                                'videoSegmentID': segment.id,
                            })
                            transcript_serializer = TranscriptSerializer(data=transcriptseg__data)
                            if transcript_serializer.is_valid():
                                transcript_serializer.save()
                            else:
                                raise ValueError("Transcript data validation failed", transcript_serializer.errors)

                print("after seg")
                if transcript_data.get('transcription'):
                    transcript_data['videoID'] = video.id
                    transcript_data['videoSegmentID'] = None
                    full_transcript_serializer = TranscriptSerializer(data=transcript_data)
                    if full_transcript_serializer.is_valid():
                        full_transcript_serializer.save()
                    else:
                        raise ValueError("Transcript data validation failed", full_transcript_serializer.errors)

                if playlist_id:
                    try:
                        playlist = Playlist.objects.get(id=playlist_id)

                        PlaylistMedia.objects.create(
                            playlist=playlist,
                            media=media,
                            added_by=request.user
                        )                    
                    except Playlist.DoesNotExist:
                        raise ValueError("Specified playlist does not exist")

                return Response(video_serializer.data, status=status.HTTP_201_CREATED)
            

            except ValueError as e:
                transaction.set_rollback(True)
                return Response(str(e), status=status.HTTP_400_BAD_REQUEST)
   
    @action(detail=False, methods=['get'])
    def get_channel_videos(self, request):
        channel_id = request.query_params.get('channel_id')
        if not channel_id:
            return Response({"error": "channel_id is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        videos = self.queryset.filter(mediaID__channelID=channel_id)

        # Apply pagination
        paginator = PageNumberPagination()
        paginated_videos = paginator.paginate_queryset(videos, request)

        serializer = VideoSerializer(paginated_videos, many=True)

        # Return paginated response
        return paginator.get_paginated_response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated], url_path='videos-by-city/(?P<city_name>[^/.]+)')
    def get_videos_by_city(self, request, city_name=None, *args, **kwargs):
        if not city_name:
            return Response({"error": "city_name parameter is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Fetch the city object
            city = City.objects.get(city_name=city_name)

            # Get videos either directly linked to the city or via monuments
            videos = Video.objects.filter(city=city) | Video.objects.filter(monument__city=city)

            # Prepare a list of video data
            video_list = []
            for video in videos:
                video_data = {
                    "title": video.mediaID.title,
                    "interviewees": [f"{participant.firstName} {participant.lastName}" for participant in video.participants.filter(role=Participant.INTERVIEWEE)],
                    "interviewers": [f"{participant.firstName} {participant.lastName}" for participant in video.participants.filter(role=Participant.INTERVIEWER)],
                    "monument": video.monument.monument_name if video.monument else None,
                    "monument_image": video.monument.monument_image.url if video.monument and video.monument.monument_image else None
                }
                video_list.append(video_data)

            # Create the response object
            response = {
                "city_name": city.city_name,
                "videos": video_list
            }
            return Response(response, status=status.HTTP_200_OK)

        except City.DoesNotExist:
            return Response({"error": "City not found."}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated], url_path='cities-with-videos')
    def get_video_cities(self, request):
        cities = City.objects.filter(videos__isnull=False).distinct() | City.objects.filter(monuments__videos__isnull=False).distinct()
        
        city_list = []

        for city in cities:
            monuments_with_videos = city.monuments.filter(videos__isnull=False).distinct()
            monument_data = [{
                "monument_name": monument.monument_name,
                "monument_image": monument.monument_image.url if monument.monument_image else None
            } for monument in monuments_with_videos]

            city_list.append({
                "city_name": city.city_name,
                "city_image": city.city_image.url if city.city_image else None,
                "monuments": monument_data
            })

        return Response({"cities": city_list}, status=status.HTTP_200_OK)



class ParticipantViewSet(viewsets.ModelViewSet):
    queryset = Participant.objects.all()
    serializer_class = ParticipantSerializer

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def add_participant(self, request):
        video_id = request.data.get('video_id')
        participants_data = request.data.get('participants', [])

        if not video_id:
            return Response({"error": "video_id is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            video = Video.objects.get(pk=video_id)
        except Video.DoesNotExist:
            return Response({"error": "Video not found"}, status=status.HTTP_404_NOT_FOUND)

        if not isinstance(participants_data, list):
            return Response({"error": "Participants data must be a list."}, status=status.HTTP_400_BAD_REQUEST)

        errors = []
        for participant_data in participants_data:
            participant_data['VideoId'] = video_id  # Set VideoId field with provided video_id
            serializer = ParticipantSerializer(data=participant_data)
            if serializer.is_valid():
                serializer.save()
            else:
                errors.append(serializer.errors)

        if errors:
            return Response({"errors": errors}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"message": "Participants added successfully"}, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def retrieve_by_role(self, request):
        role = request.query_params.get('role')
        video_id = request.query_params.get('video_id')

        if not role or not video_id:
            return Response({"error": "Both role and video_id parameters are required."}, status=status.HTTP_400_BAD_REQUEST)

        participants = self.queryset.filter(role=role, VideoId=video_id)
        serializer = ParticipantSerializer(participants, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class VideoSegmentViewSet(viewsets.ModelViewSet):
    queryset = VideoSegment.objects.all()
    serializer_class = VideoSegmentSerializer

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def create_video_segment(self, request):
        print("huh")
        try:
            video_id = request.data.get('video_id')
            video = Video.objects.get(pk=video_id)
        except Video.DoesNotExist:
            return Response({"error": "Video not found"}, status=status.HTTP_404_NOT_FOUND)
        
        segments_data = request.data.get('segments', [])
        existing_segment_numbers = set(VideoSegment.objects.filter(VideoID=video_id).values_list('segmentNumber', flat=True))
        seen_segment_numbers = set()
        
        for segment_data in segments_data:
            segment_number = segment_data.get('segmentNumber')
            if VideoSegment.objects.filter(VideoID=video.id, segmentNumber=segment_number).exists():
                return Response({"error": f"A segment with segmentNumber {segment_number} already exists for this video."},
                                status=status.HTTP_400_BAD_REQUEST)
            if segment_number in seen_segment_numbers:
                return Response({"error": f"Duplicate segmentNumber '{segment_number}' found in the request."},
                                status=status.HTTP_400_BAD_REQUEST)
            
            seen_segment_numbers.add(segment_number)
            segment_data['VideoID'] = video.id
        
        serializer = VideoSegmentSerializer(data=segments_data, many=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Video segments added successfully"}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def get_segments(self, request):
        video_id = request.query_params.get('video_id')
        if not video_id:
            return Response({"error": "video_id is required."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            video = Video.objects.get(pk=video_id)
        except Video.DoesNotExist:
            return Response({"error": "Video not found"}, status=status.HTTP_404_NOT_FOUND)
        segments = VideoSegment.objects.filter(VideoID=video_id)
        serializer = VideoSegmentSerializer(segments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class TranscriptViewSet(viewsets.ModelViewSet):
    queryset = Transcript.objects.all()
    serializer_class = TranscriptSerializer

    @action(detail=False, methods=['post'])
    def create_transcripts(self, request):
        try:
            video_id = request.data.get('video_id')
            video = Video.objects.get(pk=video_id)
        except Video.DoesNotExist:
            return Response({"error": "Video not found"}, status=status.HTTP_404_NOT_FOUND)

        transcripts_data = request.data.get('transcripts', [])
        prepared_transcripts = []

        for transcript_data in transcripts_data:
            segment_number = transcript_data.get('segmentNumber')
            try:
                video_segment = VideoSegment.objects.get(VideoID=video.id, segmentNumber=segment_number)
            except VideoSegment.DoesNotExist:
                return Response(
                    {"error": f"Segment number '{segment_number}' does not exist for this video."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            prepared_transcript = {
                'videoID': video.id,
                'videoSegmentID': video_segment.id,
                'title': transcript_data.get('title'),
                'content': transcript_data.get('content'),
                'transcriberID': request.user.id,  # Assuming user is authenticated
                'transcriptDate': datetime.now(),  # Set the current date and time
                'transcription': transcript_data.get('transcription'),
                'transcriptionLanguage': transcript_data.get('transcriptionLanguage'),
            }
            prepared_transcripts.append(prepared_transcript)

        serializer = TranscriptSerializer(data=prepared_transcripts, many=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Transcripts added successfully"}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def get_transcripts(self, request, pk=None):
        try:
            video = Video.objects.get(pk=pk)
        except Video.DoesNotExist:
            return Response({"error": "Video not found"}, status=status.HTTP_404_NOT_FOUND)

        transcripts = Transcript.objects.filter(videoID=video)
        print("they got hrt",transcripts)

        transcripts_by_language = {}

        for transcript in transcripts:
            language = transcript.transcriptionLanguage
            
            if language not in transcripts_by_language:
                transcripts_by_language[language] = []

            transcripts_by_language[language].append(TranscriptSerializer(transcript).data)

        return Response(transcripts_by_language, status=status.HTTP_200_OK)

class ComplexSegmentViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def create_complex_segment(self, request):
        video_id = request.data.get('video_id')
        segments_data = request.data.get('segments', [])
        transcripts_data = request.data.get('transcripts', [])

        try:
            video = Video.objects.get(pk=video_id)
        except Video.DoesNotExist:
            return Response({"error": "Video not found"}, status=status.HTTP_404_NOT_FOUND)

        if not isinstance(segments_data, list) or not isinstance(transcripts_data, list):
            return Response({"error": "Both segments and transcripts data must be lists."},
                            status=status.HTTP_400_BAD_REQUEST)

        seen_segment_numbers = set()
        for segment_data in segments_data:
            segment_number = segment_data.get('segmentNumber')
            if VideoSegment.objects.filter(VideoID=video.id, segmentNumber=segment_number).exists():
                return Response({"error": f"A segment with segmentNumber {segment_number} already exists for this video."},
                                status=status.HTTP_400_BAD_REQUEST)

            if segment_number in seen_segment_numbers:
                return Response({"error": f"Duplicate segmentNumber '{segment_number}' found in the request."},
                                status=status.HTTP_400_BAD_REQUEST)

            seen_segment_numbers.add(segment_number)
            segment_data['VideoID'] = video.id

        segment_serializer = VideoSegmentSerializer(data=segments_data, many=True)
        if segment_serializer.is_valid():
            segment_serializer.save()
            created_segments = segment_serializer.data
        else:
            return Response(segment_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        prepared_transcripts = []
        for transcript_data in transcripts_data:
            segment_number = transcript_data.get('segmentNumber')

            try:
                video_segment = VideoSegment.objects.get(VideoID=video.id, segmentNumber=segment_number)
            except VideoSegment.DoesNotExist:
                return Response(
                    {"error": f"Segment number '{segment_number}' does not exist for this video."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            prepared_transcript = {
                'videoID': video.id,
                'videoSegmentID': video_segment.id,
                'title': transcript_data.get('title'),
                'content': transcript_data.get('content'),
                'transcriberID': request.user.id,  # Assuming user is authenticated
                'transcriptDate': datetime.now(),  # Set the current date and time
                'transcription': transcript_data.get('transcription'),
                'transcriptionLanguage': transcript_data.get('transcriptionLanguage'),
            }
            prepared_transcripts.append(prepared_transcript)

        transcript_serializer = TranscriptSerializer(data=prepared_transcripts, many=True)
        if transcript_serializer.is_valid():
            transcript_serializer.save()
            created_transcripts = transcript_serializer.data
        else:
            return Response(transcript_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response({"message": "Segments and transcripts added successfully"}, status=status.HTTP_201_CREATED)

class complexSegementViewSet(viewsets.ModelViewSet):
    queryset = VideoSegment.objects.all()
    serializer_class = VideoSegmentSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'], url_path='create-segments-and-transcripts')
    def create_segments_and_transcripts(self, request):
        # Extract video_id from request body
        video_id = request.data.get('video_id')
        if not video_id:
            return Response({"error": "video_id is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            video = Video.objects.get(pk=video_id)
        except Video.DoesNotExist:
            return Response({"error": "Video not found"}, status=status.HTTP_404_NOT_FOUND)

        segments_data = request.data.get('segments', [])
        transcripts_data = request.data.get('transcripts', [])

        with transaction.atomic():  # Start of transaction block
            # Create video segments
            created_segments = []
            existing_segment_numbers = set(VideoSegment.objects.filter(VideoID=video_id).values_list('segmentNumber', flat=True))
            seen_segment_numbers = set()

            for segment_data in segments_data:
                segment_number = segment_data.get('segmentNumber')

                if VideoSegment.objects.filter(VideoID=video_id, segmentNumber=segment_number).exists():
                    return Response({"error": f"A segment with segmentNumber {segment_number} already exists for this video."},
                                    status=status.HTTP_400_BAD_REQUEST)
                elif segment_number in seen_segment_numbers:
                    return Response({"error": f"Duplicate segmentNumber '{segment_number}' found in the request."},
                                    status=status.HTTP_400_BAD_REQUEST)
                else:
                    segment_data['VideoID'] = video_id
                    created_segments.append(segment_data)
                    seen_segment_numbers.add(segment_number)

            serializer_segment = VideoSegmentSerializer(data=created_segments, many=True)
            if serializer_segment.is_valid():
                serializer_segment.save()
            else:
                return Response(serializer_segment.errors, status=status.HTTP_400_BAD_REQUEST)

            # Create transcripts for segments
            created_transcripts = []
            for transcript_data in transcripts_data:
                segment_number = transcript_data.get('segmentNumber')

                try:
                    video_segment = VideoSegment.objects.get(VideoID=video_id, segmentNumber=segment_number)
                except VideoSegment.DoesNotExist:
                    return Response({"error": f"Segment number '{segment_number}' does not exist for this video."},
                                    status=status.HTTP_400_BAD_REQUEST)

                prepared_transcript = {
                    'videoID': video_id,
                    'videoSegmentID': video_segment.id,
                    'title': transcript_data.get('title'),
                    'content': transcript_data.get('content'),
                    'transcriberID': request.user.id,  # Assuming user is authenticated
                    'transcriptDate': datetime.now(),  # Set the current date and time
                    'transcription': transcript_data.get('transcription'),
                    'transcriptionLanguage': transcript_data.get('transcriptionLanguage'),
                }
                created_transcripts.append(prepared_transcript)

            serializer_transcript = TranscriptSerializer(data=created_transcripts, many=True)
            if serializer_transcript.is_valid():
                serializer_transcript.save()
                return Response({"message": "Segments and transcripts added successfully"}, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer_transcript.errors, status=status.HTTP_400_BAD_REQUEST)
            
 
    
    @action(detail=False, methods=['get'], url_path='get_segment_transcript/(?P<video_id>\d+)')
    def get_segments_and_transcripts(self, request, video_id=None):
        # Ensure the user is authenticated
        if not request.user.is_authenticated:
            return Response({"error": "User not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)

        # Get media_id from the URL
        if not video_id:
            return Response({"error": "Video ID not provided"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            video = Video.objects.get(pk=video_id)
        except Video.DoesNotExist:
            return Response({"error": "Video not found"}, status=status.HTTP_404_NOT_FOUND)

        # Retrieve video segments
        video_segments = VideoSegment.objects.filter(VideoID=video_id)

        if not video_segments.exists():
            return Response({"error": "No video segments found"}, status=status.HTTP_404_NOT_FOUND)

        segments_data = []
        for segment in video_segments:
            # Retrieve transcripts for each segment
            transcripts = Transcript.objects.filter(videoID=video_id, videoSegmentID=segment.id)
            transcript_serializer = TranscriptSerializer(transcripts, many=True)
            segment_data = {
                'segment': VideoSegmentSerializer(segment).data,
                'transcripts': transcript_serializer.data
            }
            segments_data.append(segment_data)

        return Response(segments_data, status=status.HTTP_200_OK)
    

class MonumentViewSet(viewsets.ModelViewSet):
    queryset = Monument.objects.all()
    serializer_class =MonumentSerializer

class CityViewSet(viewsets.ModelViewSet):
    queryset = City.objects.all()
    serializer_class = CitySerializer

class TopicViewSet(viewsets.ModelViewSet):
    queryset = Topic.objects.all()
    serializer_class = TopicSerializer

class ImportantPersonViewSet(viewsets.ModelViewSet):
    queryset = ImportantPerson.objects.all()
    serializer_class = ImportantPersonSerializer