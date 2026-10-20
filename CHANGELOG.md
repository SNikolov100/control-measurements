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
- protected deletion for customers and customer sites.
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

### Changed

- Moved shared company fields into `CompanyMixin`.
- Renamed `base_models.py` to `model_mixins.py`.
- Extended `CompanySettings` with shared company fields.
- Renamed `PkShortNameSlugMixin` to `AutoSlugMixin`.
- Generalized automatic slug generation for different model types.
- Equipment active state is now managed automatically from its status.
- The `DECOMMISSIONED` status also covers scrapped equipment.

### Project decisions

- Django Admin will not be used as the main application interface.
- The initial version will support a single user.
- User profiles, roles, and permissions will be added at a later stage.
- Simple templates will first be used to verify rendered data.
- The final HTML and CSS design will be implemented after the main
  functionality is complete.