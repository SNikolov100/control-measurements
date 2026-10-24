# Control Measurements

Control Measurements is a Django application for managing customers,
equipment, employees, inspections, calibration schedules, repairs,
and upcoming control measurements.

## Project status

The Python foundation has been refactored after completion of the
first functional testing version.

Repeated model normalization, nested parent loading, delete
confirmation, equipment registration history, and activity action
handling have been moved into reusable base classes and mixins.

The main functional workflows remain operational after the
refactoring and have been tested again.

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

### Refactored behavior

- Customer, customer-site, and customer-contact values use shared text
  normalization.
- Email addresses are stored in lowercase.
- Employee and contact names use title-case normalization.
- Customer sites may define their own city and address.
- Empty customer-site city and address values fall back to the parent
  customer values.
- Nested URLs verify the complete customer-to-site-to-contact
  relationship.
- Contact deletion uses shared confirmation and protected-delete
  behavior.

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

### Refactored behavior

- Equipment types and concrete equipment use shared text
  normalization.
- Serial and inventory numbers are normalized to uppercase.
- Initial equipment status history is created through shared
  registration behavior.
- Equipment detail pages use the correct generic DetailView.
- Equipment type deletion uses the shared protected confirmation
  workflow.

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

### Refactored behavior

- Employee information uses shared text normalization.
- Employee names use title-case normalization.
- Email addresses are stored in lowercase.
- Activation and deactivation are atomic operations.
- Every successful activity-status change creates an employee-history
  record.
- Active status is not directly editable through the ordinary employee
  form.

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

### Refactored behavior

- Activity start, completion, and cancellation use shared action-view
  behavior.
- Business transitions remain implemented in service functions.
- Service validation errors are displayed as form errors instead of
  technical error pages.
- Failed activities require result notes.
- Repair creation requires a fault or repair reason.
- Repair completion requires a description of the performed work.
- Activity details display actual timestamps, result notes, equipment
  status, assigned employees, and cancellation information.

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

<details>
<summary><strong>Current operational workflow</strong></summary>

The primary operational hierarchy is:

Customer
→ Customer site
→ Customer contact
→ Equipment
→ Activity
→ Assigned employees
→ Result and history

Equipment belongs to a customer site. A customer contact may be
recorded as the person handing over equipment for a specific activity,
but the equipment does not belong permanently to that contact.

The planned customer-site intake workflow will allow an operator to:

1. open a customer and one of its sites;
2. select one active customer contact;
3. mark one or more registered equipment items as received;
4. register missing equipment directly for the current site;
5. create an individual activity for every selected equipment item;
6. automatically associate the customer, site, contact, and equipment
   with the created activities.
</details>

<details>
<summary><strong>Shared architecture</strong></summary>

The current shared infrastructure includes:

- configurable text normalization for strip, uppercase, lowercase,
  title case, and default text values;
- shared delete confirmation forms;
- protected-delete handling;
- shared delete confirmation templates;
- customer and customer-site parent view mixins;
- shared equipment registration history behavior;
- shared inspection action handling;
- atomic employee activation and deactivation;
- service-based equipment activity status transitions.

</details>

## Development approach

The next stage will focus on the user interface and operational
navigation:

- a stable shared layout for all templates;
- permanent navigation with an always-available Home link;
- customer-site pages as the main operational workspace;
- dedicated static CSS files;
- reusable form and table components;
- clear labels, placeholders, help text, and custom error messages;
- required and optional field indicators;
- breadcrumbs and contextual back navigation;
- equipment and activity search;
- combinable filters;
- column sorting;
- pagination that preserves active GET parameters;
- responsive presentation of lists, forms, details, and status
  histories.

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