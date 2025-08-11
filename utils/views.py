from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes
from .signed_urls import get_signed_media_url
from django.utils import timezone

class SignedUrlView(APIView):
    """Generate signed URLs for file downloads"""
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        parameters=[
            OpenApiParameter('file_path', OpenApiTypes.STR, description='File path to generate signed URL for'),
        ],
        responses={200: dict},
        description="Generate a signed URL for file download"
    )
    def get(self, request):
        """Generate signed URL for file download"""
        file_path = request.query_params.get('file_path')
        
        if not file_path:
            return Response({
                'success': False,
                'error': {
                    'code': 'MISSING_PARAMETER',
                    'message': 'file_path parameter is required'
                },
                'timestamp': timezone.now().isoformat()
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            signed_url = get_signed_media_url(file_path)
            
            return Response({
                'success': True,
                'data': {
                    'signed_url': signed_url,
                    'file_path': file_path,
                    'expires_in': 3600  # 1 hour
                },
                'message': 'Signed URL generated successfully',
                'timestamp': timezone.now().isoformat()
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'success': False,
                'error': {
                    'code': 'SIGNED_URL_ERROR',
                    'message': f'Error generating signed URL: {str(e)}'
                },
                'timestamp': timezone.now().isoformat()
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
