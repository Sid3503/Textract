# 📄 Enterprise AI Assistant

**Enterprise AI Assistant** is a comprehensive project designed to process and analyze PDF documents using advanced AI and machine learning techniques. It leverages tools like Google Generative AI, LangChain, and FAISS to extract, summarize, and answer questions from PDF content. The project also includes features for extracting images from PDFs and generating detailed descriptions of those images.

## ✨ Features

### 📝 PDF Processing
- **📋 PDF Text Extraction**: Extract text from PDF documents for further processing.
- **📃 Text Summarization**: Generate brief or detailed summaries of PDF content.
- **❓ Question Answering**: Ask questions about the PDF content and get accurate answers.
- **🏢 Organization Information Extraction**: Extract key details about organizations mentioned in the PDF.
- **🖼️ Image Extraction and Description**: Extract images from PDFs and generate detailed descriptions using AI.
- **📊 Markdown Support**: All responses (summaries, answers, and image descriptions) are returned in Markdown format for easy rendering.

### 🔐 Authentication and Security
- **👤 Employee Authentication**: Secure login system using employee ID and password verification.
- **🗄️ Database Integration**: SQLite database (employees.db) for storing and verifying employee credentials.
- **🔑 Two-Factor Authentication**: Enhanced security with OTP verification.
- **📧 Email OTP Delivery**: Integration with Mailtrap for sending OTP codes to registered employee emails.
- **🔒 Session Management**: Secure session handling for authenticated users.
- **🚫 Access Control**: Restricted access to application features based on authentication status.

## 🛠️ Technologies Used

- **🐍 Python**: Primary programming language.
- **🌶️ Flask**: Web framework for building the application.
- **🧠 Google Generative AI**: For text summarization, question answering, and image description.
- **⛓️ LangChain**: For conversational chains and document processing.
- **🔍 FAISS**: For efficient similarity search and vector storage.
- **📄 PyPDF2**: For extracting text from PDFs.
- **📑 Fitz (PyMuPDF)**: For extracting images from PDFs.
- **🖌️ Pillow (PIL)**: For image processing.
- **💾 SQLite**: For employee database management.
- **📬 Mailtrap**: For secure email testing and OTP delivery.
- **🍪 Flask-Session**: For secure session management.

## 📧 Mailtrap Integration

Mailtrap is implemented for secure email testing and OTP delivery with the following features:
- **🔒 Secure Email Testing**: Test email functionality without sending real emails during development.
- **🔑 OTP Delivery**: Send one-time passwords to registered employee emails.
- **📝 Email Templates**: Customizable email templates for OTP delivery.
- **📊 Email Analytics**: Track email delivery and open rates.
- **📨 SMTP Integration**: Easy configuration with Flask's mail extension.
- **🏝️ Sandbox Environment**: Isolate testing environment from production email systems.

## 🔄 Authentication Flow

1. **🔑 Login**: Employee enters their ID and password on the login page.
2. **✅ Credential Verification**: System verifies credentials against the employees.db database.
3. **🔢 OTP Generation**: Upon successful verification, a unique OTP is generated.
4. **📤 Email Delivery**: OTP is sent to the employee's registered email via Mailtrap.
5. **🔍 OTP Verification**: Employee enters the received OTP on the verification page.
6. **🔐 Session Creation**: Upon successful OTP verification, a secure session is created.
7. **✅ Access Granted**: Employee is redirected to the main application page.

## 🚀 Setup Instructions

### 📋 Prerequisites

1. **🐍 Python 3.8+**: Ensure Python is installed on your system.
2. **🔑 Google API Key**: Obtain a Google API key and set it as an environment variable.
3. **📥 Git**: Clone the repository using Git.
4. **📬 Mailtrap Account**: Create a Mailtrap account for email testing and OTP delivery.

### ⚙️ Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Sid3503/Major.git
   cd Major
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   Create a `.env` file in the root directory and add your API keys:
   ```
   GOOGLE_API_KEY=your_google_api_key_here
   MAILTRAP_USERNAME=your_mailtrap_username
   MAILTRAP_PASSWORD=your_mailtrap_password
   SECRET_KEY=your_flask_secret_key
   ```

4. Initialize the employee database:
   ```bash
   python init_db.py
   ```

5. Run the Flask application:
   ```bash
   python app.py
   ```

6. Access the application:
   Open your browser and navigate to `http://127.0.0.1:5000`.

## 📖 Usage

### 🔐 Authentication
1. Navigate to the login page.
2. Enter your employee ID and password.
3. Check your registered email for the OTP.
4. Enter the OTP on the verification page.
5. Upon successful verification, you'll be redirected to the main application.

### 📤 Uploading a PDF
1. Navigate to the homepage after authentication.
2. Upload a PDF file using the file upload button.
3. Once uploaded, you can perform the following actions:
   - **📝 Summarize PDF**: Generate a brief or detailed summary of the PDF.
   - **❓ Ask Questions**: Ask questions about the PDF content.
   - **🏢 Extract Organization Info**: Extract key details about the organization mentioned in the PDF.
   - **🖼️ Extract Images**: Extract images from the PDF and generate descriptions.

### 🔄 Example Workflow
1. Log in with your employee credentials.
2. Verify your identity with the OTP sent to your email.
3. Upload a PDF file.
4. Click on **Summarize PDF** to generate a summary.
5. Use the **Ask Questions** feature to query specific information from the PDF.
6. Extract images and view their descriptions.

## 🔌 API Endpoints

- **🔐 GET /login**: Display the login page.
- **🔐 POST /login**: Process login credentials and send OTP.
- **✅ GET /verify**: Display the OTP verification page.
- **✅ POST /verify**: Verify the entered OTP.
- **🚪 GET /logout**: End the current session and redirect to login.
- **📤 POST /process_pdf**: Upload and process a PDF file.
- **📝 POST /summarize_pdf**: Generate a summary of the uploaded PDF.
- **❓ POST /ask_question**: Answer questions based on the PDF content.
- **🏢 POST /fetch_org_info**: Extract organization information from the PDF.
- **🖼️ POST /extract_images**: Extract images from the PDF and generate descriptions.

## 🔒 Security Features

- **🔐 Password Hashing**: Employee passwords are securely hashed in the database.
- **⏱️ OTP Expiration**: OTPs expire after a set time period for enhanced security.
- **🛡️ Rate Limiting**: Protection against brute force attacks.
- **⌛ Session Timeout**: Automatic session expiration after inactivity.
- **🔰 CSRF Protection**: Cross-Site Request Forgery protection for all forms.
- **✅ Input Validation**: Thorough validation of all user inputs.
- **🍪 Secure Cookies**: HTTP-only cookies to prevent XSS attacks.

## 👥 Contributing

Contributions are welcome! If you'd like to contribute, please follow these steps:
1. Fork the repository.
2. Create a new branch for your feature or bugfix.
3. Commit your changes.
4. Submit a pull request with a detailed description of your changes.

## 🙏 Acknowledgments

- **🧠 Google Generative AI**: For providing powerful AI models.
- **⛓️ LangChain**: For simplifying conversational chains and document processing.
- **🔍 FAISS**: For efficient similarity search and vector storage.
- **📬 Mailtrap**: For secure email testing and OTP delivery.

## 📸 Screenshots

![Login](https://github.com/user-attachments/assets/384b0fbb-d959-4c36-9191-e7d32765d0bf)
*Login page for employee authentication.*

![OTP Verification](https://github.com/user-attachments/assets/c8d82c94-0ac0-4416-8e3c-69ecba2f8a3d)
*OTP verification page.*

![Homepage](https://github.com/user-attachments/assets/b2e68020-2eab-4041-88c1-7205fa36b197)
*Homepage of the application.*

![Summary](https://github.com/user-attachments/assets/88875136-1c21-4eb0-93ad-9a689e71ec6d)

![Question Answering](https://github.com/user-attachments/assets/e5a664fc-852e-47de-9a3b-3b5a2a9d8561)
*Image & Analysis.*

## 👤 Author

For any questions or issues, please open an issue on GitHub: [@Siddharth Mishra](https://github.com/Sid3503)

---

<p align="center">
  Made with ❤️ and lots of ☕
</p>
