# Changelog

## [Unreleased]

### Added

- Introduced `Person` as the shared source of personal information for employees and associated user accounts.
- Added employee-request review actions to create an employee or link an approved account to an existing employee, with group selection.
- Added conflict-resolution choices during LINK: reviewers can choose the source for names and phone numbers independently, with explicit identity confirmation for differing names.
- Recorded LINK decisions, including selected name and phone sources, in `EmployeeHistory`.
- Expanded the employee list with position, user permission groups, active status, combined specialty/active filters, and search/pagination that preserve applicable filters.
- Added registration email confirmation and administrative reconsideration workflows. Reconsideration preserves registration status history and the previously rejected employee request when a new pending request is created.
- Added public About and Contacts pages.
- Added separate permissions for inspection creation, assignment, start, completion, cancellation, and access to all inspections.
- Added automated checks for permission changes, direct request authorization, inspection assignments, and employee linking in earlier development work; a complete regression run has not been confirmed for this update.

### Changed

- Made `Employee.person` required. Exposed `Employee.full_name`, `Employee.phone`, and `Employee.email` as read-only properties backed by `Person`.
- Updated employee CREATE, EDIT, and LINK workflows to work with the shared `Person` record and to retain relevant personal and employment information.
- Centralized route permissions so navigation, action buttons, and middleware apply consistent access rules. Group permissions are maintained through Django Admin.
- Scoped inspections to assigned employees unless a user has permission to see all inspections. Operators with the appropriate permissions can start and finish work for employees without accounts.
- Allowed company and system settings to be viewed with read-only access while requiring change permissions to save them.
- Updated registration/profile screens and displayed the signed-in username in navigation.
- Adopted a new development migration baseline after retiring the legacy database; regenerated initial migrations and retained the new `employees` follow-up migrations.

### Fixed

- Allowed a reviewer to resolve a LINK with a name conflict, a phone conflict, or both, rather than requiring manual edits solely to resolve differing phone numbers.
- Made employee searching case-insensitive for Cyrillic text on SQLite in the earlier implementation.
- Hid unauthorized actions and returned users to Home when they could save a change but could not open the usual destination.

### Removed

- Duplicate stored employee name, phone, and email fields; their values now come from `Person`.
- Obsolete development migration files superseded by the new baseline. The old database is not intended for migration using the current history.
- Automatic profile creation through Django signals. Approved users complete their profiles through the application.

## Earlier development

- Added company and system settings, reusable models and mixins, and Bulgarian and English localization infrastructure.
- Added customer, site, and contact management, along with employee records, photos, and specialty assignment.
- Added the equipment register, equipment types, images, and equipment-type defaults for inspection intervals and expected durations. Enforced uniqueness for supplied inventory numbers and kept the customer site and equipment type fixed in standard editing.
- Added activity creation, assignment, start, completion, cancellation, and status history. Applied equipment status and employee qualification checks and defined transitions for repairs and reinspections.
- Added shared navigation, confirmation pages, a custom 404 page, reusable form fields and status badges, and a single stylesheet. Configured WhiteNoise and cached template loading for production settings.
