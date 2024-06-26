from ..users.permissions import IsAdmin
from rest_framework import viewsets,status
from .permissions import IsVideoOwnerOrReadOnly
from .models import Video, Transcript, VideoSegment, Participant
from .serializers import VideoSerializer, TranscriptSerializer, VideoSegmentSerializer,ParticipantSerializer
from rest_framework.response import Response
from rest_framework.decorators import action
from datetime import datetime
from rest_framework.permissions import AllowAny

class VideoViewSet(viewsets.ModelViewSet):
    queryset = Video.objects.all()
    serializer_class = VideoSerializer
    #add this back when done with testing
    #permission_classes = [IsVideoOwnerOrReadOnly]
    permission_classes = [AllowAny]

class TranscriptViewSet(viewsets.ModelViewSet):
    queryset = Transcript.objects.all()
    serializer_class = TranscriptSerializer
    permission_classes = [IsAdmin]

class VideoSegmentViewSet(viewsets.ModelViewSet):
    queryset = VideoSegment.objects.all()
    serializer_class = VideoSegmentSerializer
    permission_classes = [IsAdmin]


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
    #queryset to filter by role
    def get_queryset(self):
        queryset = super().get_queryset()
        role = self.request.query_params.get('role')
        if role in ['interviewer', 'interviewee']:
            queryset = queryset.filter(role=role)
        return queryset
    

    #function to get the participants by role
    @action(detail=False, methods=['get'])
    def by_role(self, request):
        participants = self.get_queryset()
        serializer = ParticipantSerializer(participants, many=True)
        return Response(serializer.data)
    
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
    @action(detail=True, methods=['post'])
    def create_transcripts(self, request, video_id):
        #make sure the video exists within the database
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
                return Response({"error": f"Segment number '{segment_number}' does not exist for this video."},
                                status=status.HTTP_400_BAD_REQUEST)
            prepared_transcript = {
                'videoID': video.id,
                'VideoSegmentID': video_segment.id, 
                'title': transcript_data.get('title'),
                'content': transcript_data.get('content'),
                'transcriberID': request.user.id, 
                'transcriptDate': datetime.now(),  
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
    #function to get the transcript based on the video id 
    @action(detail=True, methods=['get'])
    def get_transcripts(self, request, video_id):
        try:
            video = Video.objects.get(pk=video_id)
        except Video.DoesNotExist:
            return Response({"error": "Video not found"}, status=status.HTTP_404_NOT_FOUND)

        transcripts = Transcript.objects.filter(videoID=video)
        serializer = TranscriptSerializer(transcripts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)