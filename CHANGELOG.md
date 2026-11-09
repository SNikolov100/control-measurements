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
- Added globally unique non-empty inventory numbers.
- Improved operator-facing validation for duplicate inventory numbers.
- Prevented customer-site changes through the standard equipment edit form.
- Prevented equipment-type changes through the standard equipment edit form.
- Applied equipment-type defaults when interval or duration values are left empty.
- Disabled new activity creation when the equipment status does not allow it.
- Added direct URL protection for unavailable activity-creation workflows.

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
- Prevented activities from starting without assigned qualified employees.
- Prevented another activity from starting while equipment is already under inspection.
- Aligned repair results across models, forms, and services.
- Added consistent equipment status transitions for repairs and reinspections.
- Standardized user-facing terminology around activities.

### User Interface
- Shared navigation menu added.
- Confirmation pages implemented.
- Custom 404 page added.
- Redirect workflow optimized for operators.
- Disabled activity actions now use a clear visual state.
- Equipment edit screens distinguish editable data from fixed registration data.
- Fixed customer-site and equipment-type information is displayed without editable controls.
- Added a reusable `status_badge` template tag.
- Added status icons for equipment, activities, results, and status history.
- Replaced repeated status conditions in templates with a shared component.
- Added consistent disabled button styling for unavailable workflow actions.
- Added warning messages when direct URLs attempt to bypass workflow restrictions.

#### Remaining Work

- Review HTML and CSS for duplicated markup and styling.
- Extract suitable shared template components and CSS utilities.
- Add consistent navigation-menu icons.
- Add controlled equipment suspension and restoration workflows.
- Add a controlled equipment decommission workflow.
- Add the `equipment.correct_equipment_type` permission and audit workflow.
- Add the custom user model and authentication.
- Add roles and permissions.
- Customize Django Admin.
- Complete the final BG/EN review.
- Add automated tests for workflow restrictions.
- Complete responsive review and final UI styling.
- Prepare the application for deployment.