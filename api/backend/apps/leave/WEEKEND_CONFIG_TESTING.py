"""
API Testing Guide for Weekend Configuration Endpoints.

This document provides comprehensive testing instructions for the Weekend Configuration API.
"""

# ============================================================================
# WEEKEND CONFIGURATION API - TESTING GUIDE
# ============================================================================
# 
# Base URL: http://localhost:8000/api/leave/admin/weekends/config/
#
# All endpoints require:
#   - Authentication: Bearer Token
#   - Admin/HR Role
#
# ============================================================================

# 1. SEED THE DATA
# ============================================================================
# Before testing, populate the database with test weekend configurations:
#
#   python manage.py shell
#   from apps.leave.seed_weekends_config import seed_weekend_configs
#   seed_weekend_configs(schema_name='public')
#
# Or from command line:
#   python apps/leave/seed_weekends_config.py --schema public

# ============================================================================
# 2. GET WEEKEND CONFIGURATION (LIST)
# ============================================================================
# 
# Endpoint: GET /api/admin/weekends/config/
# 
# Description: Retrieve all weekend configurations with optional filtering
#
# Query Parameters (Optional):
#   - branch_id: Filter by branch UUID
#   - is_active: Filter by active status (true/false)
#   - page: Page number for pagination (default: 1)
#   - page_size: Items per page (default: 10)
#
# Example cURL:
# ============================================================================
#
# Basic request:
# curl -X GET "http://localhost:8000/api/leave/admin/weekends/config/" \
#   -H "Authorization: Bearer YOUR_TOKEN" \
#   -H "Content-Type: application/json"
#
# Filter by branch:
# curl -X GET "http://localhost:8000/api/leave/admin/weekends/config/?branch_id=a1b2c3d4-e5f6-7890-abcd-ef1234567890" \
#   -H "Authorization: Bearer YOUR_TOKEN" \
#   -H "Content-Type: application/json"
#
# Filter by active status:
# curl -X GET "http://localhost:8000/api/leave/admin/weekends/config/?is_active=true" \
#   -H "Authorization: Bearer YOUR_TOKEN" \
#   -H "Content-Type: application/json"
#
# Response (200 OK):
# ============================================================================
# {
#   "status": "success",
#   "data": [
#     {
#       "id": "550e8400-e29b-41d4-a716-446655440000",
#       "branch": "220e8400-e29b-41d4-a716-446655440111",
#       "branch_name": "Main Office",
#       "day_of_week": 6,
#       "day_of_week_display": "Sunday",
#       "week_frequency": "all",
#       "is_active": true
#     },
#     {
#       "id": "550e8400-e29b-41d4-a716-446655440001",
#       "branch": "220e8400-e29b-41d4-a716-446655440111",
#       "branch_name": "Main Office",
#       "day_of_week": 5,
#       "day_of_week_display": "Saturday",
#       "week_frequency": "all",
#       "is_active": true
#     }
#   ],
#   "total": 2
# }

# ============================================================================
# 3. CREATE WEEKEND CONFIGURATION
# ============================================================================
#
# Endpoint: POST /api/admin/weekends/config/
#
# Description: Create a new weekend configuration
#
# Request Body:
# {
#   "branch": "uuid-of-branch",
#   "day_of_week": 6,              # 0=Monday, 1=Tuesday, ..., 6=Sunday
#   "week_frequency": "all",       # all, first, second, third, fourth, last
#   "is_active": true
# }
#
# Example cURL:
# ============================================================================
#
# curl -X POST "http://localhost:8000/api/leave/admin/weekends/config/" \
#   -H "Authorization: Bearer YOUR_TOKEN" \
#   -H "Content-Type: application/json" \
#   -d '{
#     "branch": "220e8400-e29b-41d4-a716-446655440111",
#     "day_of_week": 6,
#     "week_frequency": "all",
#     "is_active": true
#   }'
#
# Response (201 CREATED):
# ============================================================================
# {
#   "status": "success",
#   "data": {
#     "id": "550e8400-e29b-41d4-a716-446655440002",
#     "branch": "220e8400-e29b-41d4-a716-446655440111",
#     "branch_name": "Main Office",
#     "day_of_week": 6,
#     "day_of_week_display": "Sunday",
#     "week_frequency": "all",
#     "week_frequency_display": "All",
#     "is_active": true,
#     "created_at": "2024-05-18T10:30:00Z"
#   }
# }

# ============================================================================
# 4. UPDATE WEEKEND CONFIGURATION
# ============================================================================
#
# Endpoint: PUT /api/admin/weekends/config/{config_id}/
#
# Description: Update an existing weekend configuration
#
# Path Parameters:
#   - config_id: UUID of the configuration to update
#
# Request Body (all fields optional):
# {
#   "day_of_week": 5,              # 0=Monday, 1=Tuesday, ..., 5=Saturday
#   "week_frequency": "second",    # all, first, second, third, fourth, last
#   "is_active": false
# }
#
# Example cURL:
# ============================================================================
#
# curl -X PUT "http://localhost:8000/api/leave/admin/weekends/config/550e8400-e29b-41d4-a716-446655440002/" \
#   -H "Authorization: Bearer YOUR_TOKEN" \
#   -H "Content-Type: application/json" \
#   -d '{
#     "day_of_week": 5,
#     "week_frequency": "second",
#     "is_active": true
#   }'
#
# Response (200 OK):
# ============================================================================
# {
#   "status": "success",
#   "data": {
#     "id": "550e8400-e29b-41d4-a716-446655440002",
#     "branch": "220e8400-e29b-41d4-a716-446655440111",
#     "branch_name": "Main Office",
#     "day_of_week": 5,
#     "day_of_week_display": "Saturday",
#     "week_frequency": "second",
#     "week_frequency_display": "Second",
#     "is_active": true,
#     "created_at": "2024-05-18T10:30:00Z"
#   }
# }

# ============================================================================
# 5. DELETE WEEKEND CONFIGURATION
# ============================================================================
#
# Endpoint: DELETE /api/admin/weekends/config/{config_id}/
#
# Description: Delete a weekend configuration
#
# Path Parameters:
#   - config_id: UUID of the configuration to delete
#
# Example cURL:
# ============================================================================
#
# curl -X DELETE "http://localhost:8000/api/leave/admin/weekends/config/550e8400-e29b-41d4-a716-446655440002/" \
#   -H "Authorization: Bearer YOUR_TOKEN" \
#   -H "Content-Type: application/json"
#
# Response (204 NO CONTENT):
# ============================================================================
# {
#   "status": "success",
#   "message": "Weekend configuration deleted successfully"
# }

# ============================================================================
# DAY OF WEEK MAPPING
# ============================================================================
# 0 = Monday
# 1 = Tuesday
# 2 = Wednesday
# 3 = Thursday
# 4 = Friday
# 5 = Saturday
# 6 = Sunday

# ============================================================================
# WEEK FREQUENCY OPTIONS
# ============================================================================
# all    = All weeks (e.g., every Sunday)
# first  = First week of the month
# second = Second week of the month
# third  = Third week of the month
# fourth = Fourth week of the month
# last   = Last week of the month

# ============================================================================
# ERROR RESPONSES
# ============================================================================
#
# 403 Forbidden (Admin/HR role required):
# {
#   "status": "error",
#   "detail": "Admin or HR role required."
# }
#
# 400 Bad Request (Validation error):
# {
#   "non_field_errors": [
#     "This weekend configuration already exists for the selected branch."
#   ]
# }
#
# 404 Not Found:
# {
#   "detail": "Not found."
# }

# ============================================================================
# USAGE EXAMPLES IN PYTHON
# ============================================================================
"""
import requests

BASE_URL = "http://localhost:8000/api/leave"
HEADERS = {
    "Authorization": "Bearer YOUR_TOKEN",
    "Content-Type": "application/json"
}

# Get all weekend configurations
def get_weekend_configs():
    response = requests.get(
        f"{BASE_URL}/admin/weekends/config/",
        headers=HEADERS
    )
    return response.json()

# Create a new weekend configuration
def create_weekend_config(branch_id, day_of_week, week_frequency):
    payload = {
        "branch": branch_id,
        "day_of_week": day_of_week,
        "week_frequency": week_frequency,
        "is_active": True
    }
    response = requests.post(
        f"{BASE_URL}/admin/weekends/config/",
        json=payload,
        headers=HEADERS
    )
    return response.json()

# Update weekend configuration
def update_weekend_config(config_id, day_of_week, week_frequency):
    payload = {
        "day_of_week": day_of_week,
        "week_frequency": week_frequency,
        "is_active": True
    }
    response = requests.put(
        f"{BASE_URL}/admin/weekends/config/{config_id}/",
        json=payload,
        headers=HEADERS
    )
    return response.json()

# Delete weekend configuration
def delete_weekend_config(config_id):
    response = requests.delete(
        f"{BASE_URL}/admin/weekends/config/{config_id}/",
        headers=HEADERS
    )
    return response.status_code

# Example usage
if __name__ == "__main__":
    # Get configs
    configs = get_weekend_configs()
    print(configs)
    
    # Create config
    branch_id = "220e8400-e29b-41d4-a716-446655440111"
    new_config = create_weekend_config(branch_id, 6, "all")
    print(new_config)
"""

# ============================================================================
# TESTING CHECKLIST
# ============================================================================
# 
# [ ] GET /api/admin/weekends/config/ - List all configurations
# [ ] GET /api/admin/weekends/config/?branch_id=<uuid> - Filter by branch
# [ ] GET /api/admin/weekends/config/?is_active=true - Filter by active status
# [ ] POST /api/admin/weekends/config/ - Create new configuration
# [ ] PUT /api/admin/weekends/config/<config_id>/ - Update configuration
# [ ] DELETE /api/admin/weekends/config/<config_id>/ - Delete configuration
# [ ] Verify non-admin users get 403 Forbidden
# [ ] Verify duplicate configurations are prevented
# [ ] Verify pagination works correctly
# [ ] Verify day_of_week validation (0-6)

print("Weekend Configuration API Testing Guide - Ready for use!")
