# Changelog

All notable changes to the Control Measurements project will be
documented in this file.

## Unreleased

### Added

- Initial Django project structure
- `core` application
- `TimestampMixin`
- `SingleRecordMixin`
- `Specialty` model
- `CompanySettings` model
- `SystemSettings` model
- HEX color validator
- Phone number validator
- Calendar period settings
- Workday settings
- Inspection warning settings
- Inspection automation settings

### Project decisions

- Django Admin will not be used as the main application interface.
- The initial version will support a single user.
- User profiles, roles, and permissions will be added at a later stage.
- Simple templates will first be used to verify rendered data.
- The final HTML and CSS design will be implemented after the main
  functionality is complete.