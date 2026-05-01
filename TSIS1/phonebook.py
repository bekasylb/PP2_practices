import csv
import json
from datetime import datetime
from connect import connect_db


def execute_sql_file(filename):
    conn = connect_db()
    cur = conn.cursor()

    with open(filename, "r", encoding="utf-8") as f:
        cur.execute(f.read())

    conn.commit()
    cur.close()
    conn.close()
    print(f"{filename} executed successfully.")


def get_group_id(cur, group_name):
    cur.execute(
        "INSERT INTO groups(name) VALUES (%s) ON CONFLICT (name) DO NOTHING",
        (group_name,)
    )
    cur.execute("SELECT id FROM groups WHERE name = %s", (group_name,))
    row = cur.fetchone()
    return row[0] if row else None


def add_contact():
    conn = connect_db()
    cur = conn.cursor()

    name = input("Name: ").strip()
    email = input("Email: ").strip()
    birthday = input("Birthday (YYYY-MM-DD): ").strip()
    group_name = input("Group: ").strip()

    group_id = get_group_id(cur, group_name)

    cur.execute("SELECT id FROM contacts WHERE name = %s", (name,))
    existing = cur.fetchone()

    if existing:
        print("Contact with this name already exists.")
        conn.rollback()
        cur.close()
        conn.close()
        return

    cur.execute(
        """
        INSERT INTO contacts(name, email, birthday, group_id)
        VALUES (%s, %s, %s, %s)
        RETURNING id
        """,
        (name, email or None, birthday or None, group_id)
    )
    contact_id = cur.fetchone()[0]

    while True:
        phone = input("Phone (leave empty to stop): ").strip()
        if not phone:
            break
        phone_type = input("Phone type (home/work/mobile): ").strip().lower()
        cur.execute(
            "INSERT INTO phones(contact_id, phone, type) VALUES (%s, %s, %s)",
            (contact_id, phone, phone_type)
        )

    conn.commit()
    cur.close()
    conn.close()
    print("Contact added.")


def show_contacts(rows):
    if not rows:
        print("No contacts found.")
        return

    for row in rows:
        print(row)


def filter_by_group():
    conn = connect_db()
    cur = conn.cursor()

    group_name = input("Enter group name: ").strip()

    cur.execute(
        """
        SELECT c.id, c.name, c.email, c.birthday, g.name
        FROM contacts c
        LEFT JOIN groups g ON c.group_id = g.id
        WHERE g.name = %s
        ORDER BY c.name
        """,
        (group_name,)
    )
    show_contacts(cur.fetchall())

    cur.close()
    conn.close()


def search_by_email():
    conn = connect_db()
    cur = conn.cursor()

    query = input("Enter part of email: ").strip()

    cur.execute(
        """
        SELECT id, name, email, birthday
        FROM contacts
        WHERE email ILIKE %s
        ORDER BY name
        """,
        (f"%{query}%",)
    )
    show_contacts(cur.fetchall())

    cur.close()
    conn.close()


def sort_contacts():
    conn = connect_db()
    cur = conn.cursor()

    print("Sort by: 1-name 2-birthday 3-date added")
    choice = input("Choose: ").strip()

    if choice == "1":
        order_by = "c.name"
    elif choice == "2":
        order_by = "c.birthday"
    elif choice == "3":
        order_by = "c.created_at"
    else:
        print("Invalid choice.")
        cur.close()
        conn.close()
        return

    cur.execute(
        f"""
        SELECT c.id, c.name, c.email, c.birthday, g.name, c.created_at
        FROM contacts c
        LEFT JOIN groups g ON c.group_id = g.id
        ORDER BY {order_by}
        """
    )
    show_contacts(cur.fetchall())

    cur.close()
    conn.close()


def paginated_navigation():
    conn = connect_db()
    cur = conn.cursor()

    limit_count = 3
    offset_count = 0

    while True:
        cur.execute("SELECT * FROM get_contacts_page(%s, %s)", (limit_count, offset_count))
        rows = cur.fetchall()

        print(f"\nPage offset={offset_count}")
        show_contacts(rows)

        cmd = input("next / prev / quit: ").strip().lower()
        if cmd == "next":
            offset_count += limit_count
        elif cmd == "prev":
            offset_count = max(0, offset_count - limit_count)
        elif cmd == "quit":
            break
        else:
            print("Unknown command.")

    cur.close()
    conn.close()


def export_to_json():
    conn = connect_db()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT
            c.id,
            c.name,
            c.email,
            c.birthday,
            g.name AS group_name
        FROM contacts c
        LEFT JOIN groups g ON c.group_id = g.id
        ORDER BY c.id
        """
    )
    contacts = cur.fetchall()

    result = []
    for contact in contacts:
        contact_id, name, email, birthday, group_name = contact

        cur.execute(
            "SELECT phone, type FROM phones WHERE contact_id = %s ORDER BY id",
            (contact_id,)
        )
        phones = [{"phone": p[0], "type": p[1]} for p in cur.fetchall()]

        result.append({
            "name": name,
            "email": email,
            "birthday": str(birthday) if birthday else None,
            "group": group_name,
            "phones": phones
        })

    with open("contacts_export.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    cur.close()
    conn.close()
    print("Exported to contacts_export.json")


def import_from_json():
    conn = connect_db()
    cur = conn.cursor()

    filename = input("JSON filename: ").strip()

    with open(filename, "r", encoding="utf-8") as f:
        data = json.load(f)

    for item in data:
        name = item.get("name")
        email = item.get("email")
        birthday = item.get("birthday")
        group_name = item.get("group", "Other")
        phones = item.get("phones", [])

        cur.execute("SELECT id FROM contacts WHERE name = %s", (name,))
        existing = cur.fetchone()

        if existing:
            decision = input(f"{name} already exists. skip / overwrite: ").strip().lower()
            if decision == "skip":
                continue
            elif decision == "overwrite":
                group_id = get_group_id(cur, group_name)
                cur.execute(
                    """
                    UPDATE contacts
                    SET email = %s, birthday = %s, group_id = %s
                    WHERE name = %s
                    RETURNING id
                    """,
                    (email, birthday, group_id, name)
                )
                contact_id = cur.fetchone()[0]
                cur.execute("DELETE FROM phones WHERE contact_id = %s", (contact_id,))
            else:
                continue
        else:
            group_id = get_group_id(cur, group_name)
            cur.execute(
                """
                INSERT INTO contacts(name, email, birthday, group_id)
                VALUES (%s, %s, %s, %s)
                RETURNING id
                """,
                (name, email, birthday, group_id)
            )
            contact_id = cur.fetchone()[0]

        for phone_data in phones:
            cur.execute(
                "INSERT INTO phones(contact_id, phone, type) VALUES (%s, %s, %s)",
                (contact_id, phone_data["phone"], phone_data["type"])
            )

    conn.commit()
    cur.close()
    conn.close()
    print("JSON import completed.")


def import_from_csv():
    conn = connect_db()
    cur = conn.cursor()

    filename = input("CSV filename: ").strip()

    with open(filename, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            name = row["name"].strip()
            email = row.get("email", "").strip() or None
            birthday = row.get("birthday", "").strip() or None
            group_name = row.get("group", "Other").strip() or "Other"
            phone = row.get("phone", "").strip()
            phone_type = row.get("phone_type", "mobile").strip().lower()

            group_id = get_group_id(cur, group_name)

            cur.execute("SELECT id FROM contacts WHERE name = %s", (name,))
            existing = cur.fetchone()

            if existing:
                contact_id = existing[0]
                cur.execute(
                    """
                    UPDATE contacts
                    SET email = %s, birthday = %s, group_id = %s
                    WHERE id = %s
                    """,
                    (email, birthday, group_id, contact_id)
                )
            else:
                cur.execute(
                    """
                    INSERT INTO contacts(name, email, birthday, group_id)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id
                    """,
                    (name, email, birthday, group_id)
                )
                contact_id = cur.fetchone()[0]

            if phone:
                cur.execute(
                    "INSERT INTO phones(contact_id, phone, type) VALUES (%s, %s, %s)",
                    (contact_id, phone, phone_type)
                )

    conn.commit()
    cur.close()
    conn.close()
    print("CSV import completed.")


def add_phone_procedure():
    conn = connect_db()
    cur = conn.cursor()

    name = input("Contact name: ").strip()
    phone = input("Phone: ").strip()
    phone_type = input("Type (home/work/mobile): ").strip().lower()

    cur.execute("CALL add_phone(%s, %s, %s)", (name, phone, phone_type))
    conn.commit()

    cur.close()
    conn.close()
    print("Phone added.")


def move_to_group_procedure():
    conn = connect_db()
    cur = conn.cursor()

    name = input("Contact name: ").strip()
    group_name = input("New group: ").strip()

    cur.execute("CALL move_to_group(%s, %s)", (name, group_name))
    conn.commit()

    cur.close()
    conn.close()
    print("Group updated.")


def search_contacts_function():
    conn = connect_db()
    cur = conn.cursor()

    query = input("Search query: ").strip()
    cur.execute("SELECT * FROM search_contacts(%s)", (query,))
    show_contacts(cur.fetchall())

    cur.close()
    conn.close()


def main():
    while True:
        print("\n--- TSIS1 PHONEBOOK ---")
        print("1. Execute schema.sql")
        print("2. Execute procedures.sql")
        print("3. Add contact")
        print("4. Filter by group")
        print("5. Search by email")
        print("6. Sort contacts")
        print("7. Paginated navigation")
        print("8. Export to JSON")
        print("9. Import from JSON")
        print("10. Import from CSV")
        print("11. Add phone (procedure)")
        print("12. Move to group (procedure)")
        print("13. Search contacts (function)")
        print("0. Exit")

        choice = input("Choose: ").strip()

        if choice == "1":
            execute_sql_file("schema.sql")
        elif choice == "2":
            execute_sql_file("procedures.sql")
        elif choice == "3":
            add_contact()
        elif choice == "4":
            filter_by_group()
        elif choice == "5":
            search_by_email()
        elif choice == "6":
            sort_contacts()
        elif choice == "7":
            paginated_navigation()
        elif choice == "8":
            export_to_json()
        elif choice == "9":
            import_from_json()
        elif choice == "10":
            import_from_csv()
        elif choice == "11":
            add_phone_procedure()
        elif choice == "12":
            move_to_group_procedure()
        elif choice == "13":
            search_contacts_function()
        elif choice == "0":
            print("Goodbye!")
            break
        else:
            print("Invalid choice.")


if __name__ == "__main__":
    main()
