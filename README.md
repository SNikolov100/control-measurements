# Control Measurements

Control Measurements is a Django application for managing customers,
equipment, employees, inspections, calibration schedules, repairs,
and upcoming control measurements.

## Project status

The project now contains a complete initial workflow for registering
equipment and managing its control activities.

The current version is ready for functional testing before code
refactoring, interface redesign, search, filters, and pagination are
introduced.

### Implemented applications

- `core`
- `customers`
- `equipment`
- `employees`
- `inspections`

## Application details

<details>
<summary><strong>core application</strong></summary>

The `core` application contains shared models, global settings,
reusable model mixins, and common validators.

### Models

- `Specialty`
- `CompanySettings`
- `SystemSettings`

### Reusable model mixins

- `TimestampMixin`
- `SingleRecordMixin`
- `CompanyMixin`
- `AutoSlugMixin`

### Validators

- HEX color validator
- Phone number validator

### Functional interface

- Specialty deletion
- Protected deletion for specialties currently in use
- Shared base template
- Initial Home page
- Main application navigation
- Company settings form
- System settings form
- Specialty list, creation, editing, and protected deletion

### System settings

- Default calendar period
- Weekend visibility
- Workday start and end times
- Inspection warning periods
- Overdue inspection alerts
- Inspection automation settings

</details>

<details>
<summary><strong>customers application</strong></summary>

The `customers` application manages customer companies, customer
sites, and contact persons.

### Models

- `Customer`
- `CustomerSite`
- `CustomerContact`

### Relationships

```text
Customer
`-- CustomerSite
    `-- CustomerContact
```

### Implemented functionality

- Automatic Unicode slug generation
- Unique company and short names
- Customer-to-site relationships
- Site-to-contact relationships
- Multiple active contacts per customer site
- One active primary contact per customer site
- Validation preventing inactive contacts from being primary
- Protected deletion of customers and customer sites
- Phone and email validation

### Functional interface

- Customer list
- Customer creation
- Customer editing
- Customer detail page
- Nested customer site creation
- Nested customer site editing
- Customer site detail page
- Customer-to-site URL relationship validation
- Customer site sections for contacts and equipment
</details>

<details>
<summary><strong>equipment application</strong></summary>

The `equipment` application manages equipment types, concrete
equipment items, inspection intervals, lifecycle statuses, and
equipment status history.

### Models

- `EquipmentType`
- `Equipment`
- `EquipmentStatusHistory`

### Relationships

```text
Specialty
`-- EquipmentType
    `-- Equipment
        `-- EquipmentStatusHistory

CustomerSite
`-- Equipment
```

### Implemented functionality

- Equipment classification by specialty
- Default inspection intervals for equipment types
- Individual inspection intervals for concrete equipment
- Estimated inspection duration
- Unique serial number validation
- Serial and inventory number normalization
- Automatic Unicode slug generation
- Equipment lifecycle statuses
- Automatic synchronization between status and active state
- Atomic equipment status changes
- Chronological equipment status history
- Protected equipment relationships

### Functional interface

- Equipment type list
- Equipment type creation and editing
- Protected equipment type deletion
- Equipment registry
- Equipment creation and editing
- Equipment detail page
- Automatic default interval and duration values
- Automatic initial equipment history
- Controlled equipment status changes
- Equipment status history display
</details>

<details>
<summary><strong>employees application</strong></summary>

The `employees` application manages employee records, employee
specialties, and employee history.

### Models

- `Employee`
- `EmployeeHistory`

### Relationships

```text
Employee
|-- many Specialties
`-- many EmployeeHistory records
```

### Implemented functionality

- Employee profile data
- Unicode slug generation from primary key and full name
- Employee name and contact-data normalization
- Phone and email validation
- Many-to-many relationship between employees and specialties
- Prevention of duplicate specialty relationships
- Employee activation and deactivation
- Chronological employee history
- Protected deletion of employees with history

### Functional interface

- Employee list
- Employee creation and editing
- Employee detail page
- Multiple specialty assignment
- Controlled employee activation and deactivation
- Employee activity history
</details>

<details>
<summary><strong>inspections application</strong></summary>

The `inspections` application manages equipment activities, assigned
employees, scheduling, results, cancellation, and equipment status
changes.

### Models

- `Inspection`

### Inspection types

- Calibration
- Periodic inspection
- Extraordinary inspection
- Repair
- Reinspection after repair

### Relationships

```text
Equipment
`-- many Inspections
    |-- many assigned Employees
    `-- optional CustomerContact
```

### Implemented functionality

- Multiple employees per activity
- Employee activity and specialty validation before starting
- Prevention of simultaneous active activities for one equipment item
- Planned, actual, and due dates
- Estimated activity duration
- Controlled inspection status transitions
- Automatic start and end timestamps
- Passed and failed inspection results
- Separate repair workflow without an inspection result
- Automatic equipment status synchronization
- Successful inspections return equipment to service
- Failed inspections move equipment to repair
- Completed repairs move equipment to reinspection
- Required cancellation reason
- Cancellation behavior based on activity type and current status
- Atomic start, completion, and cancellation operations
</details>

### Functional interface

- Activity list
- Activity creation for specific equipment
- Separate employee assignment
- Activity detail page
- Controlled activity start
- Controlled activity completion
- Passed and failed results
- Repair workflow
- Reinspection after repair
- Activity cancellation with a required reason
- Automatic actual start and end timestamps
- Automatic equipment status synchronization
- Prevention of simultaneous activities in progress for the same
  equipment

<details>
<summary><strong>Current data structure</strong></summary>

```text
Customer
`-- CustomerSite
    |-- CustomerContact
    `-- Equipment
        |-- EquipmentStatusHistory
        `-- Inspection
            `-- many Employees

Specialty
|-- many EquipmentTypes
`-- many Employees

EquipmentType
`-- many Equipment items

Employee
`-- many EmployeeHistory records
```

</details>

## Development approach

The next development stage will focus on:

- refactoring repeated view and form logic;
- reusable mixins and base classes;
- shared template components;
- dedicated CSS static files;
- required-field indicators and improved form rendering;
- search and filtering;
- pagination for larger lists;
- preparation of the first polished testing version.

## Installation

Detailed installation instructions will be added as the project
develops.

The current local setup requires:

- Python
- Django
- A virtual environment
- The dependencies from `requirements.txt`
- A local `.env` file based on `.env.example`
- Applied Django migrations

## Documentation

Project documentation will be developed and updated together with the
source code.

The project currently uses:

- `README.md` for the project overview
- `CHANGELOG.md` for notable development changes
- Git commits for the detailed development history

More detailed technical documentation will later be organized in a
separate `docs/` directory.

## License

Copyright (c) 2026 slavi6. All rights reserved.

The source code is publicly available for evaluation and testing.

Commercial use, redistribution, sublicensing, sale, and incorporation
of this software into another product are not permitted without prior
written permission from the copyright holder.