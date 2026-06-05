"""
Family Details Views for Admin Side - Get and Edit Only.

Provides REST API endpoints for viewing and editing employee family members:
- GET /employees/{employee_id}/family-details - Get all family members
- PATCH /employees/{employee_id}/family-details/{family_member_id} - Update family member

All endpoints include proper error handling and SQL injection protection.
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from apps.security.permissions import HasRBACPermission
from django.http import Http404

from apps.employees.serializers.admin.family_details_serializer import (
    FamilyMemberSerializer,
)
from apps.employees.services.admin.family_details_service import FamilyDetailsService


class FamilyDetailsListView(APIView):
    """
    API endpoint for viewing all family members of an employee.
    
    Supports:
    - GET: Retrieve all family members for an employee
    """
    
    permission_classes = [IsAuthenticated, HasRBACPermission]
    required_permissions = ["employee.view_all_employee"]
    
    def get(self, request, employee_id):
        """
        Retrieve all family members for a specific employee.
        
        Returns:
            Response: List of all active family members with their details
            
        Errors:
            404: Employee not found
        """
        try:
            payload = FamilyDetailsService.get_family_display_for_admin(employee_id)
            return Response(payload, status=status.HTTP_200_OK)
        
        except Http404:
            return Response(
                {'detail': 'Employee not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'detail': f'Error retrieving family details: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class FamilyMemberDetailView(APIView):
    """
    API endpoint for editing individual family members.
    
    Supports:
    - PATCH: Update a family member's details
    """
    
    permission_classes = [IsAuthenticated, HasRBACPermission]
    required_permissions = ["employee.edit_employee"]
    
    def patch(self, request, employee_id, family_member_id):
        """
        Update a family member's details.
        
        Request body can include any of:
        - first_name: Update first name
        - last_name: Update last name
        - date_of_birth: Update DOB (YYYY-MM-DD format)
        - relation: Update relation ID
        - gender: Update gender ID
        - occupation: Update occupation ID
        - blood_group: Update blood group ID
        - nationality: Update nationality ID
        - mobile_no: Update contact number
        - email: Update email
        - is_dependent: Update dependent status
        - is_nominee: Update nominee status
        - is_active: Deactivate/reactivate
        
        Returns:
            Response: Updated family member details
            
        Errors:
            400: Validation error
            404: Employee or family member not found
            500: Server error
        """
        try:
            serializer = FamilyMemberSerializer(data=request.data, partial=True)
            
            if not serializer.is_valid():
                return Response(
                    {'errors': serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Update family member
            family_member = FamilyDetailsService.update_family_member(
                employee_id,
                family_member_id,
                serializer.validated_data,
                updated_by=request.user
            )
            
            # Return updated object
            response_serializer = FamilyMemberSerializer(family_member)
            return Response(
                response_serializer.data,
                status=status.HTTP_200_OK
            )
        
        except Http404:
            return Response(
                {'detail': 'Family member not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'detail': f'Error updating family member: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
