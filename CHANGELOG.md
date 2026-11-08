# Changelog

## Current Development Phase

### Core
- Base models and reusable mixins implemented.
- Company and system settings implemented.
- BG/EN localization infrastructure added.

### Customers
- Customer management completed.
- Customer sites management completed.
- Customer contacts management completed.
- Slug URLs implemented.

### Equipment
- Equipment register completed.
- Equipment type management completed.
- Equipment image support added.
- Slug URLs implemented.
- Customer-site ownership is fixed after equipment registration.
- Equipment type is fixed in the standard edit workflow.
- Equipment status is managed through controlled activity transitions.
- Inspection interval and expected duration use equipment-type defaults when left empty.
- Equipment defaults now work consistently during both creation and editing.
- Inventory numbers are globally unique when provided.
- Multiple equipment records may remain without an inventory number.
- Equipment-type short names are required and unique.
- Validation messages were improved for operator use.
- Placeholders were prepared for BG/EN translation.

### Employees
- Employee management completed.
- Employee image support added.
- Specialty assignment implemented.

### Activities
- Activity lifecycle implemented.
- Assignment workflow implemented.
- Start workflow implemented.
- Completion workflow implemented.
- Cancellation workflow implemented.
- History tracking implemented.
- Activity start actions are disabled when no employees are assigned.
- Server-side validation prevents activities from starting without qualified active employees.
- Repair completion results were aligned across models, forms, and services.
- Successful repairs move equipment to the repeat-inspection workflow.
- Failed repairs keep equipment in the repair workflow.
- User-facing terminology was standardized around activities.

### User Interface
- Shared navigation menu added.
- Confirmation pages implemented.
- Custom 404 page added.
- Redirect workflow optimized for operators.
- Disabled activity actions now use a clear visual state.
- Equipment edit screens distinguish editable data from fixed registration data.
- Fixed customer-site and equipment-type information is displayed without editable controls.

#### Remaining Work

- Final review of equipment forms and translated field texts.
- Reusable status badge template tag.
- Status icons for equipment, activities, results, and history.
- Consistent navigation-menu icons.
- Advanced filters and sorting.
- Calendar view for activity planning and tracking.
- Custom user model and authentication.
- Roles and permissions.
- Controlled equipment-type correction with `equipment.correct_equipment_type`.
- Audit history for privileged corrections.
- Customized Django Admin.
- Final BG/EN review.
- Responsive review.
- Final quality assurance and automated testing.
- Deployment preparation.