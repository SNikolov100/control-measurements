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

### Project decisions

- Django Admin will not be used as the main application interface.
- The initial version will support a single user.
- User profiles, roles, and permissions will be added at a later stage.
- Simple templates will first be used to verify rendered data.
- The final HTML and CSS design will be implemented after the main
  functionality is complete.