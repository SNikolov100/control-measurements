# Control Measurements

Control Measurements is a Django application for managing equipment,
employees, inspections, calibration schedules, repairs, and upcoming
control measurements.

## Project status

The project is currently in an early development stage.

### Implemented so far

- Initial Django project structure
- `core` application
- Reusable `TimestampMixin`
- Reusable `SingleRecordMixin`
- `Specialty` model
- `CompanySettings` model
- `SystemSettings` model
- HEX color validation
- Phone number validation
- Initial calendar settings
- Workday configuration
- Inspection warning settings
- Inspection automation settings
- Reusable company and slug model mixins
- `customers` application
- `Customer` model
- `CustomerSite` model
- `CustomerContact` model
- Automatic slug generation from primary key and short name
- Customer site and contact relationships
- Primary customer contact validation
- Protected customer and site relationships


## Applications

### Implemented

- `core`
- `customers`

### Planned

- `equipment`
- `employees`
- `inspections`

## Development approach

The project will initially use simple Django forms, views, URLs, and
templates to verify the application logic and rendered data.

The complete visual interface, reusable template structure, CSS,
images, and responsive design will be implemented after the core
functionality is complete.

Django Admin is not used as the primary application interface.

The first version of the application is intended for a single user.
User profiles, roles, and permissions are planned for a later stage.

## Installation

Installation instructions will be added as the project develops.

## Documentation

Project documentation will be developed and updated together with the
source code.

## License

Copyright © 2026 slavi6. All rights reserved.

The source code is publicly available for evaluation and testing.

Commercial use, redistribution, sublicensing, sale, and incorporation
of this software into another product are not permitted without prior
written permission from the copyright holder.