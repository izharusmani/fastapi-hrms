from fastapi import FastAPI, APIRouter, HTTPException
from configurations import db
from database.schemas import all_data, all_attendance
from database.models import Employee, Attendance
from bson.objectid import ObjectId
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
router = APIRouter()

# allow local frontend to communicate
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://rococo-dieffenbachia-4abdf2.netlify.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== EMPLOYEE ENDPOINTS ====================
@router.get("/")
async def get_all_employees():
    data = db["employees"].find( )
    return all_data(data)

@router.post("/")
async def create_employee(new_employee: Employee):
    """Create a new employee with duplicate check"""
    try:
        # Check for duplicate emp_id
        existing = db["employees"].find_one({"emp_id": new_employee.emp_id})
        if existing:
            raise HTTPException(
                status_code=409,
                detail=f"Employee with ID '{new_employee.emp_id}' already exists"
            )
        
        # Check for duplicate email
        existing_email = db["employees"].find_one({"email": new_employee.email})
        if existing_email:
            raise HTTPException(
                status_code=409,
                detail=f"Employee with email '{new_employee.email}' already exists"
            )
        
        resp = db["employees"].insert_one(dict(new_employee))
        return {"status_code": 201, "id": str(resp.inserted_id), "message": "Employee created successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating employee: {str(e)}")

@router.put("/{employee_id}")
async def update_employee(employee_id: str, updated_employee: Employee):
    """Update an existing employee"""
    try:
        # Validate ObjectId
        try:
            id = ObjectId(employee_id)
        except:
            raise HTTPException(status_code=400, detail="Invalid employee ID format")
        
        existing_employee = db["employees"].find_one({"_id": id})
        if not existing_employee:
            raise HTTPException(status_code=404, detail="Employee not found")
        
        # Check for duplicate emp_id (if changing it)
        if updated_employee.emp_id != existing_employee["emp_id"]:
            duplicate = db["employees"].find_one({"emp_id": updated_employee.emp_id})
            if duplicate:
                raise HTTPException(
                    status_code=409,
                    detail=f"Employee with ID '{updated_employee.emp_id}' already exists"
                )
        
        # Check for duplicate email (if changing it)
        if updated_employee.email != existing_employee["email"]:
            duplicate_email = db["employees"].find_one({"email": updated_employee.email})
            if duplicate_email:
                raise HTTPException(
                    status_code=409,
                    detail=f"Employee with email '{updated_employee.email}' already exists"
                )
        
        db["employees"].update_one({"_id": id}, {"$set": dict(updated_employee)})
        return {"status_code": 200, "message": "Employee updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating employee: {str(e)}")

@app.delete("/{employee_id}")
async def delete_employee(employee_id: str):
    """Delete an employee"""
    try:
        # Validate ObjectId
        try:
            id = ObjectId(employee_id)
        except:
            raise HTTPException(status_code=400, detail="Invalid employee ID format")
        
        existing_employee = db["employees"].find_one({"_id": id})
        if not existing_employee:
            raise HTTPException(status_code=404, detail="Employee not found")
        
        db["employees"].delete_one({"_id": id})
        return {"status_code": 200, "message": "Employee deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting employee: {str(e)}")

# ==================== ATTENDANCE ENDPOINTS ====================
@router.post("/attendance/mark")
async def mark_attendance(attendance: Attendance):
    """Mark or update attendance for an employee"""
    try:
        # Check if employee exists
        employee = db["employees"].find_one({"emp_id": attendance.emp_id})
        if not employee:
            raise HTTPException(status_code=404, detail=f"Employee with ID '{attendance.emp_id}' not found")
        
        # Check if attendance record already exists for the date
        existing_record = db["attendance"].find_one({
            "emp_id": attendance.emp_id,
            "date": attendance.date
        })
        
        if existing_record:
            # Update existing record
            db["attendance"].update_one(
                {"_id": existing_record["_id"]},
                {"$set": {"status": attendance.status}}
            )
            return {"status_code": 200, "message": "Attendance updated successfully"}
        
        # Insert new attendance record
        resp = db["attendance"].insert_one(dict(attendance))
        return {"status_code": 201, "id": str(resp.inserted_id), "message": "Attendance marked successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error marking attendance: {str(e)}")

@router.get("/attendance/{emp_id}")
async def get_employee_attendance(emp_id: str, start_date: str = None, end_date: str = None):
    """Get all attendance records for an employee, optionally filtered by date range"""
    try:
        # Check if employee exists
        employee = db["employees"].find_one({"emp_id": emp_id})
        if not employee:
            raise HTTPException(status_code=404, detail=f"Employee with ID '{emp_id}' not found")
        
        # Build query with optional date filters
        query = {"emp_id": emp_id}
        if start_date:
            query.setdefault("date", {}).update({"$gte": start_date})
        if end_date:
            query.setdefault("date", {}).update({"$lte": end_date})
        
        records = db["attendance"].find(query).sort("date", -1)
        return all_attendance(records)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching attendance: {str(e)}")


@router.get("/attendance")
async def get_attendance(emp_id: str = None, start_date: str = None, end_date: str = None):
    """Get attendance records across employees or filtered by emp_id and/or date range"""
    try:
        query = {}
        if emp_id:
            query["emp_id"] = emp_id
        # date range
        if start_date:
            query.setdefault("date", {}).update({"$gte": start_date})
        if end_date:
            query.setdefault("date", {}).update({"$lte": end_date})

        records = db["attendance"].find(query).sort("date", -1)
        return all_attendance(records)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching attendance: {str(e)}")

@router.get("/attendance/{emp_id}/summary")
async def attendance_summary(emp_id: str):
    """Return present/absent counts for an employee"""
    try:
        employee = db["employees"].find_one({"emp_id": emp_id})
        if not employee:
            raise HTTPException(status_code=404, detail=f"Employee with ID '{emp_id}' not found")
        
        pipeline = [
            {"$match": {"emp_id": emp_id}},
            {"$group": {"_id": "$status", "count": {"$sum": 1}}}
        ]
        results = list(db["attendance"].aggregate(pipeline))
        summary = {"Present": 0, "Absent": 0}
        for r in results:
            summary[r["_id"]] = r["count"]
        summary["total"] = summary["Present"] + summary["Absent"]
        return summary
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error computing summary: {str(e)}")

@router.get("/attendance/{emp_id}/{date}")
async def get_attendance_by_date(emp_id: str, date: str):
    """Get attendance record for a specific date"""
    try:
        # Check if employee exists
        employee = db["employees"].find_one({"emp_id": emp_id})
        if not employee:
            raise HTTPException(status_code=404, detail=f"Employee with ID '{emp_id}' not found")
        
        # Get attendance for specific date
        record = db["attendance"].find_one({"emp_id": emp_id, "date": date})
        if not record:
            raise HTTPException(status_code=404, detail=f"No attendance record found for {date}")
        
        return {
            "id": str(record["_id"]),
            "emp_id": record["emp_id"],
            "date": record["date"],
            "status": record["status"],
            "created_at": record["created_at"]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching attendance: {str(e)}")

app.include_router(router)



