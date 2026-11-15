# Control Measurements

Control Measurements is a Django application for managing customers, equipment, employees, and scheduled control measurements. It is under active development.

## What the application does

| Area | Features |
| --- | --- |
| Customers | Manage customer records, sites, and site contacts. |
| Equipment | Register equipment by customer site, manage equipment types, and track equipment status. Inspection intervals and expected durations can use defaults from the equipment type. |
| Employees | Manage employee records, specialties, active status, and links to user accounts. An employee record can exist without a login. |
| Activities | Create and assign inspections, calibrations, repairs, and reinspections. Track activities through start, completion, or cancellation. Starting an activity requires active, qualified assignees. |
| Settings | Manage company details, system settings, and specialties. System and company settings can be granted as read-only access. |

## Accounts and access

Visitors can open About and Contacts, register, or sign in. Users sign in with an email address or username. A new account awaits approval. Once approved, the user completes their profile, and a superuser links the account to an existing employee record or creates one.

Manage groups and permissions in **Django Admin → Groups**. The application uses the permissions assigned to each user, including permissions inherited from groups. Group names are configurable. The same access rules control navigation, action buttons, and requests sent directly to the server.

- **Superusers** manage groups and approve registrations and employee link requests.
- **Operators** can see all inspections and create, assign, start, and complete them when granted the corresponding permissions. They can record progress for an assigned employee without a login.
- **Employees** can see their assigned inspections when granted inspection viewing access. Starting and completing work require separate permissions.

To grant visibility across all inspections, add `inspections.view_all_inspections` alongside `inspections.view_inspection`. Grant individual action permissions according to the user's responsibilities.

## Local setup

The application uses SQLite by default. Use Python 3.12 or newer and install the dependencies pinned in [requirements.txt](requirements.txt).

```bash
git clone https://github.com/SNikolov100/control-measurements.git
cd control-measurements
python -m venv .venv
```

Activate the environment with `.venv\Scripts\activate.bat` in Windows Command Prompt or `source .venv/bin/activate` on Linux and macOS.

```bash
python -m pip install -r requirements.txt
```

Copy `.env.example` to `.env` and replace the example secret key with a generated value. Keep `.env` outside version control.

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

A local configuration uses these settings:

```dotenv
DJANGO_SECRET_KEY=replace-with-your-generated-secret-key
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
```

Apply migrations, create the initial superuser, and run the server:

```bash
python -m django migrate --settings=Control_measurements.settings
python -m django createsuperuser --settings=Control_measurements.settings
python -m django runserver --settings=Control_measurements.settings
```

Open the [application](http://127.0.0.1:8000/) or [Django Admin](http://127.0.0.1:8000/admin/). Use the superuser to set up groups and their permissions.

## Testing

Run the Django test suite:

```bash
python -m django test --settings=Control_measurements.settings
```

For a browser check, use a regular account with only equipment-type viewing access. The list should open with Add, Edit, and Delete hidden. Grant the group the equipment-type change permission and reload to verify that Edit appears. Remove the permission and verify that the direct edit URL returns HTTP 403.

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
