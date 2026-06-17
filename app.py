import os
import json
from datetime import datetime
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="Sri Gowthami admissions Portal API")

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = "database.json"

DEFAULT_ENQUIRIES = [
  {
    "id": "ENQ1091",
    "name": "Aravind Swamy",
    "parent": "A. Rama Swamy",
    "email": "aravind@gmail.com",
    "phone": "9876543210",
    "course": "B.Tech Computer Science & Engineering",
    "campus": "Main Campus",
    "marks": 88,
    "status": "Shortlisted",
    "staff": "Dr. K. Raghavan",
    "notes": "Excellent academic record. Sent initial acceptance schedule.",
    "history": [
      { "date": "2026-06-16 10:15", "action": "Submitted Admission Enquiry Form" },
      { "date": "2026-06-16 11:20", "action": "Assigned counselor Dr. K. Raghavan" },
      { "date": "2026-06-16 11:20", "action": "Status updated to Shortlisted by Dr. K. Raghavan" }
    ]
  },
  {
    "id": "ENQ1092",
    "name": "Divya Reddy",
    "parent": "D. Prabhakar Reddy",
    "email": "divya.reddy@yahoo.com",
    "phone": "9123456780",
    "course": "MBA Business Management",
    "campus": "City Campus",
    "marks": 76,
    "status": "Shortlisted",
    "staff": "Prof. S. Laxmi",
    "notes": "Undergraduate documents verified, waiting for fee confirmation.",
    "history": [
      { "date": "2026-06-15 14:02", "action": "Submitted Admission Enquiry Form" },
      { "date": "2026-06-15 15:30", "action": "Status updated to Shortlisted by Prof. S. Laxmi" }
    ]
  },
  {
    "id": "ENQ1093",
    "name": "Rahul Kumar",
    "parent": "Satish Kumar",
    "email": "rahulkumar@outlook.com",
    "phone": "9988776655",
    "course": "B.Tech Civil Engineering",
    "campus": "Engineering Block",
    "marks": 52,
    "status": "Pending",
    "staff": "Mr. B. Srinivas",
    "notes": "Enquired about campus hostel accommodation facilities.",
    "history": [
      { "date": "2026-06-16 09:45", "action": "Submitted Admission Enquiry Form" }
    ]
  },
  {
    "id": "ENQ1094",
    "name": "Sneha Rao",
    "parent": "P. Venkateswara Rao",
    "email": "sneha.rao@gmail.com",
    "phone": "9554321098",
    "course": "B.Tech Electronics & Comm. Eng.",
    "campus": "Main Campus",
    "marks": 45,
    "status": "Ineligible",
    "staff": "Mrs. P. Shanti",
    "notes": "Marks are below the minimum threshold required for ECE (55%).",
    "history": [
      { "date": "2026-06-16 08:30", "action": "Submitted Admission Enquiry Form" },
      { "date": "2026-06-16 08:31", "action": "System auto-marked Ineligible due to insufficient marks" }
    ]
  },
  {
    "id": "ENQ1095",
    "name": "Vineeth Naidu",
    "parent": "V. Krishna Naidu",
    "email": "vineeth.naidu@gmail.com",
    "phone": "9440123456",
    "course": "B.Tech Artificial Intelligence & ML",
    "campus": "Engineering Block",
    "marks": 92,
    "status": "Approved",
    "staff": "Dr. K. Raghavan",
    "notes": "Direct Admission approved under merit bracket. Seat reservation fee processed.",
    "history": [
      { "date": "2026-06-14 11:12", "action": "Submitted Admission Enquiry Form" },
      { "date": "2026-06-14 12:00", "action": "Assigned to counselor Dr. K. Raghavan" },
      { "date": "2026-06-14 16:30", "action": "Status updated to Approved by Dr. K. Raghavan" }
    ]
  }
]

# Models
class HistoryItem(BaseModel):
    date: str
    action: str

class EnquiryItem(BaseModel):
    id: Optional[str] = None
    name: str
    parent: str
    email: str
    phone: str
    course: str
    campus: str
    marks: int
    status: Optional[str] = "Pending"
    staff: Optional[str] = "Dr. K. Raghavan"
    notes: Optional[str] = ""
    leadScore: Optional[str] = None
    source: Optional[str] = "Website Portal"
    history: Optional[List[HistoryItem]] = None

class ModifyEnquiry(BaseModel):
    status: str
    staff: str
    notes: Optional[str] = ""

class LoginCredentials(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    status: str
    token: str
    username: str
    role: str
    name: str

class TokenVerifyRequest(BaseModel):
    token: str

def load_db() -> List[Dict[str, Any]]:
    if not os.path.exists(DB_PATH):
        save_db(DEFAULT_ENQUIRIES)
        return DEFAULT_ENQUIRIES
    try:
        with open(DB_PATH, "r") as f:
            return json.load(f)
    except Exception:
        return DEFAULT_ENQUIRIES

def save_db(data: List[Dict[str, Any]]):
    with open(DB_PATH, "w") as f:
        json.dump(data, f, indent=2)

@app.get("/api/enquiries", response_model=List[EnquiryItem])
def get_enquiries():
    return load_db()

@app.post("/api/enquiries", response_model=EnquiryItem)
def create_enquiry(item: EnquiryItem):
    db = load_db()
    
    # Generate unique ID
    num = 1000 + len(db) + 1
    generated_id = f"ENQ{num}"
    
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d %H:%M")
    
    history = item.history or []
    if not history:
        history.append(HistoryItem(date=date_str, action=f"Submitted Enquiry Form for {item.course}"))

    new_item = item.dict()
    new_item["id"] = generated_id
    new_item["history"] = [h.dict() for h in history]

    db.insert(0, new_item)
    save_db(db)
    return new_item

@app.put("/api/enquiries/{enquiry_id}", response_model=EnquiryItem)
def update_enquiry(enquiry_id: str, updates: ModifyEnquiry):
    db = load_db()
    for index, e in enumerate(db):
        if e["id"] == enquiry_id:
            now = datetime.now()
            date_str = now.strftime("%Y-%m-%d %H:%M")
            
            history = e.get("history", [])
            
            if e["status"] != updates.status:
                history.append({"date": date_str, "action": f"Status changed to {updates.status} by counselor"})
                e["status"] = updates.status
                
            if e.get("staff") != updates.staff:
                history.append({"date": date_str, "action": f"Assigned counselor updated to {updates.staff}"})
                e["staff"] = updates.staff
                
            if updates.notes and updates.notes.strip() != "":
                history.append({"date": date_str, "action": f"Note added: \"{updates.notes.strip()}\""})
                e["notes"] = updates.notes
                
            e["history"] = history
            db[index] = e
            save_db(db)
            return e
            
    raise HTTPException(status_code=404, detail="Enquiry not found")

@app.delete("/api/enquiries/{enquiry_id}")
def delete_enquiry(enquiry_id: str):
    db = load_db()
    for index, e in enumerate(db):
        if e["id"] == enquiry_id:
            deleted = db.pop(index)
            save_db(db)
            return {"status": "success", "message": f"Deleted enquiry {enquiry_id}", "deleted": deleted}
            
    raise HTTPException(status_code=404, detail="Enquiry not found")

@app.post("/api/enquiries/restore")
def restore_db():
    save_db(DEFAULT_ENQUIRIES)
    return {"status": "success", "message": "Database restored to default demo records", "data": DEFAULT_ENQUIRIES}

@app.post("/api/login", response_model=LoginResponse)
def login(credentials: LoginCredentials):
    users = {
        "admin": {"password": "password123", "role": "admin", "name": "System Admin", "token": "token-admin-123"},
        "counselor": {"password": "password123", "role": "counselor", "name": "Dr. K. Raghavan", "token": "token-counselor-raghavan"},
        "counselor1": {"password": "password123", "role": "counselor", "name": "Dr. K. Raghavan", "token": "token-counselor-raghavan"},
        "counselor2": {"password": "password123", "role": "counselor", "name": "Prof. S. Laxmi", "token": "token-counselor-laxmi"},
        "counselor3": {"password": "password123", "role": "counselor", "name": "Mr. B. Srinivas", "token": "token-counselor-srinivas"},
        "counselor4": {"password": "password123", "role": "counselor", "name": "Mrs. P. Shanti", "token": "token-counselor-shanti"}
    }
    
    username = credentials.username.lower().strip()
    if username in users and users[username]["password"] == credentials.password:
        user_info = users[username]
        return LoginResponse(
            status="success",
            token=user_info["token"],
            username=username,
            role=user_info["role"],
            name=user_info["name"]
        )
        
    raise HTTPException(status_code=401, detail="Invalid username or password")

@app.post("/api/verify_token")
def verify_token(payload: TokenVerifyRequest):
    valid_tokens = {
        "token-admin-123",
        "token-counselor-raghavan",
        "token-counselor-laxmi",
        "token-counselor-srinivas",
        "token-counselor-shanti"
    }
    if payload.token in valid_tokens:
        return {"status": "valid"}
    raise HTTPException(status_code=401, detail="Invalid session token")
