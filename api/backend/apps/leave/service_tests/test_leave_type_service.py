"""
Tests for LeaveTypeService
"""
import pytest
from django_tenants.test.cases import TenantTestCase
from rest_framework.exceptions import ValidationError, NotFound
from ..services import LeaveTypeService
from ..models import LeaveType


class TestLeaveTypeService(TenantTestCase):
    """Test cases for LeaveTypeService"""

    @classmethod
    def setup_tenant(cls, tenant):
        tenant.company_name = "Test Tenant"
        tenant.slug = "testtenant"
        tenant.schema_name = cls.get_test_schema_name()

    @classmethod
    def setup_domain(cls, domain):
        domain.domain = cls.get_test_tenant_domain()

    def test_create_leave_type(self):
        """Test creating a new leave type"""
        data = {
            'code': 'PL',
            'name': 'Privilege Leave',
            'max_days_per_year': 20
        }
        
        leave_type = LeaveTypeService.create_leave_type(data)
        
        assert leave_type.code == 'PL'
        assert leave_type.name == 'Privilege Leave'
        assert leave_type.max_days_per_year == 20

    def test_create_leave_type_duplicate_code(self):
        """Test cannot create leave type with duplicate code"""
        data = {
            'code': 'SL',
            'name': 'Sick Leave',
            'max_days_per_year': 10
        }
        
        LeaveTypeService.create_leave_type(data)
        
        with pytest.raises(ValidationError):
            LeaveTypeService.create_leave_type(data)

    def test_get_all_leave_types(self):
        """Test fetching all leave types"""
        # Create multiple leave types
        for i in range(3):
            LeaveTypeService.create_leave_type({
                'code': f'LT{i}',
                'name': f'Leave Type {i}',
                'max_days_per_year': 10 + i
            })
        
        leave_types = LeaveTypeService.get_all_leave_types()
        assert leave_types.count() >= 3

    def test_get_leave_type_by_id(self):
        """Test fetching leave type by ID"""
        data = {
            'code': 'ML',
            'name': 'Maternity Leave',
            'max_days_per_year': 90
        }
        
        created = LeaveTypeService.create_leave_type(data)
        fetched = LeaveTypeService.get_leave_type_by_id(str(created.id))
        
        assert fetched.id == created.id
        assert fetched.code == 'ML'

    def test_update_leave_type(self):
        """Test updating a leave type"""
        data = {
            'code': 'CL',
            'name': 'Casual Leave',
            'max_days_per_year': 12
        }
        
        leave_type = LeaveTypeService.create_leave_type(data)
        
        update_data = {
            'name': 'Casual Leave (Updated)',
            'max_days_per_year': 15
        }
        
        updated = LeaveTypeService.update_leave_type(str(leave_type.id), update_data)
        
        assert updated.name == 'Casual Leave (Updated)'
        assert updated.max_days_per_year == 15

    def test_soft_delete_leave_type(self):
        """Test soft deleting a leave type"""
        data = {
            'code': 'UL',
            'name': 'Unpaid Leave',
            'max_days_per_year': 0
        }
        
        leave_type = LeaveTypeService.create_leave_type(data)
        leave_type_id = str(leave_type.id)
        
        LeaveTypeService.soft_delete_leave_type(leave_type_id)
        
        # Should not be fetchable
        with pytest.raises(NotFound):
            LeaveTypeService.get_leave_type_by_id(leave_type_id)

    def test_restore_leave_type(self):
        """Test restoring a soft-deleted leave type"""
        data = {
            'code': 'RL',
            'name': 'Restored Leave',
            'max_days_per_year': 5
        }
        
        leave_type = LeaveTypeService.create_leave_type(data)
        leave_type_id = str(leave_type.id)
        
        LeaveTypeService.soft_delete_leave_type(leave_type_id)
        restored = LeaveTypeService.restore_leave_type(leave_type_id)
        
        assert restored.is_active is True

    def test_filter_leave_types(self):
        """Test filtering leave types"""
        # Create test leave types
        LeaveTypeService.create_leave_type({
            'code': 'SL1',
            'name': 'Sick Leave Type 1',
            'max_days_per_year': 10
        })
        LeaveTypeService.create_leave_type({
            'code': 'PL1',
            'name': 'Personal Leave Type 1',
            'max_days_per_year': 5
        })
        
        filters = {'name': 'Sick'}
        results = LeaveTypeService.get_all_leave_types(filters=filters)
        
        assert all('Sick' in lt.name for lt in results)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
