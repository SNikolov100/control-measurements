# Application Workflow Guide

> Българска версия: [WORKFLOW_GUIDE_BG.md](WORKFLOW_GUIDE_BG.md)

This document describes the standard operational workflow in the
Control Measurements application.

> General operational logic: [WORKFLOW_EN.md](WORKFLOW_EN.md)



## Main Workflow

Initial Setup → Customer → Customer Site → Equipment → Activity → Employee → Result → History

<details>
<summary><strong>1. Initial System Setup</strong></summary>

Before starting regular work, open the **Settings** menu and complete the initial system configuration.

### Our Company Details

Enter and verify the information about the company operating the system.

This information may be used throughout the application and in future generated documents.

### System Settings

Review and configure the available system settings.

Make sure that the selected values match the organization’s working process before registering customers, equipment, and activities.

### Specialties

Create the specialties used when registering employees and assigning work.

For each specialty:

1. Enter a clear name and short name.
2. Assign a unique code.
3. Add a description when clarification is needed.
4. Select a recognizable color.
5. Set the display order.
6. Confirm that the specialty is active.

Only create specialties that are actually used by the organization.

### Setup Checklist

Before continuing, verify that:

- [ ] Our company details are entered.
- [ ] System settings are reviewed.
- [ ] Required specialties are created.
- [ ] Specialty codes are unique.
- [ ] Active specialties are correctly marked.

The initial setup should be completed before employees, equipment, and activities are entered into the system.

</details>

<details>
<summary><strong>2. Preparing Test Data</strong></summary>

## ⚠️ Important Test Data Rule

> **All preloaded equipment records must initially have the
> “In Service” (`in_service`) status.**

The **In Service** status means that:

- the equipment exists in the database;
- the equipment belongs to a specific customer site;
- the equipment is physically located at the customer site;
- the equipment has not yet arrived for the current inspection;
- there is no active inspection or repair activity for the equipment.

### Do Not Preload Equipment as “Waiting for Inspection”

The **Waiting for Inspection** status should be assigned only after:

1. the equipment has been physically delivered to our facility;
2. the operator has found or registered it in the system;
3. a new activity has been created for it.

> **Registering equipment does not mean that the equipment is
> physically present at our facility.**
>
> **Creating a new activity indicates that the equipment has arrived
> and has entered the current operational workflow.**

### Correct Test Transition

```text
In Service
→ Physical receipt of the equipment
→ Creation of a new activity
→ Waiting for Inspection
→ Assignment of a qualified employee
→ Start of the activity
```

### Test Data Checklist

Verify the following when preparing and testing the initial data:

- [ ] All preloaded equipment records start with the `in_service` status.
- [ ] Equipment moves to “Waiting for Inspection” after a new activity is created.
- [ ] Equipment without an active activity is not shown as waiting for inspection.
- [ ] A trainee without a specialty cannot be assigned independently.
- [ ] Available employees are filtered by the required specialty.
- [ ] An unsuccessful inspection sends the equipment into the repair workflow.
- [ ] A repeat inspection is created after a successful repair.
- [ ] Equipment returns to normal service only after a successful final result.

</details>

<details>
<summary><strong>3. Customer and Customer Site</strong></summary>

1. Search for an existing customer.
2. Create the customer if no matching record exists.
3. Select or create the customer site.
4. Add the responsible contact person when needed.

</details>

<details>
<summary><strong>4. Equipment Registration</strong></summary>

1. Open the equipment list for the selected customer site.
2. Search for the equipment before creating a new record.
3. Register the equipment if it does not already exist.
4. Confirm the identification and technical information.
5. Add an equipment image when available.

</details>

<details>
<summary><strong>5. Activity Creation</strong></summary>

1. Select the equipment.
2. Create the required activity.
3. Select the appropriate activity type.
4. Save the activity.
5. Return to the equipment list for the current customer site and
   continue with the next item.

</details>

<details>
<summary><strong>6. Activity Processing</strong></summary>

The standard activity lifecycle is:

1. Activity created.
2. Employee assigned.
3. Activity started.
4. Result entered.
5. Activity completed or cancelled.
6. Changes recorded in the activity history.

After Assign, Start, Complete, or Cancel, the operator returns to the
main Activities list.

</details>

<details>
<summary><strong>7. Repair Workflow</strong></summary>

1. Create a repair activity.
2. Assign an employee.
3. Start the repair.
4. Complete the repair when the work is finished.
5. Create a follow-up inspection when required.
6. Record the final inspection result.

Repair activities may initially have no fixed completion date.

</details>


<details>
<summary><strong>8. Important Operator Rules</strong></summary>

- Search before creating a new record.
- Verify that the correct customer site is selected.
- Do not create duplicate equipment records.
- Use the available workflow actions instead of manually changing statuses.
- Confirm all delete operations carefully.
- Review the activity history when checking previous actions.
- Use the main lists to continue work after completing an operation.

</details>


