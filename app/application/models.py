import enum

from sqlalchemy import Boolean, Column, Date, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.extensions import db


class ApplicationStatus(enum.Enum):
    INCOMPLETE = "Incomplete"
    PENDING = "Pending"
    APPROVED = "Approved"
    REJECTED = "Rejected"

    def __str__(self):
        return self.value


class PreferredCourse(db.Model):
    __tablename__ = "preferred_course"
    id = Column(Integer, primary_key=True, autoincrement=True)
    course_name = Column(String(255), nullable=False)
    max_applications_count = Column(Integer, nullable=False)
    applied_count = Column(Integer, default=0)
    applications = relationship("Application", back_populates="preferred_course")

    def is_available(self) -> bool:
        return self.applied_count < self.max_applications_count  # type: ignore


class Application(db.Model):
    __tablename__ = "applications"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user = Column(Integer, ForeignKey("user.id"), nullable=False)
    full_name = Column(String(255), nullable=False)
    date_of_birth = Column(Date, nullable=False)
    gender = Column(String(10), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    phone_number = Column(String(20), nullable=False)
    address = Column(String(500), nullable=False)
    nationality = Column(String(100), nullable=False)
    highest_qualification = Column(String(255), nullable=False)
    institution_name = Column(String(255), nullable=False)
    graduation_year = Column(Integer, nullable=False)
    preferred_course_id = Column(
        Integer, ForeignKey("preferred_course.id"), nullable=False
    )
    status = Column(
        Enum(ApplicationStatus), default=ApplicationStatus.INCOMPLETE, nullable=False
    )
    admission_letter_path = Column(String(500), nullable=True)
    documents = relationship(
        "Document", back_populates="application", cascade="all, delete-orphan"
    )
    preferred_course = relationship("PreferredCourse", back_populates="applications")


class Document(db.Model):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True, autoincrement=True)
    application_id = Column(
        Integer, ForeignKey("applications.id", ondelete="CASCADE"), nullable=False
    )
    document_type_id = Column(
        Integer, ForeignKey("document_type_names.id"), nullable=False
    )
    file_path = Column(String(500), nullable=False)
    application = relationship("Application", back_populates="documents")
    document_type = relationship("DocumentType", back_populates="documents")


class DocumentType(db.Model):
    __tablename__ = "document_type_names"
    id = Column(Integer, primary_key=True, autoincrement=True)
    document_type_name = Column(String(100), nullable=False, unique=True)
    documents = relationship("Document", back_populates="document_type")


class ApplicationAcceptanceSettings(db.Model):
    __tablename__ = "application_acceptance_settings"
    id = Column(Integer, primary_key=True, autoincrement=True)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    is_enabled = Column(Boolean, default=True)
