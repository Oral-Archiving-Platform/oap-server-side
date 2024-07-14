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


class VideoViewSet(viewsets.ModelViewSet):
    queryset = Video.objects.all()
    serializer_class = VideoSerializer
    permission_classes = [IsVideoOwnerOrReadOnly]
    #uncomment if needed for testing
    # permission_classes = [AllowAny]

#the interview/interviwer function class
class AddparticipantViewSet(viewsets.ModelViewSet):
    queryset= Participant.objects.all()
    def create(self, request, video_id):
        #check if video exists 
        try:
            video = Video.objects.get(pk=video_id)
        except Video.DoesNotExist:
            return Response({"error": "Video not found"}, status=status.HTTP_404_NOT_FOUND)
        participants_data = request.data.get('participants', [])
        #serialize the participant data and store it
        for participant_data in participants_data:
            participant_data['VideoId'] = video.id  # Set the foreign key to the existing video id
            serializer = ParticipantSerializer(data=participant_data)
            if serializer.is_valid():
                serializer.save()
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({"message": "Participants added successfully"}, status=status.HTTP_201_CREATED)
#retreive by role and by video id 
    @action(detail=False, methods=['post'])
    def by_role(self, request):
        role = request.data.get('role')
        video_id = request.data.get('video_id')

        if not role or not video_id:
            return Response({"error": "Both role and video_id parameters are required."}, status=status.HTTP_400_BAD_REQUEST)

        participants = self.queryset.filter(role=role, VideoId=video_id)
        serializer = ParticipantSerializer(participants, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class VideoSegmentViewSet(viewsets.ModelViewSet):
    queryset = VideoSegment.objects.all()
    serializer_class = VideoSegmentSerializer
    #function to cfreate video segment and save them even as a bulk
    @action(detail=True, methods=['post'])
    def create_video_segment(self, request, video_id):
        #see if video exists in database based on the video_id
        try:
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
    @action(detail=True, methods=['get'])
    def get_segments(self, request, video_id):
        try:
            video = Video.objects.get(pk=video_id)
        except Video.DoesNotExist:
            return Response({"error": "Video not found"}, status=status.HTTP_404_NOT_FOUND)
        
        segments = VideoSegment.objects.filter(VideoID=video)
        serializer = VideoSegmentSerializer(segments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

# transcript viewset
class TranscriptViewSet(viewsets.ModelViewSet):
    queryset = Transcript.objects.all()
    serializer_class = TranscriptSerializer
    #the function foe crating transcripts 
 # Make sure the video exists within the database
    @action(detail=True, methods=['post'])
    def create_transcripts(self, request, video_id):
        try:
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
    @action(detail=True, methods=['get'])
    def get_transcripts(self, request, video_id):
        try:
            video = Video.objects.get(pk=video_id)
        except Video.DoesNotExist:
            return Response({"error": "Video not found"}, status=status.HTTP_404_NOT_FOUND)

        transcripts = Transcript.objects.filter(videoID=video)
        serializer = TranscriptSerializer(transcripts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

#this is the added segment viewset 
class complexSegementViewSet(viewsets.ModelViewSet):
    queryset = Video.objects.all()
    serializer_class = VideoSerializer
    #permission_classes = [AllowAny]   Adjust permissions as needed

    @action(detail=True, methods=['post'], url_path='create-segments-and-transcripts')
    def create_segments_and_transcripts(self, request, video_id):
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

                if VideoSegment.objects.filter(VideoID=video.id, segmentNumber=segment_number).exists():
                    return Response({"error": f"A segment with segmentNumber {segment_number} already exists for this video."},
                                    status=status.HTTP_400_BAD_REQUEST)
                elif segment_number in seen_segment_numbers:
                    return Response({"error": f"Duplicate segmentNumber '{segment_number}' found in the request."},
                                    status=status.HTTP_400_BAD_REQUEST)
                else:
                    segment_data['VideoID'] = video.id
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
                    video_segment = VideoSegment.objects.get(VideoID=video.id, segmentNumber=segment_number)
                except VideoSegment.DoesNotExist:
                    return Response({"error": f"Segment number '{segment_number}' does not exist for this video."},
                                    status=status.HTTP_400_BAD_REQUEST)

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
                created_transcripts.append(prepared_transcript)

            serializer_transcript = TranscriptSerializer(data=created_transcripts, many=True)
            if serializer_transcript.is_valid():
                serializer_transcript.save()
                return Response({"message": "Segments and transcripts added successfully"}, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer_transcript.errors, status=status.HTTP_400_BAD_REQUEST)
