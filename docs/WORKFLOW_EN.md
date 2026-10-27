
---

# Typical Operational Workflow

This document describes the general operational logic of the  
**Control Measurements** application.

Its purpose is to help testers and future operators understand the
relationship between customers, customer sites, contact persons,
equipment, employees and activities.
---
## Important Equipment Status Rule

> Registering equipment does not mean that the equipment is physically
> present at our facility.

Equipment that exists in the register but remains physically located
at the customer site will normally have the **In Service**
(`in_service`) status.

The equipment should move to **Waiting for Inspection** only after:

1. the equipment has been physically delivered to our facility;
2. the operator has found or registered it in the system;
3. a new activity has been created for it.

Detailed instructions for preparing and verifying test data are
available in [WORKFLOW_GUIDE_EN.md](WORKFLOW_GUIDE_EN.md).

---
## 1. Employees and Specialties

The system contains the employees who may participate in inspection,
calibration and repair activities.

Each employee may be qualified in one or more specialties.

When employees are assigned to an activity, the application offers only
employees who have the specialty required for that particular activity.

A single employee or a team of several employees may be assigned to an
activity.

### Employees Without a Specialty

An employee may be registered without an acquired specialty.

Such an employee is considered a trainee or a person who is not yet
officially qualified to perform specialized work independently.

Until the required specialty has been acquired, the employee must not
be available for assignment to activities requiring that qualification.

---

## 2. Customer and Customer Site

Equipment belongs to a customer company and is used at a specific
customer site, such as:

- a department;
- a workshop;
- an organizational unit;
- a production site;
- another operational location.

A primary contact person may be selected for each customer site.

This is usually the person who delivers the equipment and serves as the
main point of contact between the customer and the service provider.

Multiple equipment records may belong to the same customer site.

---

## 3. Receiving Previously Registered Equipment

When equipment is delivered, the operator first checks whether it
already exists in the equipment register.

If the equipment was registered during a previous visit:

1. Find the customer.
2. Open the appropriate customer site.
3. Find the equipment by its registration, serial or other identification number.
4. Verify that the equipment information is still correct.
5. Create a new activity for the equipment.

Before being physically received, the equipment will normally have the
status **In Service** (`in_service`).

This status means that the equipment exists in the register but is
currently located at the customer site and has not been delivered for
the current inspection.

After a new activity is created, the equipment moves to a state
indicating that it has been physically received and is waiting for
inspection.

---

## 4. Receiving New Equipment

If the delivered equipment does not exist in the register, it must
first be registered.

### 4.1. Checking the Equipment Type

The operator checks whether the required equipment type already exists
in the equipment type register.

If the type does not exist:

1. Create a new equipment type.
2. Enter the required type information.
3. Return to the customer site.

### 4.2. Registering the Specific Equipment

After selecting the appropriate type, the operator:

1. Opens the customer and the appropriate customer site.
2. Selects the contact person or primary responsible person.
3. Creates a new equipment record.
4. Selects the equipment type.
5. Enters the serial, registration or other identification number.
6. Enters the remaining available information.
7. Saves the equipment.
8. Creates a new activity for it.

Creating the equipment only adds it to the register.

Creating the activity indicates that the equipment has physically
arrived and is waiting to be processed.

After the activity is created successfully, the operator returns to the
equipment list for the current customer site so that the next device
from the same delivery can be processed.

---

## 5. Preparing and Starting an Inspection

After the equipment has been received, an appropriate activity is
created, for example:

- calibration;
- periodic inspection;
- extraordinary inspection;
- repair;
- repeat inspection after repair.

The normal process is:

1. Create an activity for the specific equipment.
2. Determine the required specialty.
3. Assign one employee or a team.
4. The employee list is filtered according to the required specialty.
5. Start the activity.

Starting the activity means that work on the equipment has actually
begun.

After assigning, starting, completing or cancelling an activity, the
operator is returned to the common activities list.

---

## 6. Completing an Inspection

After the inspection is performed, the operator records its result.

### Successful Result

When the result is successful:

1. Complete the activity as successful.
2. Store the result in the activity history.
3. Move the equipment to the state determined by the workflow.
4. After it is returned to the customer, the equipment is considered to be in service again.

### Unsuccessful Result

When the result is unsuccessful:

1. Complete the activity as unsuccessful.
2. Store the result in the activity history.
3. Mark the equipment as requiring repair.
4. Find it through the **Under Repair** (`under_repair`) filter.
5. Create a repair activity for the equipment.

---

## 7. Repair

A repair is a separate activity with its own lifecycle.

1. Find the equipment in the equipment list or through the under-repair filter.
2. Create a repair activity.
3. Assign an employee or team with the required specialty.
4. Start the repair.
5. Record the repair result when the work is completed.

A repair may have no predefined completion deadline.

Successful completion of the repair means that the repair work has been
performed. It does not automatically prove that the equipment now meets
the inspection requirements.

For this reason, a **Repeat Inspection After Repair** activity must be
created after a successful repair.

If the repair is unsuccessful, the result remains in the history and
the equipment stays in a state corresponding to the unresolved problem.

---

## 8. Repeat Inspection After Repair

After a successful repair, the equipment must undergo another
inspection.

1. Create a “Repeat Inspection After Repair” activity.
2. Assign an employee or team with the required specialty.
3. Start the activity.
4. Perform the inspection.
5. Record a successful or unsuccessful result.

Only a successful repeat inspection confirms that the equipment may
return to normal service.

If the repeat inspection is unsuccessful, the equipment may be sent
for repair again.

---

## 9. Workflow Summary

The typical operational workflow is:

1. Register employees and their specialties.
2. Select or create a customer.
3. Select or create a customer site.
4. Select the primary contact person.
5. Search for the delivered equipment.
6. Register the equipment if it does not already exist.
7. Create a new activity.
8. Move the equipment to the “Waiting for Inspection” state.
9. Assign a qualified employee or team.
10. Start the activity.
11. Complete it with a successful or unsuccessful result.
12. Create a repair activity when necessary.
13. Perform a repeat inspection after a successful repair.
14. Preserve state changes and results in the history.
15. Return successfully inspected equipment to normal service.