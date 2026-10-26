# Control Measurements

Control Measurements is a Django application for managing customers,
equipment, employees, inspections, calibration schedules, repairs,
and upcoming control measurements.


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