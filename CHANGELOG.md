# Changelog

All notable changes to the Control Measurements project will be
documented in this file.

## Unreleased

### Added

- Added reusable `CompanyMixin`.
- Added reusable `PkShortNameSlugMixin`.
- Added the `customers` application.
- Added the `Customer` model.
- Added the `CustomerSite` model.
- Added the `CustomerContact` model.
- Added automatic slug generation from primary key and short name.
- Added customer-to-site and site-to-contact relationships.
- Added validation for one active primary contact per customer site.
- Added validation preventing inactive contacts from being primary.
- Added protected deletion for customers and customer sites.
- Added the `equipment` application.
- Added the `EquipmentType` model.
- Added the `Equipment` model.
- Added the `EquipmentStatusHistory` model.
- Added protected relationships to specialties and customer sites.
- Added configurable default inspection intervals for equipment types.
- Added individual inspection intervals for concrete equipment.
- Added estimated inspection durations.
- Added automatic normalization of serial and inventory numbers.
- Added unique serial number validation.
- Added automatic equipment slug generation.
- Added equipment lifecycle statuses.
- Added automatic synchronization between equipment status and active state.
- Added atomic equipment status changes.
- Added chronological equipment status history.
- Added validation preventing zero inspection intervals and durations.
- Added the `employees` application.
- Added the `Employee` model.
- Added the `EmployeeHistory` model.
- Added Unicode employee slug generation from primary key and full name.
- Added normalization of employee names and contact data.
- Added the many-to-many relationship between employees and specialties.
- Added chronological employee history.
- Added employee activation and deactivation support.
- Added protected deletion for employees with history.
- Added prevention of duplicate employee-specialty relationships.
- Added the `inspections` application.
- Added the `Inspection` model.
- Added calibration, periodic inspection, extraordinary inspection,
  repair, and reinspection activity types.
- Added multiple employee assignments per inspection.
- Added customer contact assignment per inspection.
- Added received, due, planned, actual start, and actual end dates.
- Added estimated inspection duration.
- Added inspection status transitions.
- Added passed and failed inspection results.
- Added separate result handling for repair activities.
- Added validation of assigned employee activity and specialty.
- Added prevention of simultaneous activities for one equipment item.
- Added atomic inspection start, completion, and cancellation services.
- Added automatic synchronization between inspections and equipment
  statuses.
- Added mandatory cancellation reasons.
- Added the first functional CRUD interface for specialties.
- Added specialty list, create, edit, and delete views.
- Added simple templates for validating rendered specialty data.
- Added protected specialty deletion with related-record information.
- Added user-friendly deletion error messages.
- Added the first shared `base.html` template.
- Added the initial Home page and application navigation.
- Added functional interfaces for company and system settings.
- Added reusable single-record form view behavior for settings.
- Added CRUD interfaces for equipment types.
- Added equipment registry, creation, editing, and detail views.
- Added automatic equipment defaults from the selected equipment type.
- Added automatic initial equipment status history on registration.
- Added equipment status change form and view.
- Added equipment status history to the equipment detail page.
- Added customer list, creation, editing, and detail views.
- Added nested customer site creation, editing, and detail views.
- Added customer site validation through nested customer URLs.
- Added customer site equipment and contact sections.
- Added customer contact creation, editing, details, duplicate
  validation, and protected deletion.
- Added equipment creation directly from a customer site.
- Added employee list, creation, editing, details, specialties,
  activation, deactivation, and history.
- Added the activities list and activity detail page.
- Added activity creation for specific equipment.
- Added employee assignment to pending activities.
- Added controlled activity start, completion, and cancellation
  workflows.
- Added passed and failed activity results.
- Added repair and reinspection workflows.
- Added automatic equipment status changes from activity operations.
- Added validation preventing simultaneous activities in progress
  for the same equipment.
- Added cancellation reasons and actual activity timestamps.

### Changed

- Moved shared company fields into `CompanyMixin`.
- Renamed `base_models.py` to `model_mixins.py`.
- Extended `CompanySettings` with shared company fields.
- Renamed `PkShortNameSlugMixin` to `AutoSlugMixin`.
- Generalized automatic slug generation for different model types.
- Equipment active state is now managed automatically from its status.
- The `DECOMMISSIONED` status also covers scrapped equipment.
- Employee data is normalized before model field validation.
- Employee specialties are managed through a direct many-to-many relationship.
- Inspection workflow operations are organized in `services.py`.
- Pending activity cancellation now preserves the current equipment
  status.
- Cancelled active repairs move equipment to temporarily suspended.
- Cancelled active reinspections return equipment to waiting for
  reinspection.
- Specialty deletion now prevents removal of specialties used by
  equipment types or employees.
- Existing specialty templates now inherit from the shared base template.
- Company and system settings now use a shared single-record form view mixin.
- Equipment status changes are performed through the model status method
  instead of direct field editing.
- Customer sites are now created and edited in the context of their parent
  customer.
- Customer site URLs now validate the customer-to-site relationship.
- Equipment statuses are now managed automatically through activity
  start, completion, and cancellation operations.
- Manual equipment status changes were removed from the interface.
- New activities are registered before employees are assigned.
- Employee assignment is now performed separately for pending
  activities.
- Customer contacts are no longer required when creating an activity.
- Equipment activity creation is blocked while another activity for
  the same equipment is in progress.
- Employee activation and deactivation now create employee history
  records.

### Project decisions

- Django Admin will not be used as the main application interface.
- The initial version will support a single user.
- User profiles, roles, and permissions will be added at a later stage.
- Simple templates will first be used to verify rendered data.
- The final HTML and CSS design will be implemented after the main
  functionality is complete.
- The calendar will be implemented after the main functional interfaces are
  complete.
- Repeated view logic will be reviewed and refactored into reusable mixins
  after the functional workflows are complete.
- Required fields, help text, widgets, and final form styling will be added
  during the final interface design stage.
- Phone number validation will be reviewed to prevent excessively long
  numbers.
- The current feature set will be used as the first functional testing
  version.
- Further business features will be postponed until the existing code
  is refactored and the main interface is redesigned.
- Search, filters, and pagination will be added to the equipment and
  activity lists.
- Repeated view, form, and deletion logic will be reviewed for reusable
  mixins and base classes.
- CSS will be moved to dedicated static files during the interface
  redesign.