from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.security.permissions import HasRBACPermission
from apps.employees.serializers.admin.role_mapping_serializer import (
    EmployeeRoleListSerializer,
    RoleMappingOptionsSerializer,
    RoleAssignSerializer,
    RoleAssignmentSerializer,
    RoleBulkMappingSerializer,
    RoleRevokeSerializer,
    SystemRoleSerializer,
    SystemRoleWriteSerializer,
)
from apps.employees.services.admin.role_mapping_service import (
    RoleMappingService,
    company_from_request,
)


class RoleDashboardView(APIView):
    permission_classes = [IsAuthenticated, HasRBACPermission]
    required_permissions = ["employee.assign_role", "employee.view_employee"]

    def get(self, request, *args, **kwargs):
        company = company_from_request(request)
        roles = RoleMappingService.role_queryset(company)
        employees = RoleMappingService.employee_queryset(company, request.query_params)
        return Response(
            {
                "roles": SystemRoleSerializer(roles, many=True).data,
                "employees": EmployeeRoleListSerializer(employees[:100], many=True).data,
            },
            status=status.HTTP_200_OK,
        )


class RoleListCreateView(APIView):
    permission_classes = [IsAuthenticated, HasRBACPermission]
    required_permissions_by_method = {
        "GET": ["employee.assign_role", "employee.view_employee"],
        "POST": ["employee.assign_role"],
    }

    def get(self, request, *args, **kwargs):
        company = company_from_request(request)
        roles = RoleMappingService.role_queryset(company)
        return Response(SystemRoleSerializer(roles, many=True).data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        serializer = SystemRoleWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        role = RoleMappingService.create_role(serializer.validated_data)
        return Response(SystemRoleSerializer(role).data, status=status.HTTP_201_CREATED)


class RoleMappingOptionsView(APIView):
    permission_classes = [IsAuthenticated, HasRBACPermission]
    required_permissions = ["employee.assign_role"]

    def get(self, request, *args, **kwargs):
        company = company_from_request(request)
        payload = RoleMappingService.option_payload(company)
        return Response(RoleMappingOptionsSerializer(payload).data, status=status.HTTP_200_OK)


class RoleDetailView(APIView):
    permission_classes = [IsAuthenticated, HasRBACPermission]
    required_permissions_by_method = {
        "PATCH": ["employee.assign_role"],
        "DELETE": ["employee.remove_role"],
    }

    def patch(self, request, role_id, *args, **kwargs):
        serializer = SystemRoleWriteSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        role = RoleMappingService.update_role(role_id, serializer.validated_data)
        return Response(SystemRoleSerializer(role).data, status=status.HTTP_200_OK)

    def delete(self, request, role_id, *args, **kwargs):
        company = company_from_request(request)
        RoleMappingService.delete_role(company, role_id)
        return Response(status=status.HTTP_204_NO_CONTENT)


class RoleEmployeeListView(APIView):
    permission_classes = [IsAuthenticated, HasRBACPermission]
    required_permissions = ["employee.assign_role", "employee.view_employee"]

    def get(self, request, *args, **kwargs):
        company = company_from_request(request)
        employees = RoleMappingService.employee_queryset(company, request.query_params)
        return Response(EmployeeRoleListSerializer(employees[:100], many=True).data, status=status.HTTP_200_OK)


class EmployeeRoleDetailView(APIView):
    permission_classes = [IsAuthenticated, HasRBACPermission]
    required_permissions_by_method = {
        "GET": ["employee.assign_role", "employee.view_employee"],
        "POST": ["employee.assign_role"],
        "PUT": ["employee.assign_role"],
        "PATCH": ["employee.assign_role"],
    }

    def get(self, request, target_employee_id, *args, **kwargs):
        company = company_from_request(request)
        employee, assignments = RoleMappingService.employee_assignments(company, target_employee_id)
        return Response(
            {
                "employee": EmployeeRoleListSerializer(employee).data,
                "assignments": RoleAssignmentSerializer(assignments, many=True).data,
            },
            status=status.HTTP_200_OK,
        )

    def post(self, request, target_employee_id, *args, **kwargs):
        company = company_from_request(request)
        serializer = RoleAssignSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        assignment = RoleMappingService.assign_role(
            company,
            target_employee_id,
            serializer.validated_data,
            user=request.user,
        )
        return Response(RoleAssignmentSerializer(assignment).data, status=status.HTTP_201_CREATED)

    def put(self, request, target_employee_id, *args, **kwargs):
        company = company_from_request(request)
        serializer = RoleBulkMappingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        assignments = RoleMappingService.sync_employee_roles(
            company,
            target_employee_id,
            serializer.validated_data,
            user=request.user,
        )
        return Response(RoleAssignmentSerializer(assignments, many=True).data, status=status.HTTP_200_OK)

    def patch(self, request, target_employee_id, *args, **kwargs):
        return self.put(request, target_employee_id, *args, **kwargs)


class RoleAssignmentRevokeView(APIView):
    permission_classes = [IsAuthenticated, HasRBACPermission]
    required_permissions = ["employee.remove_role"]

    def delete(self, request, assignment_id, *args, **kwargs):
        company = company_from_request(request)
        serializer = RoleRevokeSerializer(data=request.data or {})
        serializer.is_valid(raise_exception=True)
        RoleMappingService.revoke_assignment(
            company,
            assignment_id,
            serializer.validated_data,
            user=request.user,
        )
        return Response(status=status.HTTP_204_NO_CONTENT)
