from django.apps import apps
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema
 

from ..helpers import paginate_queryset
from ..models.masters.leave_policy import (
    EmployeeLeavePolicy,
    LeavePolicy,
    LeavePolicyRule,
)
from ..models.masters.leave_types import LeaveType
from ..serializers.leave_policies import (
    LeavePolicyCreateSerializer,
    LeavePolicyAssignSerializer,
    LeavePolicySerializer,
    EmployeePolicyAssignSerializer,
)

from ..serializers.leave_policies import LeavePolicyUpdateSerializer
from apps.security.permissions import HasRBACPermission
from drf_spectacular.utils import extend_schema
 
 

@extend_schema(tags=["Admin (Leave)"])
class AdminLeavePolicyListCreateView(APIView):
    permission_classes = [IsAuthenticated, HasRBACPermission]
    required_permissions = ["leave.view_leave_policies", "leave.add_leave_policy"]

    def get(self, request):
        queryset = LeavePolicy.objects.filter(is_active=True).order_by(
            "-effective_from"
        )
        results, total = paginate_queryset(queryset, request)
        serializer = LeavePolicySerializer(results, many=True)
        return Response({"items": serializer.data, "total": total})

    @extend_schema(
        request=LeavePolicyCreateSerializer,
        responses={201: LeavePolicySerializer},
    )
    def post(self, request):
        serializer = LeavePolicyCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        policy = LeavePolicy.objects.create(
            name=data["name"],
            description=data.get("description", ""),
            effective_from=data["effective_from"],
            effective_to=data.get("effective_to"),
            is_active=True,
            meta_data={"code": data["code"]},
        )

        for leave_type_item in data["leave_types"]:
            leave_type = get_object_or_404(
                LeaveType,
                id=leave_type_item["leave_type_id"],
                is_active=True,
            )
            LeavePolicyRule.objects.create(
                policy=policy,
                leave_type=leave_type,
                meta_data={"max_days": str(leave_type_item["max_days"])},
            )

        return Response(
            LeavePolicySerializer(policy).data,
            status=status.HTTP_201_CREATED,
        )


@extend_schema(
    tags=["Admin (Leave)"],
    request=LeavePolicyAssignSerializer,
    responses={200: None},
)
class AdminLeavePolicyAssignView(APIView):
    permission_classes = [IsAuthenticated, HasRBACPermission]
    required_permissions = ["leave.manage_leave_policy_assignments"]
 
    def post(self, request):
        # if not is_admin_user(request.user):
        #     return Response(
        #         {"detail": "Admin or HR role required."},
        #         status=status.HTTP_403_FORBIDDEN,
        #     )
 
        serializer = LeavePolicyAssignSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
 
        policy = get_object_or_404(
            LeavePolicy, id=data["leave_policy_id"], is_active=True
        )
        employee_model = apps.get_model("employees", "Employee")
 
        for employee_id in data["employee_ids"]:
            employee = get_object_or_404(employee_model, pk=employee_id)
            EmployeeLeavePolicy.objects.get_or_create(
                employee=employee,
                policy=policy,
                effective_from=data["effective_date"],
                defaults={"effective_to": None},
            )
 
        return Response({"detail": "Leave policy assigned."}, status=status.HTTP_200_OK)
 
 


@extend_schema(tags=["Admin (Leave)"])
class EmployeePolicyAssignView(APIView):
    """
    API endpoint for assigning leave policy to a single employee.
   
    POST /api/admin/employee-policy/assign/
   
    
    POST /api/admin/employee-policy/assign/
    
    Request:
    {
        "employee_id": 500,
        "leave_policy_id": "uuid",
        "effective_from": "2024-07-01"
    }
   
    
    Response:
    {
        "status": "success",
        "message": "Policy assigned"
    }
    """
   
    permission_classes = [IsAuthenticated, HasRBACPermission]
    required_permissions = ["leave.manage_leave_policy_assignments"]
 
    
    # permission_classes = [IsAuthenticated]

    @extend_schema(
        operation_id="assign_employee_policy",
        description="Assign leave policy to a single employee",
        request=EmployeePolicyAssignSerializer,
        responses={200: None},
    )
    def post(self, request):
        """
        Assign leave policy to a single employee.
       
        
        Only accessible by Admin/HR users.
        """
        # if not is_admin_user(request.user):
        #     return Response(
        #         {"status": "error", "detail": "Admin or HR role required."},
        #         status=status.HTTP_403_FORBIDDEN,
        #     )
 
        serializer = EmployeePolicyAssignSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
 

        serializer = EmployeePolicyAssignSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            # Get leave policy
            policy = get_object_or_404(
                LeavePolicy, id=data["leave_policy_id"], is_active=True
            )
 
            # Get employee
            employee_model = apps.get_model("employees", "Employee")
            employee = get_object_or_404(employee_model, id=data["employee_id"])
 

            # Get employee
            employee_model = apps.get_model("employees", "Employee")
            employee = get_object_or_404(employee_model, id=data["employee_id"])

            # Assign policy to employee
            EmployeeLeavePolicy.objects.get_or_create(
                employee=employee,
                policy=policy,
                effective_from=data["effective_from"],
                defaults={"effective_to": None},
            )
 

            return Response(
                {
                    "status": "success",
                    "message": "Policy assigned",
                },
                status=status.HTTP_200_OK,
            )
 

        except Exception as e:
            return Response(
                {
                    "status": "error",
                    "detail": str(e),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
    

@extend_schema(tags=["Admin (Leave)"])
class AdminLeavePolicyUpdateView(APIView):
    permission_classes = [IsAuthenticated, HasRBACPermission]
    required_permissions = ["leave.update_leave_policy"]

    @extend_schema(
        operation_id="update_leave_policy",
        description="Update leave policy",
        request=LeavePolicyUpdateSerializer,
        responses={200: None},
    )
    def put(self, request, id):
        # if not is_admin_user(request.user):
        #     return Response(
        #         {"detail": "Admin or HR role required."},
        #         status=status.HTTP_403_FORBIDDEN,
        #     )

        leave_policy = get_object_or_404(
            LeavePolicy,
            id=id,
            is_active=True,
        )

        serializer = LeavePolicyUpdateSerializer(
            leave_policy,
            data=request.data,
            partial=True,
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {
                "status": "success",
                "message": "Leave policy updated",
            },
            status=status.HTTP_200_OK,
        )
