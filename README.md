# Control Measurements

Control Measurements is a Django application for managing customers,
equipment, employees, inspections, calibrations, repairs,
and control measurement schedules.


---

# Development Status

<details>
<summary><strong>Core Structure</strong></summary>

- [x] Project structure established
- [x] Reusable base models implemented
- [x] Company settings implemented
- [x] System settings implemented
- [x] Internationalization (BG/EN) enabled

</details>

<details>
<summary><strong>Customers</strong></summary>

- [x] Customers CRUD
- [x] Customer sites CRUD
- [x] Customer contacts CRUD
- [x] Slug-based URLs

</details>

<details>
<summary><strong>Equipment</strong></summary>

- [x] Equipment register
- [x] Equipment types management
- [x] Equipment image support
- [x] Slug-based URLs

</details>

<details>
<summary><strong>Employees</strong></summary>

- [x] Employee management
- [x] Employee image support
- [x] Specialty assignment

</details>

<details>
<summary><strong>Activities (Inspections)</strong></summary>

- [x] Activity creation
- [x] Assignment workflow
- [x] Start workflow
- [x] Completion workflow
- [x] Cancellation workflow
- [x] Status history

</details>

<details>
<summary><strong>User Interface</strong></summary>

- [x] Navigation menu
- [x] Confirmation pages
- [x] Custom 404 page
- [ ] Advanced filtering
- [ ] Final UI styling
- [ ] Responsive review

</details>

<details>
<summary><strong>Future Enhancements</strong></summary>

- [ ] User accounts
- [ ] Roles and permissions
- [ ] Backup and restore
- [ ] Audit improvements

</details>

---

# Testing Checklist

<details>
<summary><strong>Customers</strong></summary>

- [ ] Create customer
- [ ] Edit customer
- [ ] Delete customer
- [ ] Open details page
- [ ] Verify invalid slug returns 404

</details>

<details>
<summary><strong>Customer Sites</strong></summary>

- [ ] Create customer site
- [ ] Edit customer site
- [ ] Delete customer site

</details>

<details>
<summary><strong>Equipment</strong></summary>

- [ ] Create equipment
- [ ] Upload equipment image
- [ ] Edit equipment
- [ ] Delete equipment
- [ ] Verify invalid slug returns 404

</details>

<details>
<summary><strong>Employees</strong></summary>

- [ ] Create employee
- [ ] Upload employee image
- [ ] Edit employee
- [ ] Delete employee

</details>

<details>
<summary><strong>Activities</strong></summary>

- [ ] Create activity
- [ ] Assign employee
- [ ] Start activity
- [ ] Complete activity
- [ ] Cancel activity
- [ ] Verify activity history
- [ ] Verify redirects

</details>

---

# Development Principles

<details>
<summary><strong>Architecture Guidelines</strong></summary>

- Service layer handles business rules.
- Models own state transitions.
- Related operations use transactions when needed.
- URL parameters use TextChoices `.value`.
- UI choices may be restricted by forms, but validation is performed in business logic.
- Delete operations always require confirmation.
- Operator workflow and usability have priority over technical implementation details.
- Django Admin is not used.
- Single-user operation is the current target.
- Multi-user support may be added later.

</details>

## Documentation

The project currently uses:

- `README.md` for the project overview and installation instructions
- `CHANGELOG.md` for notable development changes
- Git commits for the detailed development history

### General Operational Workflow

The following documents explain the business logic, participants,
equipment lifecycle and activity status transitions:

- [Typical Operational Workflow – English](docs/WORKFLOW_EN.md)
- [Обичаен работен процес – Български](docs/WORKFLOW_BG.md)

### Application Workflow Guides

The following guides describe the practical actions performed by
operators and testers:

- [Application Workflow Guide – English](docs/WORKFLOW_GUIDE_EN.md)
- [Ръководство за работа с приложението – Български](docs/WORKFLOW_GUIDE_BG.md)

## Repository

[Control Measurements on GitHub](https://github.com/SNikolov100/control-measurements)

## Requirements

- Python 3.12+
- pip
- Git
- SQLite (included with Python)

<details>
<summary><strong>Quick Start</strong></summary>

### 1. Clone the repository

```bash
git clone https://github.com/SNikolov100/control-measurements.git
cd control-measurements
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

### 3. Activate the virtual environment

On Windows:

```bash
venv\Scripts\activate
```

On Linux or macOS:

```bash
source venv/bin/activate
```

### 4. Install the dependencies

```bash
pip install -r requirements.txt
```

### 5. Create the environment file

Copy `.env.example` to a new file named `.env`.

On Windows Command Prompt:

```bash
copy .env.example .env
```

On Linux or macOS:

```bash
cp .env.example .env
```

Open the newly created `.env` file and replace the example secret key with your own Django secret key.

A new key can be generated with:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Your `.env` file should follow this structure:

```env
DJANGO_SECRET_KEY=replace-with-your-generated-secret-key
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
```

> Do not commit the `.env` file. It is intentionally excluded through `.gitignore`.

### 6. Apply the database migrations

```bash
python manage.py migrate
```

### 7. Start the development server

```bash
python manage.py runserver
```

Open the application at:

[http://127.0.0.1:8000/](http://127.0.0.1:8000/)
</details>

## License

Copyright (c) 2026 slavi6. All rights reserved.

The source code is publicly available for evaluation and testing.

Commercial use, redistribution, sublicensing, sale, and incorporation
of this software into another product are not permitted without prior
written permission from the copyright holder.