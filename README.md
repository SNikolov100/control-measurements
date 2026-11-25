# Control Measurements

Control Measurements is a Django application for managing customers, equipment, employees, and scheduled control measurements. The project is under active development.

## What the application does

| Area | Features |
| --- | --- |
| Customers | Manage customer records, sites, and site contacts. |
| Equipment | Register equipment by customer site, manage equipment types, and track equipment status. Inspection intervals and expected durations can use defaults from the equipment type. |
| Employees | Manage employee records, specialties, active status, and optional links to user accounts. Search and filter employees by specialty and active status. An employee can exist without a login. |
| Activities | Create and assign periodic and extraordinary inspections, repairs, and reinspections. Start, interrupt, resume, complete or cancel activities. Starting or resuming requires all assigned employees to be active, qualified and free. Activity history records actions, actors and assignment snapshots. |
| Settings | Manage company details, system settings, and specialties. Company and system settings can be exposed as read-only where permissions allow. |

## People, accounts, and access

### Shared personal data

`Person` is the central record for personal information, including names and contact details. An `Employee` must reference a `Person`; a `Person` may also be associated with an `AppUser` account. An employee record does not require an account.

The employee's `full_name`, `phone`, and `email` are read-only properties derived from the linked `Person`, rather than separate stored fields on `Employee`. This keeps personal information in one place.

### Registration and employee requests

Visitors can access the public pages (including About and Contacts), register, and sign in. Users can sign in using their email address or username. The registration process includes email confirmation and administrative approval or rejection. Approved accounts complete their personal profile before receiving full application access.

A superuser reviews an employee request and can either **CREATE** a new employee record or **LINK** the account to an existing employee. An existing permission group can be selected during review. Rejected registration and employee requests support an administrative **Reconsider** workflow; the employee-request workflow preserves the earlier decision in its history.

When linking, the application checks personal-data conflicts. For different names and/or phone numbers, the reviewer can select which record's values to retain and confirm that the records belong to the same person. The action and the chosen sources are recorded in `EmployeeHistory`. Other conflicting personal data may still require manual resolution before linking.

### Permissions

Manage groups and permissions in **Django Admin → Groups**. Authorization is based on assigned permissions, including those inherited from groups; group names are configurable. Navigation, action buttons, and direct requests use consistent permission checks.

- **Superusers** manage permission groups and review registration and employee requests.
- **Operators** can see all inspections and create, assign, start, interrupt, resume, complete or cancel them when granted the corresponding permissions. They can record progress for an assigned employee without a login.
- **Employees** can see assigned inspections when granted viewing access. Starting/resuming, interrupting and completing assigned work require the corresponding permissions.

To allow visibility across all inspections, grant `inspections.view_all_inspections` alongside `inspections.view_inspection`. Grant each action permission according to the user's responsibilities.

### Inspection validity and history

A successful periodic, extraordinary or repeat inspection after repair establishes a validity date using the equipment-specific interval and the local completion date. A failed inspection or repair alone does not renew validity. The activity details show recorded history, including changes to assigned employees, results and cancellation reasons. Earlier activities may have no recorded event history. Physical laboratory intake and handover are not yet tracked as a separate stay.

### REST API

The initial Django REST Framework implementation includes EquipmentType operations, JWT and session authentication, and Swagger/OpenAPI documentation (`/api/docs/`). The token endpoint is `/api/token/`. Further endpoints and permission coverage are under development.

## Local setup

Use Python 3.12 or newer and install the dependencies listed in [requirements.txt](requirements.txt). The current development workflow uses PostgreSQL; consult the Django settings and local environment configuration for the database connection details. Do not assume an SQLite default without checking the settings in the version you are running.

```bash
git clone https://github.com/SNikolov100/control-measurements.git
cd control-measurements
python -m venv .venv
```

Activate the environment with `./.venv/Scripts/Activate.ps1` in Windows PowerShell (or `.venv\Scripts\activate.bat` in Command Prompt), or `source .venv/bin/activate` on Linux/macOS.

```bash
python -m pip install -r requirements.txt
```

Copy `.env.example` to `.env` where the example file is available, generate a unique secret key, and configure the environment values required by the current settings (including database and email settings as applicable). Do not commit `.env` or secrets.

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

A typical local configuration includes:

```dotenv
DJANGO_SECRET_KEY=replace-with-your-generated-secret-key
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
```

**Migration baseline:** During development, the initial migration files were regenerated and the legacy development database was retired. Set up a **fresh database** for the current migration history; do not attempt to upgrade the old development database using these files. Ensure the database exists and is correctly configured before running migrations.

Apply migrations, create the initial superuser, and run the server:

```bash
python -m django migrate --settings=Control_measurements.settings
python -m django createsuperuser --settings=Control_measurements.settings
python -m django runserver --settings=Control_measurements.settings
```

Open the [application](http://127.0.0.1:8000/) or [Django Admin](http://127.0.0.1:8000/admin/). Use the superuser to configure groups and their permissions.

## Testing and verification

Run Django's system checks:

```bash
python manage.py check
```

Run the test suite when appropriate:

```bash
python -m django test --settings=Control_measurements.settings
```

Manual checks carried out during development include employee CREATE/EDIT/LINK, linking with name and phone conflicts, and the employee list's search, filtering, and pagination. `EmployeeHistory` was also inspected after linking to verify that the selected sources were logged. Manual checks also cover interruption/resumption, activity history, assignment changes, validity and direct URL access (403 without permission, 404 for inaccessible inspections). These manual checks do **not** replace a full automated regression run.

For a permission check, use a regular account with only equipment-type viewing access. The list should open with Add, Edit, and Delete hidden. Grant the equipment-type change permission and reload to verify that Edit appears. Remove it and verify that the direct edit URL returns HTTP 403.

## Documentation

- Workflow overview ([English](docs/WORKFLOW_EN.md) · [Български](docs/WORKFLOW_BG.md))
- Application guide ([English](docs/WORKFLOW_GUIDE_EN.md) · [Български](docs/WORKFLOW_GUIDE_BG.md))
- [Changelog](CHANGELOG.md)

## License

Copyright (c) 2026 slavi6. All rights reserved.

The source code is publicly available for evaluation and testing.

Commercial use, redistribution, sublicensing, sale, and incorporation
of this software into another product are not permitted without prior
written permission from the copyright holder.
