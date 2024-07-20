from ..users.permissions import IsAdmin
from rest_framework import viewsets,status
from .permissions import IsVideoOwnerOrReadOnly
from .models import Video, Transcript, VideoSegment, Participant
from .serializers import VideoSerializer, TranscriptSerializer, VideoSegmentSerializer,ParticipantSerializer
from rest_framework.response import Response
from rest_framework.decorators import action
from datetime import datetime
from rest_framework.permissions import AllowAny
from django.db import transaction
from rest_framework.permissions import IsAuthenticated


class VideoViewSet(viewsets.ModelViewSet):
    queryset = Video.objects.all()
    serializer_class = VideoSerializer
    permission_classes = [IsVideoOwnerOrReadOnly]
    #uncomment if needed for testing
    # permission_classes = [AllowAny]

#the interview/interviwer function class
class ParticipantViewSet(viewsets.ModelViewSet):
    queryset = Participant.objects.all()
    serializer_class = ParticipantSerializer

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def add_participant(self, request):
        video_id = request.data.get('video_id')
        participants_data = request.data.get('participants', [])

        if not video_id:
            return Response({"error": "video_id is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Check if video exists
        try:
            video = Video.objects.get(pk=video_id)
        except Video.DoesNotExist:
            return Response({"error": "Video not found"}, status=status.HTTP_404_NOT_FOUND)

        if not isinstance(participants_data, list):
            return Response({"error": "Participants data must be a list."}, status=status.HTTP_400_BAD_REQUEST)

        errors = []
        for participant_data in participants_data:
            # Ensure each participant's video_id is correctly set
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
    #function to cfreate video segment and save them even as a bulk
    @action(detail=False, methods=['post'],permission_classes=[IsAuthenticated])
    def create_video_segment(self, request):
        #see if video exists in database based on the video_id
        try:
            video_id = request.data.get('video_id')
            video = Video.objects.get(pk=video_id)
        except Video.DoesNotExist:
            return Response({"error": "Video not found"}, status=status.HTTP_404_NOT_FOUND)
        segments_data = request.data.get('segments', [])
        # collect existing segment numbers for the given video_id
        existing_segment_numbers = set(VideoSegment.objects.filter(VideoID=video_id).values_list('segmentNumber', flat=True))
        seen_segment_numbers = set()
        for segment_data in segments_data:
            segment_number = segment_data.get('segmentNumber')
            #make sure that the segemnt numbers to be received are unique within database
            if VideoSegment.objects.filter(VideoID=video.id, segmentNumber=segment_number).exists():
                return Response({"error": f"A segment with segmentNumber {segment_number} already exists for this video."},
                                status=status.HTTP_400_BAD_REQUEST)
            # check if segmentNumber is unique within the request data
            if segment_number in seen_segment_numbers:
                return Response({"error": f"Duplicate segmentNumber '{segment_number}' found in the request."},
                                status=status.HTTP_400_BAD_REQUEST)
            seen_segment_numbers.add(segment_number)            
            # prepare segment for bulk creation
            segment_data['VideoID'] = video.id
        # bulk create the segments in the database
        serializer = VideoSegmentSerializer(data=segments_data, many=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Video segments added successfully"}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    #function for retrevieve segements 
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
# transcript viewset
class TranscriptViewSet(viewsets.ModelViewSet):
    queryset = Transcript.objects.all()
    serializer_class = TranscriptSerializer
    #the function foe crating transcripts 
 # Make sure the video exists within the database
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
        
    #this is a function to retrieve transcripts of a specific video
    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def get_transcripts(self, request, pk=None):
        try:
            video = Video.objects.get(pk=pk)
        except Video.DoesNotExist:
            return Response({"error": "Video not found"}, status=status.HTTP_404_NOT_FOUND)

        transcripts = Transcript.objects.filter(videoID=video)
        serializer = TranscriptSerializer(transcripts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class complexSegementViewSet(viewsets.ModelViewSet):
    queryset = VideoSegment.objects.all()
    serializer_class = VideoSegmentSerializer

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