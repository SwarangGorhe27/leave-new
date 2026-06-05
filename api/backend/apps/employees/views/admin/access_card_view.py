"""
Access Card Views for Admin Side.

Provides REST API endpoints for viewing, creating, updating, and deleting access cards:
- GET /employees/{employee_id}/access-cards - Get all access cards
- POST /employees/{employee_id}/access-cards - Create new access card
- PATCH /employees/{employee_id}/access-cards/{card_id} - Update access card
- DELETE /employees/{employee_id}/access-cards/{card_id} - Deactivate access card
- GET /employees/{employee_id}/access-cards/{card_id} - Get specific access card

All endpoints include proper error handling and SQL injection protection.
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from apps.security.permissions import HasRBACPermission
from django.http import Http404

from apps.employees.serializers.admin.access_card_serializer import (
    AccessCardSerializer,
    AccessCardListSerializer,
    AccessCardCreateSerializer,
)
from apps.employees.services.admin.access_card_service import AccessCardService
from apps.core.openapi import empty_ok_response, extend_schema, extend_schema_view


@extend_schema_view(
    get=extend_schema(responses={status.HTTP_200_OK: AccessCardListSerializer(many=True)}),
    post=extend_schema(
        request=AccessCardCreateSerializer,
        responses={status.HTTP_201_CREATED: AccessCardSerializer},
    ),
)
class AccessCardListCreateView(APIView):
    """
    API endpoint for viewing and creating access cards.
    
    Supports:
    - GET: Retrieve all access cards for an employee
    - POST: Create a new access card
    """
    
    permission_classes = [IsAuthenticated, HasRBACPermission]
    required_permissions_by_method = {
        "GET": ["employee.view_employee"],
        "POST": ["employee.edit_employee"],
    }
    
    def get(self, request, employee_id):
        """
        Retrieve all access cards for a specific employee.
        
        URL: GET /api/employees/{employee_id}/access-cards
        
        Returns:
            Response: List of all active access cards with their details
            
        Errors:
            404: Employee not found
            500: Internal server error
        """
        try:
            # Get all access cards using service
            access_cards = AccessCardService.get_all_access_cards(employee_id)
            
            # Serialize access cards
            serializer = AccessCardListSerializer(access_cards, many=True)
            
            return Response({
                'status': 'success',
                'count': len(serializer.data),
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        
        except Http404:
            return Response({
                'status': 'error',
                'detail': 'Employee not found.'
            }, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            return Response({
                'status': 'error',
                'detail': f'Error retrieving access cards: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def post(self, request, employee_id):
        """
        Create a new access card for an employee.
        
        URL: POST /api/employees/{employee_id}/access-cards
        
        Request body:
        {
            "access_card_number": "CARD123456",
            "from_date": "2024-01-15",
            "to_date": "2025-01-14"
        }
        
        Returns:
            Response: Created access card details
            
        Errors:
            400: Validation error
            404: Employee not found
            500: Internal server error
        """
        try:
            # Validate input data
            serializer = AccessCardCreateSerializer(
                data=request.data,
                context={"employee_id": employee_id},
            )
            
            if not serializer.is_valid():
                return Response({
                    'status': 'error',
                    'detail': 'Validation failed',
                    'errors': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Create access card using service
            access_card = AccessCardService.create_access_card(
                employee_id=employee_id,
                validated_data=serializer.validated_data,
                created_by=request.user if request.user.is_authenticated else None
            )
            
            # Serialize the created object
            response_serializer = AccessCardSerializer(access_card)
            
            return Response({
                'status': 'success',
                'detail': 'Access card created successfully',
                'data': response_serializer.data
            }, status=status.HTTP_201_CREATED)
        
        except Http404:
            return Response({
                'status': 'error',
                'detail': 'Employee not found.'
            }, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            return Response({
                'status': 'error',
                'detail': f'Error creating access card: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema_view(
    get=extend_schema(responses={status.HTTP_200_OK: AccessCardSerializer}),
    patch=extend_schema(
        request=AccessCardSerializer,
        responses={status.HTTP_200_OK: AccessCardSerializer},
    ),
    delete=extend_schema(responses=empty_ok_response()),
)
class AccessCardDetailView(APIView):
    """
    API endpoint for viewing, updating, and deleting specific access cards.
    
    Supports:
    - GET: Retrieve a specific access card
    - PATCH: Update an access card
    - DELETE: Deactivate an access card
    """
    
    permission_classes = [IsAuthenticated, HasRBACPermission]
    required_permissions_by_method = {
        "GET": ["employee.view_employee"],
        "PATCH": ["employee.edit_employee"],
        "DELETE": ["employee.delete_employee"],
    }
    
    def get(self, request, employee_id, card_id):
        """
        Retrieve a specific access card.
        
        URL: GET /api/employees/{employee_id}/access-cards/{card_id}
        
        Returns:
            Response: Access card details
            
        Errors:
            404: Employee or access card not found
            500: Internal server error
        """
        try:
            access_card = AccessCardService.get_access_card_by_id(employee_id, card_id)
            serializer = AccessCardSerializer(access_card)
            
            return Response({
                'status': 'success',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        
        except Http404:
            return Response({
                'status': 'error',
                'detail': 'Employee or access card not found.'
            }, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            return Response({
                'status': 'error',
                'detail': f'Error retrieving access card: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def patch(self, request, employee_id, card_id):
        """
        Update an access card's details.
        
        URL: PATCH /api/employees/{employee_id}/access-cards/{card_id}
        
        Request body (all fields optional):
        {
            "access_card_number": "CARD123456",
            "from_date": "2024-01-15",
            "to_date": "2025-01-14",
            "is_active": true
        }
        
        Returns:
            Response: Updated access card details
            
        Errors:
            400: Validation error
            404: Employee or access card not found
            500: Internal server error
        """
        try:
            # Get the current access card
            access_card = AccessCardService.get_access_card_by_id(employee_id, card_id)
            
            # Validate input data
            serializer = AccessCardSerializer(
                access_card,
                data=request.data,
                partial=True,
                context={'employee_id': employee_id}
            )
            
            if not serializer.is_valid():
                return Response({
                    'status': 'error',
                    'detail': 'Validation failed',
                    'errors': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Update access card using service
            updated_card = AccessCardService.update_access_card(
                employee_id=employee_id,
                card_id=card_id,
                validated_data=serializer.validated_data,
                updated_by=request.user if request.user.is_authenticated else None
            )
            
            # Serialize the updated object
            response_serializer = AccessCardSerializer(updated_card)
            
            return Response({
                'status': 'success',
                'detail': 'Access card updated successfully',
                'data': response_serializer.data
            }, status=status.HTTP_200_OK)
        
        except Http404:
            return Response({
                'status': 'error',
                'detail': 'Employee or access card not found.'
            }, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            return Response({
                'status': 'error',
                'detail': f'Error updating access card: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def delete(self, request, employee_id, card_id):
        """
        Deactivate (soft delete) an access card.
        
        URL: DELETE /api/employees/{employee_id}/access-cards/{card_id}
        
        Returns:
            Response: Success message
            
        Errors:
            404: Employee or access card not found
            500: Internal server error
        """
        try:
            # Deactivate access card using service
            AccessCardService.deactivate_access_card(employee_id, card_id)
            
            return Response({
                'status': 'success',
                'detail': 'Access card deactivated successfully'
            }, status=status.HTTP_200_OK)
        
        except Http404:
            return Response({
                'status': 'error',
                'detail': 'Employee or access card not found.'
            }, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            return Response({
                'status': 'error',
                'detail': f'Error deactivating access card: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
