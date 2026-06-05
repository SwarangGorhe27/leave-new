"""
Nominee Details Views for Admin Side — GET and PATCH.

Endpoints:
    GET  /employees/{employee_id}/nominee-details
         → Returns all active nominees for the employee.

    PATCH /employees/{employee_id}/nominee-details/{nominee_id}
         → Partially updates a single nominee record.
           Accepts identity_proof_* fields so admin can record
           whichever document the employee uploaded via the
           single "identity_proof" UI section.

All endpoints include proper error handling and SQL injection protection.
"""

from django.http import Http404
from rest_framework import status
from apps.security.permissions import HasRBACPermission
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.employees.serializers.admin.nominee_serializer import (
    NomineeDetailSerializer,
    NomineeUpdateSerializer,
)
from apps.employees.services.admin.nominee_service import NomineeService


class NomineeListView(APIView):
    """
    GET /employees/{employee_id}/nominee-details

    Returns all active nominee records for an employee.
    Each record includes resolved master labels and identity_proof metadata
    so the admin UI can display the uploaded document filename / link.
    """

    # permission_classes = [IsAuthenticated]   # ← enable in production
    permission_classes = [IsAuthenticated, HasRBACPermission]
    required_permissions = ["employee.view_employee"]

    def get(self, request, employee_id):
        """
        Retrieve all nominees for a specific employee.

        Path params:
            employee_id (UUID): The employee's UUID.

        Returns:
            200: List of nominee objects.
            404: Employee not found.
            500: Unexpected server error.
        """
        try:
            nominees = NomineeService.get_all_nominees(str(employee_id))
            serializer = NomineeDetailSerializer(nominees, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Http404:
            return Response(
                {"detail": "Employee not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as exc:
            return Response(
                {"detail": f"Error retrieving nominee details: {str(exc)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class NomineeDetailView(APIView):
    """
    PATCH /employees/{employee_id}/nominee-details/{nominee_id}

    Partially updates a nominee record.

    Accepts any subset of:
        first_name, last_name, date_of_birth, relation,
        nominee_purpose, nominee_percentage,
        mobile_no, address,
        guardian_name, guardian_relation, guardian_address,
        identity_proof_url, identity_proof_name,
        identity_proof_size_bytes, identity_proof_mime_type,
        is_active
    """

    # permission_classes = [IsAuthenticated]   # ← enable in production
    permission_classes = [IsAuthenticated, HasRBACPermission]
    required_permissions = ["employee.edit_employee"]

    def patch(self, request, employee_id, nominee_id):
        """
        Partially update a nominee's details.

        Path params:
            employee_id (UUID): The employee's UUID.
            nominee_id  (UUID): The nominee record's UUID.

        Request body (all optional — send only fields to update):
            {
                "first_name": "Priya",
                "last_name": "Sharma",
                "date_of_birth": "1994-03-10",
                "relation": <relation_id>,
                "nominee_purpose": <purpose_id>,
                "nominee_percentage": "100.00",
                "mobile_no": "+91 98765 00001",
                "address": "42, Koramangala, Bangalore",
                "guardian_name": null,
                "guardian_relation": null,
                "guardian_address": null,
                "identity_proof_url": "https://s3.example.com/proofs/abc.pdf",
                "identity_proof_name": "aadhaar_priya.pdf",
                "identity_proof_size_bytes": 204800,
                "identity_proof_mime_type": "application/pdf",
                "is_active": true
            }

        Returns:
            200: Updated nominee object (full detail with labels).
            400: Validation errors.
            404: Employee or nominee not found.
            500: Unexpected server error.
        """
        try:
            serializer = NomineeUpdateSerializer(data=request.data, partial=True)

            if not serializer.is_valid():
                return Response(
                    {"errors": serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            nominee = NomineeService.update_nominee(
                employee_id=str(employee_id),
                nominee_id=str(nominee_id),
                validated_data=serializer.validated_data,
                updated_by=request.user,
            )

            # Return the full detail serializer (with labels resolved)
            response_serializer = NomineeDetailSerializer(nominee)
            return Response(response_serializer.data, status=status.HTTP_200_OK)

        except Http404:
            return Response(
                {"detail": "Nominee not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as exc:
            return Response(
                {"detail": f"Error updating nominee: {str(exc)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
