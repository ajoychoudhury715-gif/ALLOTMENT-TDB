# Custom Role Structure & Permissions Design

## Current Proposed Role Structure

### 1. Admin
**Full System Access**
- ✅ View all schedules across all departments
- ✅ Edit all appointments and patient data
- ✅ Manage staff assignments and allocations
- ✅ Access all analytics and reports
- ✅ User management and role assignment
- ✅ System configuration and settings
- ✅ Time block management for all staff
- ✅ Clear/reset schedule functionality
- ✅ Backup and export capabilities

### 2. Doctor
**Department-Specific Professional Access**
- ✅ View own schedule and assigned patients
- ✅ Edit appointments where they are the assigned doctor
- ✅ Update patient status (WAITING, ARRIVED, ON GOING, DONE)
- ✅ View department-specific analytics
- ✅ Manage their own time blocks
- ✅ View assistant workload for their procedures
- ❌ Cannot edit other doctors' schedules
- ❌ Cannot access other departments

### 3. Assistant
**Operational Support Access**
- ✅ View assigned appointments (FIRST, SECOND, Third roles)
- ✅ Update patient status
- ✅ View own workload summary
- ✅ View department availability dashboard
- ✅ Update procedure notes
- ❌ Cannot create new appointments
- ❌ Cannot edit doctor assignments
- ❌ Cannot access analytics

### 4. Viewer
**Read-Only Monitoring Access**
- ✅ View all schedules in read-only mode
- ✅ View department availability
- ✅ View patient status updates
- ❌ Cannot edit any data
- ❌ Cannot access admin functions

## Customization Options

### Option A: Simplified 3-Role Structure
```
Admin (Full Access)
├── View/Edit Everything
├── User Management
└── System Settings

Staff (Operational Access)
├── View/Edit Schedules
├── Update Patient Status
└── Manage Own Assignments

Viewer (Read-Only)
└── View-Only Access
```

### Option B: Department-Specific Roles
```
Admin (System-Wide)
├── Global Admin
└── Department Admin

Doctor
├── Senior Doctor (can manage assistants)
├── Regular Doctor (standard access)
└── Resident Doctor (limited editing)

Assistant
├── Senior Assistant (can mentor others)
├── Lead Assistant (can override allocations)
└── Junior Assistant (standard access)

Support
├── Receptionist (can create appointments)
├── Coordinator (can reschedule)
└── Viewer (read-only)
```

### Option C: Task-Based Permissions
```
Granular Permission System:
- Can_View_Schedules
- Can_Edit_Appointments
- Can_Manage_Staff
- Can_Access_Analytics
- Can_Export_Data
- Can_Manage_Users
- Can_Clear_Schedule
- Can_Override_Allocations
```

## Customization Questions

Please let me know your preferred approach:

1. **Role Structure**: Which model works best for your organization?
   - 4-tier system (Admin/Doctor/Assistant/Viewer)
   - 3-tier system (Admin/Staff/Viewer)
   - Department-specific roles
   - Task-based granular permissions

2. **Department Access**: How should PROSTHO/ENDO departments be handled?
   - Complete isolation (users only see their department)
   - Cross-department viewing with editing restrictions
   - Department admins can see both departments

3. **Doctor Permissions**: What should doctors be able to do?
   - Edit only their own appointments?
   - Override assistant assignments?
   - Access department analytics?
   - Manage their own time blocks?

4. **Assistant Permissions**: What level of access for assistants?
   - Can they create new appointments?
   - Can they edit existing ones?
   - Can they see other assistants' schedules?
   - Can they manage their own time blocks?

5. **Special Requirements**: Any specific workflow needs?
   - Shift supervisor roles?
   - Emergency override permissions?
   - Temporary elevated access?
   - External contractor access?

## Recommended Customization

Based on a typical dental practice, I recommend:

**4-Tier System with Department Isolation:**
- **Admin**: Practice owner/manager
- **Doctor**: Each doctor manages their own schedule
- **Assistant**: Standard operational access within department
- **Viewer**: Reception/admin staff for monitoring

**Department Access:**
- Doctors and assistants primarily see their own department
- Admin can see everything
- Cross-department viewing for coordination purposes

**Key Permissions:**
- Doctors can edit their own appointments
- Assistants can update status but not create appointments
- Time block management based on role level
- Analytics access based on department and role level