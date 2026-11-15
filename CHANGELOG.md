# Changelog

## [Unreleased]

### Added

- Account registration with a required email address and optional username. Users can sign in with either credential.
- Registration approval and rejection, followed by personal profile completion for approved accounts.
- Employee link requests that let a superuser link an account to an existing employee record or create a new one and select an existing permission group.
- Public About and Contacts pages.
- Separate permissions for inspection creation, assignment, start, completion, cancellation, and access to all inspections.
- Automated checks for permission changes, direct request authorization, inspection assignments, and employee linking.

### Changed

- Centralized route permissions so navigation, action buttons, and middleware apply the same access rules. Group permissions are managed through Django Admin.
- Scoped inspections to the current employee's assignments unless the user has permission to see all inspections. Operators with the appropriate permissions can start and finish work assigned to employees without accounts.
- Allowed company and system settings to be viewed with read-only access while requiring change permissions to save them.
- Updated registration and profile screens and displayed the signed-in username in the navigation.

### Fixed

- Blocked employee linking when the account and employee email addresses differ. Filled an empty employee email from the account and required explicit confirmation for a name mismatch.
- Made employee search case-insensitive for Cyrillic text on SQLite.
- Hid actions that users lack permission to perform and returned users to Home when they could save a change but could not open the usual destination.

### Removed

- Automatic profile creation through Django signals. Approved users complete their profiles through the application.

## Earlier development

- Added company and system settings, reusable models and mixins, and Bulgarian and English localization infrastructure.
- Added customer, site, and contact management, along with employee records, photos, and specialty assignment.
- Added the equipment register, equipment types, images, and equipment-type defaults for inspection intervals and expected durations. Enforced uniqueness for supplied inventory numbers and kept the customer site and equipment type fixed in standard editing.
- Added activity creation, assignment, start, completion, cancellation, and status history. Applied equipment status and employee qualification checks and defined transitions for repairs and reinspections.
- Added shared navigation, confirmation pages, a custom 404 page, reusable form fields and status badges, and a single stylesheet. Configured WhiteNoise and cached template loading for production settings.
