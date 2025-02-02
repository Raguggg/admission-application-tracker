import json
from datetime import date, datetime
from functools import wraps
from io import BytesIO
from pathlib import Path
from typing import Optional

from flask import request, send_file
from flask_login import current_user, login_required
from flask_restx import Namespace, Resource, abort, fields, reqparse
from pydantic import (BaseModel, EmailStr, Field, ValidationError,
                      field_validator)
from sqlalchemy.exc import IntegrityError
from werkzeug.datastructures import FileStorage

from app.application.admission_letter import generate_letter
from app.application.models import (Application, ApplicationAcceptanceSettings,
                                    ApplicationStatus, Document, DocumentType,
                                    PreferredCourse)
from app.config import FileConfig
from app.extensions import api, db


class ApplicationCreateSchema(BaseModel):
    full_name: str = Field(..., min_length=1, max_length=255)
    date_of_birth: date
    gender: str = Field(..., min_length=1, max_length=10)
    email: EmailStr
    phone_number: str = Field(..., min_length=1, max_length=20)
    address: str = Field(..., min_length=1, max_length=500)
    nationality: str = Field(..., min_length=1, max_length=100)
    highest_qualification: str = Field(..., min_length=1, max_length=255)
    institution_name: str = Field(..., min_length=1, max_length=255)
    graduation_year: int = Field(..., gt=1900, lt=2100)
    preferred_course_id: int

    @field_validator("gender")
    def validate_gender(cls, value: str) -> str:
        allowed_genders = ["Male", "Female", "Other"]
        if value.title() not in allowed_genders:
            raise ValueError(f"Gender must be one of {allowed_genders}")
        return value.title()

    @field_validator("phone_number")
    def validate_phone_number(cls, value):
        if not value.startswith("+") or not value[1:].isdigit():
            raise ValueError("Phone number must start with '+' and contain only digits")
        return value

    @field_validator("graduation_year")
    def validate_graduation_year(cls, value):
        current_year = datetime.now().year
        if value > current_year:
            raise ValueError("Graduation year cannot be greater than the current year")
        return value

    @field_validator("date_of_birth")
    def validate_date_of_birth(cls, value):
        today = date.today()
        age = (
            today.year
            - value.year
            - ((today.month, today.day) < (value.month, value.day))
        )
        if age < 18:
            raise ValueError("Applicant must be at least 18 years old")
        return value


class CourseCreateSchema(BaseModel):
    course_name: str = Field(..., min_length=1, max_length=255)
    max_applications_count: int = Field(..., gt=0)


class StatusChangeSchema(BaseModel):
    status: ApplicationStatus


class ApplicationAcceptanceSchema(BaseModel):
    is_enabled: bool
    start_date: Optional[date] = None
    end_date: Optional[date] = None


# Define two namespaces for grouping endpoints.
user_ns = Namespace("user", description="User operations")
admin_ns = Namespace("admin", description="Admin operations")

api.add_namespace(user_ns, path="/user")
api.add_namespace(admin_ns, path="/admin")


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            abort(403, "Authentication required") # type: ignore
        return f(*args, **kwargs)

    return decorated


def user_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or current_user.is_admin():
            abort(401, "Authentication required") # type: ignore
        return f(*args, **kwargs)

    return decorated


# --- Swagger Models (for documentation) ---

application_model = user_ns.model(
    "Application",
    {
        # 'id': fields.Integer(readonly=True),
        "full_name": fields.String(),
        "email": fields.String(),
        "status": fields.String(readonly=True),
    },
)

application_create_model = user_ns.model(
    "Application",
    {
        "full_name": fields.String(
            required=True, description="Full name of the applicant"
        ),
        "date_of_birth": fields.Date(required=True, description="Date of birth"),
        "gender": fields.String(required=True, description="Gender"),
        "phone_number": fields.String(required=True, description="Phone number"),
        "address": fields.String(required=True, description="Address"),
        "nationality": fields.String(required=True, description="Nationality"),
        "highest_qualification": fields.String(
            required=True, description="Highest qualification"
        ),
        "institution_name": fields.String(
            required=True, description="Institution name"
        ),
        "graduation_year": fields.Integer(required=True, description="Graduation year"),
        "preferred_course_id": fields.Integer(
            required=True, description="Preferred course ID"
        ),
        "email": fields.String(required=True, description="Email address"),
    },
)


course_model = admin_ns.model(
    "Course",
    {
        "id": fields.Integer(readonly=True),
        "course_name": fields.String(),
        "max_applications_count": fields.Integer(),
        "applied_count": fields.Integer(readonly=True),
    },
)

document_model = user_ns.model(
    "Document",
    {
        "id": fields.Integer(),
        "document_type_id": fields.Integer(),
        # 'file_path': fields.String(),
    },
)
application_setting_model = admin_ns.model(
    "ApplicationAcceptanceSettings",
    {
        "start_date": fields.Date(),
        "end_date": fields.Date(),
        "is_enabled": fields.Boolean(),
    },
)

document_name_model = admin_ns.model(
    "DocumentType",
    {"id": fields.Integer(readonly=True), "document_type_name": fields.String()},
)
# --- USER ENDPOINTS ---


@user_ns.route("/courses")
class CourseList(Resource):
    @login_required
    @user_ns.doc("list_courses")
    def get(self):
        """List all available courses"""
        courses = PreferredCourse.query.all()
        result = [
            {
                "id": course.id,
                "course_name": course.course_name,
            }
            for course in courses
            if course.is_available()
        ]
        return result, 200


@user_ns.route("/applications")
class UserApplication(Resource):
    @login_required
    @user_required
    @user_ns.doc("create_application")
    @user_ns.expect(application_create_model)
    def post(self):
        """Create a new application (only one allowed per user)"""

        existing_app = Application.query.filter_by(user=current_user.id).first()

        if existing_app:
            return {"message": "Application already exists for this user."}, 400
        print(request.json)
        try:
            data = ApplicationCreateSchema.model_validate(request.json)
        except ValidationError as e:
            return json.loads(e.json()), 400

        course = PreferredCourse.query.get_or_404(data.preferred_course_id)
        if not course or not course.is_available():
            return {"message": "Selected course is not available."}, 400

        application = Application(
            user=current_user.id,
            full_name=data.full_name,
            date_of_birth=data.date_of_birth,
            gender=data.gender,
            email=data.email,
            phone_number=data.phone_number,
            address=data.address,
            nationality=data.nationality,
            highest_qualification=data.highest_qualification,
            institution_name=data.institution_name,
            graduation_year=data.graduation_year,
            preferred_course_id=data.preferred_course_id,
            status=ApplicationStatus.INCOMPLETE,
        )
        db.session.add(application)
        course.applied_count += 1
        db.session.commit()
        return {
            "message": "Application created successfully.",
            "application_id": application.id,
        }, 201

    @login_required
    @user_ns.doc("get_application")
    @user_ns.marshal_with(application_model)
    def get(self):
        """Get the current user's application"""

        application = Application.query.filter_by(user=current_user.id).first()
        if not application:
            return {"message": "Your application found."}, 404
        return {
            "id": application.id,
            "full_name": application.full_name,
            "email": application.email,
            "status": application.status.value,
        }, 200


@user_ns.route("/documents")
class DocumentList(Resource):
    @login_required
    @user_ns.doc("list_documents")
    @user_ns.marshal_list_with(document_model)
    def get(self):
        """List documents for the user's application"""

        application = Application.query.filter_by(user=current_user.id).first()
        if not application:
            return {"message": "The application found."}, 404
        return [
            {
                "id": doc.id,
                "document_type_id": doc.document_type_id,
            }
            for doc in application.documents
        ], 200


upload_parser = reqparse.RequestParser()
upload_parser.add_argument(
    "document_type_id",
    type=int,
    required=True,
    help="Type of document",
    location="form",
)
upload_parser.add_argument(
    "file", location="files", type=FileStorage, required=True, help="File"
)


@user_ns.route("/documents/upload")
class DocumentUpload(Resource):
    @login_required
    @user_required
    @user_ns.doc("upload_document")
    @user_ns.expect(upload_parser)
    def post(self):
        """
        Upload a document. Once all required documents are uploaded,
        change the application status to PENDING.
        """
        application = Application.query.filter_by(user=current_user.id).first()
        if not application:
            return {"message": "No application found."}, 404

        try:
            document_type_id = int(request.form["document_type_id"])

        except Exception as e:
            return str(e), 400
        DocumentType.query.get_or_404(document_type_id)

        if "file" not in request.files:
            return {"message": "No file part in the request."}, 400

        file = request.files["file"]
        if file.filename == "":
            return {"message": "No selected file."}, 400

        # file_data = file.read()
        # file_path = f"/path/to/documents/{file.filename}"
        base_path: Path = FileConfig.UPLOAD_FILE
        file_path = base_path / f"{current_user.id}_{file.filename}"
        with open(file_path, "wb") as f:
            f.write(file.read())
        document = Document(
            application_id=application.id,
            document_type_id=document_type_id,
            file_path=str(file_path),
        )
        db.session.add(document)
        db.session.commit()
        # Adjust as needed
        if len(application.documents) >= DocumentType.query.count():
            application.status = ApplicationStatus.PENDING
            db.session.commit()

        return {
            "message": "Document uploaded successfully.",
            "document_id": document.id,
        }, 201


@user_ns.route("/status")
class ApplicationStatusCheck(Resource):
    @login_required
    @user_ns.doc("check_status")
    def get(self):
        """Check the status of the application"""
        application = Application.query.filter_by(user=current_user.id).first()
        if not application:
            return {"message": "No application found."}, 404
        return {
            "application_id": application.id,
            "status": application.status.value,
        }, 200


@user_ns.route("/letter")
class DownloadLetter(Resource):
    @login_required
    @user_ns.doc("download_letter")
    def get(self):
        """Download admission letter if available"""
        application = Application.query.filter_by(user=current_user.id).first()
        if not application:
            return {"message": "No application found."}, 404

        if (
            application.status != ApplicationStatus.APPROVED
            or not application.admission_letter_path
        ):
            return {"message": "Admission letter not available."}, 400

        fake_file = BytesIO(b"This is your admission letter content.")
        fake_file.seek(0)
        return send_file(
            fake_file,
            as_attachment=True,
            download_name="admission_letter.pdf",
            mimetype="application/pdf",
        )


# --- ADMIN ENDPOINTS ---


@admin_ns.route("/courses")
class AdminCourseList(Resource):
    @login_required
    @admin_ns.doc("list_courses")
    @admin_ns.marshal_list_with(course_model)
    def get(self):
        """List all courses"""
        courses = PreferredCourse.query.all()
        return [
            {
                "id": course.id,
                "course_name": course.course_name,
                "max_applications_count": course.max_applications_count,
                "applied_count": course.applied_count,
            }
            for course in courses
        ], 200

    @login_required
    @admin_required
    @admin_ns.doc("create_course")
    @admin_ns.expect(course_model)
    def post(self):
        """Add a new course"""
        try:
            data = CourseCreateSchema.model_validate(request.get_json())
        except ValidationError as e:
            return e.errors(), 400

        course = PreferredCourse(
            course_name=data.course_name,
            max_applications_count=data.max_applications_count,
            applied_count=0,
        )
        db.session.add(course)
        db.session.commit()
        return {"message": "Course created successfully.", "course_id": course.id}, 201


@admin_ns.route("/documents")
class AdminDocumentList(Resource):
    @login_required
    @admin_ns.doc("list_docs")
    @admin_ns.marshal_list_with(document_name_model)
    def get(self):
        """List all docs"""
        docs = DocumentType.query.all()
        return [
            {
                "id": doc.id,
                "document_type_name": doc.document_type_name,
            }
            for doc in docs
        ], 200

    @login_required
    @admin_required
    @admin_ns.doc("create_doc")
    @admin_ns.expect(document_name_model)
    def post(self):
        data = request.get_json()
        document_type_name = data.get("document_type_name")

        # Check if the document type already exists
        existing_doc = DocumentType.query.filter_by(
            document_type_name=document_type_name
        ).first()
        if existing_doc:
            return {
                "message": "Document type already exists."
            }, 400  # Return an error response

        try:
            doc = DocumentType(document_type_name=document_type_name)
            db.session.add(doc)
            db.session.commit()
            return {
                "message": "Document created successfully.",
                "document_id": doc.id,
            }, 201
        except IntegrityError:
            db.session.rollback()  # Rollback the transaction to keep DB consistent
            return {"message": "A document with this name already exists."}, 400


@admin_ns.route("/applications")
class AdminApplicationList(Resource):
    @login_required
    @admin_required
    @admin_ns.doc("list_applications")
    def get(self):
        """Get list of all applications"""
        applications = Application.query.all()
        result = [
            {
                "id": app.id,
                "full_name": app.full_name,
                "email": app.email,
                "status": app.status.value,
            }
            for app in applications
        ]
        return result, 200


application_status = reqparse.RequestParser()
application_status.add_argument(
    "status",
    type=ApplicationStatus,
    required=True,
    choices=[i.value for i in ApplicationStatus],
    help="Type of document",
    location="form",
)


@admin_ns.route("/applications/<int:application_id>/status")
class AdminApplicationStatus(Resource):
    @login_required
    @admin_required
    @admin_ns.expect(application_status)
    @admin_ns.doc("change_application_status")
    def put(self, application_id):
        """Change status of an application"""

        try:
            data = StatusChangeSchema(**request.form)
        except ValueError as e:
            return json.loads(e.json()), 400

        application = Application.query.get(application_id)
        if not application:
            return {"message": "Application not found."}, 404

        if application.status == ApplicationStatus.APPROVED:
            return {"message": "Unable to change we not have feature"}, 400
        if application.status == data.status:
            return {
                "message": "Application status updated.",
                "application_id": application.id,
                "status": application.status.value,
            }, 200
        if data.status == ApplicationStatus.APPROVED:
            application.admission_letter_path = generate_letter(application)

        application.status = data.status
        db.session.commit()
        return {
            "message": "Application status updated.",
            "application_id": application.id,
            "status": application.status.value,
        }, 200


@admin_ns.route("/acceptance")
class AdminApplicationAcceptance(Resource):
    @login_required
    @admin_required
    @admin_ns.doc("toggle_application_acceptance")
    @admin_ns.expect(application_setting_model)
    def put(self):
        """
        Enable or disable application acceptance.
        Optionally, update start_date and end_date.
        """
        try:
            data = ApplicationAcceptanceSchema.model_validate(request.get_json())
        except ValidationError as e:
            return e.errors(), 400

        settings = ApplicationAcceptanceSettings.query.first()
        if not settings:
            settings = ApplicationAcceptanceSettings()
            db.session.add(settings)

        settings.is_enabled = data.is_enabled
        settings.start_date = data.start_date
        settings.end_date = data.end_date
        db.session.commit()
        return {
            "message": "Application acceptance settings updated.",
            "is_enabled": settings.is_enabled,
            "start_date": str(settings.start_date) if settings.start_date else None,
            "end_date": str(settings.end_date) if settings.end_date else None,
        }, 200
