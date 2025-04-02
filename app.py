from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
from fpdf import FPDF
import os
from dotenv import load_dotenv
from supabase import create_client, Client
from twilio.rest import Client as TwilioClient
import dropbox
import unicodedata

load_dotenv()

app = Flask(__name__)
CORS(app)

# Supabase initialization
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Twilio configuration
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = "whatsapp:+14155238886"
twilio_client = TwilioClient(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Dropbox configuration
DROPBOX_ACCESS_TOKEN = os.getenv("DROPBOX_ACCESS_TOKEN")
dropbox_client = dropbox.Dropbox(DROPBOX_ACCESS_TOKEN)

# Create a directory for storing PDFs if it doesn't exist
os.makedirs('pdfs', exist_ok=True)

@app.route('/api/upload', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        if 'excelFile' not in request.files:
            return jsonify({'error': 'No file part'}), 400

        file = request.files['excelFile']

        if not file or not (file.filename.endswith('.xlsx') or file.filename.endswith('.xls')):
            return jsonify({'error': 'Invalid file format. Please upload an Excel file.'}), 400

        try:
            df = pd.read_excel(file)
        except Exception as e:
            return jsonify({'error': f'Error reading Excel file: {str(e)}'}), 500

        # Identify the subject columns dynamically (all columns after 'Class')
        subject_columns = df.columns[3:]  # Starts from index 3 as 'Class' is at index 2

        student_details = []

        for index, row in df.iterrows():
            student_name = row['Student Name']
            roll_number = row['Roll Number']
            student_class = row['Class']

            whatsapp_number = get_whatsapp_number_from_supabase(student_name)

            if whatsapp_number is None:
                print(f"No WhatsApp number found for {student_name}")
                continue

            # Extract the subjects and marks for the student
            subjects = subject_columns
            marks = [row[subject] for subject in subjects]
            total_marks = sum(marks)

            student_details.append({
                'name': student_name,
                'roll_number': roll_number,
                'class': student_class,
                'whatsapp_number': whatsapp_number,
                'subjects': subjects,
                'marks': marks,
                'total_marks': total_marks
            })

        for student in student_details:
            if student['whatsapp_number'] is None:
                print(f"No WhatsApp number found for {student['name']}")
                continue

            pdf_file_path = create_pdf(
                student['name'],
                student['roll_number'],
                student['class'],
                student['subjects'],
                student['marks'],
                student['total_marks']
            )

            shareable_link = upload_to_dropbox(pdf_file_path)

            send_whatsapp_message(student['whatsapp_number'], shareable_link)

        return jsonify({'message': 'Files generated and sent via WhatsApp successfully!'}), 200


def get_whatsapp_number_from_supabase(student_name):
    response = supabase.from_('sample_students').select('whatsapp_number').eq('name', student_name).execute()
    data = response.data

    if data and len(data) > 0:
        return data[0]['whatsapp_number']
    return None

def normalize_text(text):
    return unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')

def create_pdf(student_name, roll_number, student_class, subjects, marks, total_marks):
    # Function to replace special characters that can't be encoded
    def replace_special_characters(text):
        return text.replace("\u2013", "-")  # Replace en dash with a regular dash

    pdf = FPDF()
    pdf.add_page()

    pdf.image('/home/joshua/Documents/ESEC Mark Generator/ESEC_Logo.jpeg', 10, 8, 33)
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, 'Erode Sengunthar Engineering College', ln=True, align='C')

    pdf.ln(50)
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, f"Name: {student_name}", ln=True)
    pdf.cell(0, 10, f"Class: {student_class}", ln=True)
    pdf.cell(0, 10, "Dept: Artificial Intelligence and Data Science", ln=True)

    pdf.ln(10)

    pdf.set_font("Arial", 'B', 12)
    pdf.cell(100, 10, 'Subject', 1)
    pdf.cell(40, 10, 'Marks', 1)
    pdf.ln()

    pdf.set_font("Arial", size=12)

    for subject, mark in zip(subjects, marks):
        # Replace special characters in subject names
        subject = replace_special_characters(subject)

        subject_width = 100
        marks_width = 40

        pdf.multi_cell(subject_width, 10, subject, 1, align='L')  # Subject column
        pdf.set_xy(pdf.get_x() + subject_width, pdf.get_y() - 10)  # Move cursor to the next column
        pdf.cell(marks_width, 10, str(mark), 1, ln=True, align='C')  # Marks column

    pdf.ln(10)
    pdf.cell(0, 10, f"Total Marks scored by the student is {total_marks}", ln=True)

    pdf.ln(20)
    pdf.cell(0, 10, "Signature of HoD/AI&DS                                                                Signature of Principal", ln=True)

    pdf_file_path = f'pdfs/{student_name.replace(" ", "_")}_{roll_number}.pdf'
    pdf.output(pdf_file_path)
    return pdf_file_path


def upload_to_dropbox(file_path):
    with open(file_path, "rb") as f:
        dropbox_path = f"/{os.path.basename(file_path)}"
        dropbox_client.files_upload(f.read(), dropbox_path)

        shared_link_metadata = dropbox_client.sharing_create_shared_link_with_settings(dropbox_path)
        return shared_link_metadata.url

def send_whatsapp_message(whatsapp_number, file_link):
    # Ensure there are no spaces in the phone number
    whatsapp_number = whatsapp_number.strip()  # Remove any leading/trailing whitespace

    message_body = f"Dear Student, your marks report is ready. You can download your report from the following link: {file_link}"

    try:
        message = twilio_client.messages.create(
            body=message_body,
            from_=TWILIO_WHATSAPP_NUMBER,
            to=f"whatsapp:{whatsapp_number}"  # Directly format the WhatsApp number
        )

        print(message.to)
        print(f"Message sent to {whatsapp_number}: SID {message.sid}")

    except Exception as e:
        print(f"Failed to send message to {whatsapp_number}: {e}")

if __name__ == '__main__':
    app.run(debug=True)