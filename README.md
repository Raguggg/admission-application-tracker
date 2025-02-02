# University Admission Application System

## Project Overview

This project is a Flask-based web application designed to handle university admission applications. It offers two main interfaces:

- **User Interface:** Allows applicants to create and submit their admission application, upload required documents, and download an admission letter upon approval.
- **Admin Interface:** Enables administrators to manage courses, document types, and review or update the status of submitted applications. Administrators can also toggle the application acceptance period.

The application utilizes Flask for the backend, Flask-Login for authentication, Flask-Migrate for database migrations, and Flask-RESTx for API documentation and endpoint creation. SQLAlchemy is used as the ORM layer, with SQLite used by default (configurable to other databases like PostgreSQL or MySQL).

## Installation Instructions

Follow these steps to install and run the application locally:


Follow these steps to set up the project locally:

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Raguggg/admission-application-tracker.git
   ```
2. **Navigate to the project directory**:
   ```bash
   cd admission-application-tracker
   ```
3. **Sync dependencies**:
   - If you’re using `uv`, run (recommended):
     ```bash
     uv sync
     ```
   - Otherwise:
     1. Create a virtual environment:
        ```bash
        python -m venv venv
        ```
     2. Activate the virtual environment:
        - On macOS/Linux:
          ```bash
          source venv/bin/activate
          ```
        - On Windows:
          ```bash
          venv\Scripts\activate
          ```
    3. Install all packages
        ```bash
        pip install .
        ```

4. **Configure Environment Variables (Optional):**

   The default configuration is set in the `dev_config` object. For production, you may wish to set environment variables (e.g., `SECRET_KEY`, `SQLALCHEMY_DATABASE_URI`) and create a separate configuration module.

5. **Database Setup:**

   The application uses Flask-Migrate to handle database migrations. Run the following commands to set up the database:

   ```bash
   flask db init
   flask db migrate
   flask db upgrade
   ```

   Alternatively, the application factory calls `db.create_all()` to create tables if they do not exist when running in development mode.

6. **Run the Application:**

   Start the Flask development server:

   ```bash
   flask run
   ```

   Visit [http://127.0.0.1:5000/hello](http://127.0.0.1:5000/hello) to see a simple greeting page. API documentation is available at [http://127.0.0.1:5000/api/docs](http://127.0.0.1:5000/api/docs).

## Usage Instructions

### For Applicants (Users)

- **Register & Login:**
  - Use the `/register` endpoint to create a new account.
  - Log in using the `/login` endpoint.

- **Submit an Application:**
  - Once logged in, navigate to the `/user/applications` endpoint (POST) to create your application. Ensure all required fields are provided.
  - After creating the application, you can check its status by calling `/user/status` (GET).

- **Upload Documents:**
  - Upload required documents via `/user/documents/upload` (POST). Once all required documents are uploaded, the application status automatically updates to `PENDING`.

- **Download Admission Letter:**
  - If your application status is updated to `APPROVED` and an admission letter has been generated, download it from `/user/letter` (GET).

### For Administrators

- **Admin Login:**
  - Admin accounts (e.g., the default admin user with email `admin@gmail.com` and password `admin`) can log in using the same login endpoint.
  - Only logged-in administrators have access to admin-specific endpoints.

- **Manage Courses:**
  - List all courses using `/admin/courses` (GET).
  - Create a new course using `/admin/courses` (POST).

- **Manage Document Types:**
  - List document types using `/admin/documents` (GET).
  - Create new document types via `/admin/documents` (POST).

- **Review and Update Applications:**
  - Retrieve all submitted applications using `/admin/applications` (GET).
  - Change the status of a particular application (e.g., to approve or reject an application) using `/admin/applications/<application_id>/status` (PUT).
  - When an application is approved, an admission letter is generated automatically.

- **Toggle Application Acceptance:**
  - Enable or disable the overall application acceptance (with optional start and end dates) using `/admin/acceptance` (PUT).

## Testing

To run tests (if applicable), follow these steps:

1. **Install Test Dependencies:**

   If not already included, install testing libraries such as `pytest`:

   ```bash
   pip install pytest
   ```

2. **Run the Test Suite:**

   Execute all tests by running:

   ```bash
   pytest
   ```

   Ensure your test database is properly configured in your testing configuration. Tests should cover functionality such as user registration, application submission, document uploads, and admin operations.

## Technology Stack

- **Backend Framework:** Flask
- **API Documentation:** Flask-RESTx (Swagger UI)
- **Database ORM:** SQLAlchemy
- **Database Migration:** Flask-Migrate
- **Authentication:** Flask-Login
- **Data Validation:** Pydantic
- **PDF Generation:** reportlab
- **Testing:** Pytest

## Assumptions & Design Decisions

- **Single Application per User:** Each user is allowed only one active application. Attempts to create multiple applications are blocked.
- **Role-Based Access:** The application distinguishes between regular users and administrators. Admin users have exclusive access to certain endpoints (e.g., course management, document type management, application review).
- **Default Admin User:** The application automatically creates a default admin user (`admin@gmail.com`) with a preset password (`admin`) on the first run if no admin exists.
- **File Storage:** Uploaded documents and generated admission letters are stored in dedicated directories (`UPLOADS` and `ADMISSION_LETTER`). These directories are automatically created if they do not exist.
- **Data Validation:** User input is validated using Pydantic models to ensure data consistency (e.g., age verification, phone number format).
- **Application Status Workflow:** The application follows a status flow from `INCOMPLETE` → `PENDING` → `APPROVED`/`REJECTED`, with specific actions (such as document uploads and admission letter generation) triggering status changes.
- **Error Handling:** The application includes basic error handling, returning appropriate HTTP status codes and error messages for invalid operations (e.g., duplicate registrations, invalid document uploads).
