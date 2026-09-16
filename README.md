# Student Management System - CRUD

## Technology
- HTML
- CSS
- JavaScript
- Python Flask
- SQLite
- REST API

## Run

1. Open the project folder in VS Code.
2. Open Terminal.
3. Create a virtual environment (optional):

   python -m venv venv

4. Activate it on Windows:

   venv\Scripts\activate

5. Install packages:

   pip install -r requirements.txt

6. Run:

   python app.py

7. Open the address shown in the terminal, normally:

   http://127.0.0.1:5000

The SQLite database `students.db` will be created automatically.

## API Endpoints

GET    /api/students/
GET    /api/students/{id}/
POST   /api/students/
PUT    /api/students/{id}/
PATCH  /api/students/{id}/
DELETE /api/students/{id}/

## CRUD
Create - Add a student
Read - View/search students
Update - Edit a student
Delete - Delete a student

## Validation
- All fields required
- Valid email format
- Age between 15 and 100
- Duplicate email is rejected
- Server-side validation included
