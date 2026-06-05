"""
Family Details Serializers for Admin Side - Get and Edit Only.

Handles serialization of employee family member data for:
- GET: Retrieve all family members for an employee
- PATCH: Update family member details

SQL injection protection through Django ORM parametrized queries.
"""

from rest_framework import serializers
from apps.employees.models.family import EmployeeFamilyMember


class FamilyMemberSerializer(serializers.ModelSerializer):
    """
    Serializer for displaying and updating family members on admin side.
    Shows all family details with masters populated.
    """
    
    # Master details as nested objects
    relation_label = serializers.CharField(source='relation.label', read_only=True)
    gender_label = serializers.CharField(source='gender.label', read_only=True, allow_null=True)
    occupation_label = serializers.CharField(source='occupation.label', read_only=True, allow_null=True)
    blood_group_label = serializers.CharField(source='blood_group.label', read_only=True, allow_null=True)
    nationality_label = serializers.CharField(source='nationality.label', read_only=True, allow_null=True)
    
    # Computed fields
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = EmployeeFamilyMember
        fields = [
            'id',
            'first_name',
            'last_name',
            'full_name',
            'date_of_birth',
            'relation',
            'relation_label',
            'gender',
            'gender_label',
            'occupation',
            'occupation_label',
            'blood_group',
            'blood_group_label',
            'nationality',
            'nationality_label',
            'mobile_no',
            'email',
            'is_dependent',
            'is_nominee',
            'is_active',
        ]
        read_only_fields = ['id', 'full_name']
    
    def get_full_name(self, obj):
        if obj.first_name and obj.last_name:
            return f"{obj.first_name} {obj.last_name}"
        return obj.first_name or ""
