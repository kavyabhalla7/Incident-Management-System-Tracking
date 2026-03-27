import json
from datetime import datetime

FILE = "incidents.json"


def load_data():
    try:
        with open(FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def save_data(data):
    with open(FILE, "w") as f:
        json.dump(data, f, indent=4)


def create_incident():
    data = load_data()

    print("\n--- Create New Incident ---")

    service = input("Enter Service Name: ").strip()

    severity = ""
    while severity not in ["SEV1", "SEV2", "SEV3"]:
        severity = input("Enter Severity (SEV1/SEV2/SEV3): ").strip().upper()
        if severity not in ["SEV1", "SEV2", "SEV3"]:
            print("❌ Invalid! Please enter SEV1, SEV2 or SEV3 only.")

    description = input("Enter Description: ").strip()

    if data:
        last_id = max(int(inc["id"].split("-")[1]) for inc in data)
        incident_id = f"INC-{last_id + 1:03}"
    else:
        incident_id = "INC-001"

    incident = {
        "id": incident_id,
        "service": service,
        "severity": severity,
        "description": description,
        "status": "Open",
        "created_at": str(datetime.now())
    }

    data.append(incident)
    save_data(data)

    print(f"\n✅ Incident {incident_id} Created Successfully!")


def view_incidents():
    data = load_data()

    if not data:
        print("\n⚠️  No incidents found. Create one first!")
        return

    print("\nFilter options:")
    print("1. View All")
    print("2. Filter by Status")
    print("3. Filter by Severity")

    choice = input("Enter choice: ").strip()

    if choice == "2":
        print("Statuses: Open / Investigating / Mitigated / Resolved")
        status_filter = input("Enter status to filter by: ").strip().capitalize()
        filtered = [inc for inc in data if inc["status"] == status_filter]

    elif choice == "3":
        sev_filter = input("Enter severity to filter by (SEV1/SEV2/SEV3): ").strip().upper()
        filtered = [inc for inc in data if inc["severity"] == sev_filter]

    else:
        filtered = data

    if not filtered:
        print("⚠️  No incidents match that filter.")
        return

    print(f"\n📋 Showing {len(filtered)} incident(s):\n")

    for inc in filtered:
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"  🆔  ID          : {inc['id']}")
        print(f"  🔧  Service     : {inc['service']}")
        print(f"  🚨  Severity    : {inc['severity']}")
        print(f"  📝  Description : {inc['description']}")
        print(f"  📌  Status      : {inc['status']}")
        print(f"  🕐  Created At  : {inc['created_at']}")
        if "updated_at" in inc:
            print(f"  ✏️   Updated At  : {inc['updated_at']}")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")


def update_incident():
    data = load_data()

    if not data:
        print("\n⚠️  No incidents found. Create one first!")
        return

    incident_id = input("\nEnter Incident ID to update (e.g. INC-001): ").strip().upper()

    found = None
    for inc in data:
        if inc["id"] == incident_id:
            found = inc
            break

    if not found:
        print("❌ Incident not found. Check the ID and try again.")
        return

    print(f"\n--- Current Details for {incident_id} ---")
    print(f"  Status      : {found['status']}")
    print(f"  Severity    : {found['severity']}")
    print(f"  Description : {found['description']}")

    print("\nWhat do you want to update?")
    print("1. Status")
    print("2. Severity")
    print("3. Description")

    choice = input("Enter choice: ").strip()

    if choice == "1":
        valid_statuses = ["Open", "Investigating", "Mitigated", "Resolved"]
        print("Valid statuses: Open / Investigating / Mitigated / Resolved")
        new_value = input("Enter new status: ").strip().capitalize()
        if new_value not in valid_statuses:
            print("❌ Invalid status entered.")
            return
        found["status"] = new_value

    elif choice == "2":
        valid_severities = ["SEV1", "SEV2", "SEV3"]
        new_value = input("Enter new severity (SEV1/SEV2/SEV3): ").strip().upper()
        if new_value not in valid_severities:
            print("❌ Invalid severity entered.")
            return
        found["severity"] = new_value

    elif choice == "3":
        new_value = input("Enter new description: ").strip()
        if not new_value:
            print("❌ Description cannot be empty.")
            return
        found["description"] = new_value

    else:
        print("❌ Invalid choice.")
        return

    found["updated_at"] = str(datetime.now())

    save_data(data)
    print(f"\n✅ Incident {incident_id} Updated Successfully!")


def delete_incident():
    data = load_data()

    if not data:
        print("\n⚠️  No incidents found. Create one first!")
        return

    incident_id = input("\nEnter Incident ID to delete (e.g. INC-001): ").strip().upper()

    found = None
    for inc in data:
        if inc["id"] == incident_id:
            found = inc
            break

    if not found:
        print("❌ Incident not found. Check the ID and try again.")
        return

    print(f"\n--- Incident to Delete ---")
    print(f"  ID          : {found['id']}")
    print(f"  Service     : {found['service']}")
    print(f"  Severity    : {found['severity']}")
    print(f"  Description : {found['description']}")
    print(f"  Status      : {found['status']}")

    confirm = input("\n⚠️  Are you sure you want to delete this? (yes/no): ").strip().lower()

    if confirm != "yes":
        print("❌ Deletion cancelled.")
        return

    data.remove(found)
    save_data(data)

    print(f"\n✅ Incident {incident_id} Deleted Successfully!")


def menu():
    while True:
        print("\n╔══════════════════════════════╗")
        print("║   🚨 Incident Tracker 🚨      ║")
        print("╠══════════════════════════════╣")
        print("║  1. Create Incident           ║")
        print("║  2. View Incidents            ║")
        print("║  3. Update Incident           ║")
        print("║  4. Delete Incident           ║")
        print("║  5. Exit                      ║")
        print("╚══════════════════════════════╝")

        choice = input("Enter choice: ").strip()

        if choice == "1":
            create_incident()
        elif choice == "2":
            view_incidents()
        elif choice == "3":
            update_incident()
        elif choice == "4":
            delete_incident()
        elif choice == "5":
            print("\n👋 Goodbye! Stay on-call! 🚀")
            break
        else:
            print("❌ Invalid choice. Enter 1-5.")


if __name__ == "__main__":
    menu()