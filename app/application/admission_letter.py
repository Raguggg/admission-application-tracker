from datetime import date

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from app.config import FileConfig


def generate_admission_letter(pdf_path, student_info, admission_details):
    """
    Generates a formatted admission letter PDF.

    :param pdf_path: Path to save the PDF file.
    :param student_info: Dictionary containing student information.
                         Example:
                         {
                             "name": "John Doe",
                             "email": "john.doe@example.com",
                             "phone": "123-456-7890",
                             "
                         }
    :param admission_details: Dictionary containing admission details.
                              Example:
                              {
                                  "course": "Computer Science",
                                  "admission_date": "2025-03-01",
                              }
    """
    # Create a canvas object with letter size
    c = canvas.Canvas(pdf_path, pagesize=letter)
    width, height = letter

    # Draw header
    c.setFont("Helvetica-Bold", 22)
    c.drawCentredString(width / 2.0, height - 80, "Admission Letter")

    # Draw a line under the header for separation
    c.setLineWidth(2)
    c.line(50, height - 90, width - 50, height - 90)

    # Student Information Section
    c.setFont("Helvetica", 12)
    text = c.beginText(50, height - 130)
    text.setLeading(18)  # set the line spacing

    text.textLine("Student Information:")
    text.textLine("-------------------------")
    text.textLine(f"Name: {student_info.get('name', 'N/A')}")
    text.textLine(f"Email: {student_info.get('email', 'N/A')}")
    text.textLine(f"Phone: {student_info.get('phone', 'N/A')}")
    text.textLine("")  # Add a blank line

    # Admission Details Section
    text.textLine("Admission Details:")
    text.textLine("-------------------------")
    text.textLine(f"Course: {admission_details.get('course', 'N/A')}")
    text.textLine(f"Admission Date: {admission_details.get('admission_date', 'N/A')}")

    c.drawText(text)

    # Footer with a note
    c.setFont("Helvetica-Oblique", 10)
    c.drawString(
        50,
        50,
        "This is an auto-generated admission letter. For any queries, please contact the admissions office.",
    )

    # Save the PDF file
    c.save()


def generate_letter(app_obj):
    admission_details = {
        "course": app_obj.preferred_course,
        "admission_date": date.today().strftime("%Y-%m-%d"),
    }
    pdf_path = f"{app_obj.id}_admission_letter.pdf"
    file_path = FileConfig.ADMISSION_LETTER / pdf_path
    # Generate the PDF
    student_info = {
        "name": app_obj.full_name,
        "email": app_obj.email,
        "phone": app_obj.phone_number,
    }

    generate_admission_letter(str(file_path), student_info, admission_details)
    return str(file_path)
