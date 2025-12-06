from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import RouteRequestSerializer, RouteResponseSerializer
from .utils import RouteOptimizer
import logging

logger = logging.getLogger(__name__)

class OptimizeRouteView(APIView):
    """
    API endpoint to optimize route with fuel stops
    
    POST /api/optimize-route/
    Body: {
        "start": "Los Angeles, CA",
        "finish": "New York, NY"
    }
    """
    
    def post(self, request):
        serializer = RouteRequestSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                serializer.errors, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            optimizer = RouteOptimizer()
            result = optimizer.optimize_route(
                start=serializer.validated_data['start'],
                finish=serializer.validated_data['finish']
            )
            
            response_serializer = RouteResponseSerializer(data=result)
            response_serializer.is_valid(raise_exception=True)
            
            return Response(
                response_serializer.data,
                status=status.HTTP_200_OK
            )
            
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error optimizing route: {str(e)}")
            return Response(
                {'error': 'Internal server error occurred'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )