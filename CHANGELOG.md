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
- Added a reusable text normalization mixin with configurable
  strip, uppercase, lowercase, title-case, and default-value rules.
- Added a shared delete confirmation form with an explicit
  confirmation checkbox.
- Added a reusable protected-delete view mixin.
- Added a shared base template for delete confirmation pages.
- Added reusable customer and customer-site parent view mixins.
- Added a reusable equipment registration mixin for creating the
  initial equipment status history.
- Added a reusable inspection action mixin for starting, completing,
  and cancelling activities.
- Added optional city and address fields to customer sites.
- Added fallback city and address values from the parent customer
  when the customer site values are empty.
- Added custom validation messages for specialty fields and activity
  forms.
- Added required fault descriptions when creating repair activities.
- Added required repair-work descriptions when completing repairs.
- Added required result notes for failed activities.

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
- Canceled active repairs move equipment to temporarily suspended.
- Canceled active reinspections return equipment to waiting for
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

### Changed

- Refactored repeated create, detail, update, delete, and nested-parent
  view logic into reusable mixins.
- Refactored repeated text normalization from individual models into
  a shared configurable model mixin.
- Refactored employee activation and deactivation into one atomic
  internal status-change operation.
- Refactored activity start, completion, and cancellation views to use
  shared action handling.
- Refactored equipment registration to create the initial status
  history through shared view behavior.
- Refactored specialty, customer contact, and equipment type deletion
  to use the shared confirmation workflow.
- Changed specialty listing from a function-based view to a
  class-based ListView.
- Changed equipment details to use the correct DetailView base class.
- Changed employee forms so active status is managed only through the
  controlled activation and deactivation workflow.
- Changed activity completion details to display actual start, actual
  end, result notes, and equipment status.
- Changed names of employees and customer contacts to title case
  during normalization.
- Changed emails to lowercase during normalization.
- Changed equipment serial and inventory numbers to uppercase during
  normalization.
- Changed an empty customer country to use Bulgaria as the default.
- Disabled browser-side form validation on the updated forms so
  Django validation messages are displayed consistently.

### Fixed

- Fixed tuple values caused by trailing commas in form fields,
  success URLs, and model Meta options.
- Fixed inconsistent form and view class naming in the customers
  application.
- Fixed activity completion views that could return None instead of
  an HTTP response.
- Fixed service ValidationError handling for confirmation forms
  without matching model fields.
- Fixed customer-site city and address display when values are
  inherited from the customer.
- Fixed duplicate-contact validation after text normalization.
- Fixed equipment detail view inheritance.
- Fixed technical activity-history values so human-readable labels
  are displayed.
- Fixed repair activities being created without a fault description.



### Project decisions

- Equipment belongs permanently to a customer site, not to a customer
  contact.
- A customer contact represents the person handing over equipment for
  a specific activity or intake.
- The customer-site page will become the main operational workspace.
- The planned intake workflow will allow the operator to select one
  active customer contact and multiple equipment items from the site.
- Missing equipment can be registered directly for the current
  customer site before activities are created.
- Equipment statuses are managed through activity start, completion,
  and cancellation operations rather than through a manual status
  interface.
- The next development stage will focus on the shared layout,
  navigation, HTML/CSS design, form presentation, search, filters,
  sorting, and pagination.