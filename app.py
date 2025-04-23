# app.py
import re
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from pdf_processing import get_pdf_text, get_text_chunks, summarize_data, user_input, fetch_org_info_from_genai, fetch_images
import os
from werkzeug.utils import secure_filename
import os
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import google.generativeai as genai
from langchain.memory import ConversationBufferMemory
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
from langchain_community.vectorstores import FAISS, Chroma
from langchain_community.embeddings import HuggingFaceInstructEmbeddings
from langchain_community.llms import HuggingFaceHub
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from flask_mail import Mail, Message
from flask import send_from_directory
import random
from PIL import Image
import sqlite3
import secrets
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = 'aa8104f270d2ba3bcf463e1e5a10ae64'

app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT'))
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS') == 'True'
app.config['MAIL_USE_SSL'] = os.getenv('MAIL_USE_SSL') == 'True'

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

mail = Mail(app)

def remove_markdown(text):
    """Removes markdown symbols and extra spaces from text."""
    text = re.sub(r'\*\*.*?\*\*', '', text)  # Remove headers (e.g., **Header**)
    text = re.sub(r'[\*\-] ', '', text)  # Remove bullet points
    text = re.sub(r'[#\*_\[\]()]', '', text)  # Remove markdown symbols
    text = re.sub(r'\n+', '\n', text).strip()  # Remove extra newlines
    return text

def format_text(text):
    """Formats text into structured paragraphs."""
    sections = text.split("\n")
    formatted_text = "\n\n".join(section.strip() for section in sections if section.strip())
    return formatted_text


def get_db_connection():
    """Establish a connection to the SQLite database."""
    conn = sqlite3.connect('employees.db')
    conn.row_factory = sqlite3.Row  # Enables column name-based access
    return conn

def validate_user(username, password):
    """Checks if the provided username and password are valid."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM employees WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()

    if user and user["password"] == password:  # Replace with password hashing later
        return user  # Returns the user details
    return None


def generate_otp():
    return random.randint(100000, 999999)

def send_otp_email(recipient_email, otp_code):
    msg = Message('Your OTP Code',
                  sender=os.getenv('MAIL_USERNAME'),  
                  recipients=[recipient_email])
    msg.body = f'Your OTP code is: {otp_code}'
    mail.send(msg)

def validate_email(email):
    """Basic email validation"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """Basic password validation"""
    if len(password) < 6:
        return False
    return True

def user_exists(username, email):
    """Check if username or email already exists"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM employees WHERE username = ? OR email = ?", (username, email))
    exists = cursor.fetchone() is not None
    conn.close()
    return exists

def create_user(username, employee_id, email, password):
    """Create a new user in the database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO employees (username, employee_id, password, email)
            VALUES (?, ?, ?, ?)
        ''', (username, employee_id, password, email))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Handle user registration"""
    if request.method == 'GET':
        return render_template('register.html')
    
    # Handle POST request
    username = request.form.get('username')
    employee_id = request.form.get('employee_id')
    email = request.form.get('email')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')
    
    # Basic validation
    if not all([username, employee_id, email, password, confirm_password]):
        return jsonify({'success': False, 'error': 'All fields are required'}), 400
    
    if password != confirm_password:
        return jsonify({'success': False, 'error': 'Passwords do not match'}), 400
    
    if not validate_email(email):
        return jsonify({'success': False, 'error': 'Invalid email format'}), 400
    
    if not validate_password(password):
        return jsonify({'success': False, 'error': 'Password must be at least 6 characters'}), 400
    
    if user_exists(username, email):
        return jsonify({'success': False, 'error': 'Username or email already exists'}), 400
    
    # Create user (not verified yet)
    if not create_user(username, employee_id, email, password):
        return jsonify({'success': False, 'error': 'Registration failed. Please try again.'}), 400
    
    # Generate OTP and store in session
    session['register_email'] = email
    session['register_otp'] = generate_otp()
    session['register_otp_expiry'] = (datetime.now() + timedelta(minutes=15)).timestamp()
    
    # Send OTP email
    send_otp_email(email, session['register_otp'])
    
    return jsonify({
        'success': True,
        'redirect_url': url_for('verify_registration_otp')
    })

@app.route('/verify-registration', methods=['GET', 'POST'])
def verify_registration_otp():
    """Verify OTP for new registration"""
    if 'register_email' not in session:
        return redirect(url_for('register'))
    
    if request.method == 'GET':
        return render_template('verify_new.html', email=session['register_email'])
    
    # Handle POST request
    entered_otp = request.form.get('otp')
    email = session.get('register_email')
    stored_otp = session.get('register_otp')
    expiry = session.get('register_otp_expiry')
    
    # Check if OTP is valid and not expired
    if not all([entered_otp, stored_otp, expiry]):
        flash('OTP verification failed. Please try again.', 'error')
        return redirect(url_for('register'))
    
    if datetime.now().timestamp() > expiry:
        flash('OTP has expired. Please request a new one.', 'error')
        return redirect(url_for('register'))
    
    if entered_otp != str(stored_otp):
        flash('Invalid OTP. Please try again.', 'error')
        return render_template('verify_otp.html', email=email)
    
    # Since we removed is_verified column, we'll just verify the OTP match is enough
    # No need to update any column in the database
    
    # Clear registration session data
    session.pop('register_email', None)
    session.pop('register_otp', None)
    session.pop('register_otp_expiry', None)
    
    flash('Registration successful! Please login with your credentials.', 'success')
    return redirect(url_for('login'))

@app.route('/resend-otp', methods=['POST'])
def resend_registration_otp():
    """Resend OTP for registration"""
    if 'register_email' not in session:
        return jsonify({'success': False, 'error': 'Session expired. Please restart registration.'}), 400
    
    email = session['register_email']
    
    # Generate new OTP
    session['register_otp'] = generate_otp()
    session['register_otp_expiry'] = (datetime.now() + timedelta(minutes=15)).timestamp()
    
    # Send OTP email
    send_otp_email(email, session['register_otp'])
    
    return jsonify({'success': True, 'message': 'New OTP sent to your email.'})


@app.route('/', methods=['GET', 'POST'])
def login():
    """Handles user login."""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = validate_user(username, password)

        if user:
            session['username'] = username
            session['otp'] = generate_otp()
            send_otp_email(user["email"], session['otp'])
            return jsonify({'success': True, 'redirect_url': url_for('verify_otp')})
        else:
            return jsonify({'success': False, 'error': 'Invalid username or password'}), 401
            
    # For GET requests, render the template with any flash messages
    return render_template('login_new.html')

@app.route('/verify', methods=['GET', 'POST'])
def verify_otp():
    """Handles OTP verification."""
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        entered_otp = request.form['otp']
        if entered_otp == str(session.get('otp')):
            return redirect(url_for('index'))
        else:
            flash('Invalid OTP')

    return render_template('verify_new.html')

@app.route('/index')
def index():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/process_pdf', methods=['POST'])
def process_pdf():
    if 'pdf_file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    file = request.files['pdf_file']
    
    if file.filename == '' or not file.filename.endswith('.pdf'):
        return jsonify({'error': 'Invalid file type. Only PDFs are allowed.'}), 400
    
    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        # Ensure the uploads folder exists
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])

        file.save(filepath)

        try:
            raw_text = get_pdf_text(filepath)
            text_chunks = get_text_chunks(raw_text)

            embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

            new_db = FAISS.from_texts(text_chunks, embeddings)
            new_db.save_local("faiss_index")

            new_db.persist()
        except Exception as e:
            return jsonify({'error': f'Error processing PDF: {str(e)}'}), 500
        finally:
            os.remove(filepath)

        return jsonify({'message': 'PDF processed successfully'}), 200

@app.route('/summarize_pdf', methods=['POST'])
def summarize_pdf():
    if 'pdf_file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    file = request.files['pdf_file']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join('uploads', filename)
        file.save(filepath)

        summary = summarize_data(filepath)
        formatted_summary = remove_markdown(summary)
        final_summary = format_text(formatted_summary)
        
        os.remove(filepath)
        
        return jsonify({'summary': final_summary}), 200

@app.route('/ask_question', methods=['POST'])
def ask_question():
    data = request.get_json()
    user_question = data.get('question', '')
    if user_question:
        try:
            response = user_input(user_question)
            return jsonify({'response': response}), 200
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
    else:
        return jsonify({'error': 'No question provided'}), 400

@app.route('/fetch_org_info', methods=['POST'])
def fetch_org_info():
    if 'pdf_file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    file = request.files['pdf_file']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join('uploads', filename)
        file.save(filepath)

        org_info = fetch_org_info_from_genai(filepath)
        formatted_org_info = remove_markdown(org_info)
        final_org_info = format_text(formatted_org_info)
        
        os.remove(filepath)
        
        return jsonify({'orgInfo': final_org_info}), 200
    

@app.route('/uploads/images/<filename>')
def serve_image(filename):
    return send_from_directory('uploads/images', filename)


@app.route('/extract_images', methods=['POST'])
def extract_images():
    if 'pdf_file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    file = request.files['pdf_file']
    
    if file.filename == '' or not file.filename.endswith('.pdf'):
        return jsonify({'error': 'Invalid file type. Only PDFs are allowed.'}), 400
    
    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join('uploads', filename)
        file.save(filepath)

        try:
            fetch_images(filepath)  # Extract images
            return jsonify({'message': 'Images extracted successfully'}), 200
        except Exception as e:
            return jsonify({'error': f'Error extracting images: {str(e)}'}), 500
        finally:
            os.remove(filepath)

@app.route('/analyze_images', methods=['POST'])
def analyze_images():
    if 'pdf_file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    file = request.files['pdf_file']
    
    if file.filename == '' or not file.filename.endswith('.pdf'):
        return jsonify({'error': 'Invalid file type. Only PDFs are allowed.'}), 400
    
    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join('uploads', filename)
        file.save(filepath)

        try:
            fetch_images(filepath)  # Ensure images are extracted
            image_folder = os.path.join('uploads', 'images')
            image_files = os.listdir(image_folder)
            
            images_with_descriptions = []
            for image_file in image_files:
                image_path = os.path.join(image_folder, image_file)
                image = Image.open(image_path)
                
                # Generate description using Gemini
                model = genai.GenerativeModel("gemini-1.5-flash")
                response = model.generate_content(["Describe in detail the image", image], stream=True)
                response.resolve()
                
                # Return the URL for the image
                image_url = url_for('serve_image', filename=image_file)
                images_with_descriptions.append({
                    'url': image_url,  # URL to access the image
                    'description': response.text
                })
            
            return jsonify({'images': images_with_descriptions}), 200
        except Exception as e:
            return jsonify({'error': f'Error analyzing images: {str(e)}'}), 500
        finally:
            os.remove(filepath)

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('otp', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    app.run(debug=True)
