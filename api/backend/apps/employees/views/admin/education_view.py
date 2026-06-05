"""
Education Details Views for Admin Side - Get and Edit Only.

Provides REST API endpoints for viewing and editing employee education records:
- GET /employees/{employee_id}/education-details - Get all education records
- PATCH /employees/{employee_id}/education-details/{education_id} - Update education record

All endpoints include proper error handling and SQL injection protection.
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from apps.security.permissions import HasRBACPermission
from django.http import Http404

from apps.employees.serializers.admin.education_serializer import (
    EducationDetailSerializer,
    EducationWriteSerializer,
)
from apps.employees.services.admin.education_service import EducationDetailsService
from apps.core.openapi import extend_schema, extend_schema_view


@extend_schema_view(
    get=extend_schema(responses={status.HTTP_200_OK: EducationDetailSerializer(many=True)}),
)
class EducationDetailsListView(APIView):
    """
    API endpoint for viewing all education records of an employee.
    
    Supports:
    - GET: Retrieve all education records for an employee
    """
    
    permission_classes = [IsAuthenticated, HasRBACPermission]
    required_permissions = ["employee.view_employee"]
    
    def get(self, request, employee_id):
        """
        Retrieve all education records for a specific employee.
        
        Returns:
            Response: List of all active education records with their details
            
        Errors:
            404: Employee not found
        """
        try:
            # Get all education records using service
            education_records = EducationDetailsService.get_all_education_records(
                employee_id
            )
            
            # Serialize education records
            serializer = EducationDetailSerializer(education_records, many=True)
            
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except Http404:
            return Response(
                {'detail': 'Employee not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'detail': f'Error retrieving education details: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@extend_schema_view(
    patch=extend_schema(
        request=EducationWriteSerializer,
        responses={status.HTTP_200_OK: EducationDetailSerializer},
    ),
)
class EducationDetailView(APIView):
    """
    API endpoint for editing individual education records.
    
    Supports:
    - PATCH: Update a education record's details
    """
    
    permission_classes = [IsAuthenticated, HasRBACPermission]
    required_permissions = ["employee.edit_employee"]

    def patch(self, request, employee_id, education_id):
        """
        Update an education record's details.
        
        Request body can include any of:
        - education_level: Education level ID
        - qualification: Qualification ID
        - specialization: Specialization ID
        - board: Board ID
        - institution_name: Institution name
        - university_name: University name
        - start_year: Start year
        - end_year: End year
        - from_date/start_date: Start date (YYYY-MM-DD format)
        - to_date/end_date: End date (YYYY-MM-DD format)
        - study_mode: Study mode ID
        - education_status: Education status ID
        - grade_or_cgpa: Grade or CGPA
        - percentage: Percentage (0-100)
        - roll_number: Roll number
        - certificate_number: Certificate number
        - is_highest: Mark as highest qualification
        - sort_order: Sort order
        
        Returns:
            Response: Updated education record details
            
        Errors:
            400: Validation error
            404: Employee or education record not found
            500: Server error
        """
        try:
            serializer = EducationWriteSerializer(
                data=request.data,
                partial=True
            )
            
            if not serializer.is_valid():
                return Response(
                    {'errors': serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Update education record
            education_record = EducationDetailsService.update_education_record(
                employee_id,
                education_id,
                serializer.validated_data,
                updated_by=request.user
            )
            
            # Return the updated record
            response_serializer = EducationDetailSerializer(education_record)
            
            return Response(
                response_serializer.data,
                status=status.HTTP_200_OK
            )
        
        except Http404:
            return Response(
                {'detail': 'Education record not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'detail': f'Error updating education record: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
