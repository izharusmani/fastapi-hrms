def individual_data(employee):
    return {
        "id": str(employee["_id"]),
        "emp_id": employee["emp_id"],
        "name": employee["name"],
        "age": employee["age"],
        "email": employee["email"],
        "department": employee["department"],
        "created_at": employee["created_at"],
        "updated_at": employee["updated_at"]
    }

def all_data(employees):
    return [individual_data(employee) for employee in employees]

def individual_attendance(record):
    return {
        "id": str(record["_id"]),
        "emp_id": record["emp_id"],
        "date": record["date"],
        "status": record["status"],
        "created_at": record["created_at"]
    }

def all_attendance(records):
    return [individual_attendance(record) for record in records]
    