Here's the content formatted as Markdown, ready for conversion:

# Major

**Major** is a comprehensive project designed to process and analyze PDF documents using advanced AI and machine learning techniques. It leverages tools like Google Generative AI, LangChain, and FAISS to extract, summarize, and answer questions from PDF content. The project also includes features for extracting images from PDFs and generating detailed descriptions of those images.

## Features

- **PDF Text Extraction**: Extract text from PDF documents for further processing.
- **Text Summarization**: Generate brief or detailed summaries of PDF content.
- **Question Answering**: Ask questions about the PDF content and get accurate answers.
- **Organization Information Extraction**: Extract key details about organizations mentioned in the PDF.
- **Image Extraction and Description**: Extract images from PDFs and generate detailed descriptions using AI.
- **Markdown Support**: All responses (summaries, answers, and image descriptions) are returned in Markdown format for easy rendering.

## Technologies Used

- **Python**: Primary programming language.
- **Flask**: Web framework for building the application.
- **Google Generative AI**: For text summarization, question answering, and image description.
- **LangChain**: For conversational chains and document processing.
- **FAISS**: For efficient similarity search and vector storage.
- **PyPDF2**: For extracting text from PDFs.
- **Fitz (PyMuPDF)**: For extracting images from PDFs.
- **Pillow (PIL)**: For image processing.

## Setup Instructions

### Prerequisites

1. **Python 3.8+**: Ensure Python is installed on your system.
2. **Google API Key**: Obtain a Google API key and set it as an environment variable.
3. **Git**: Clone the repository using Git.

### Installation

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
   Create a `.env` file in the root directory and add your Google API key:
   ```
   GOOGLE_API_KEY=your_google_api_key_here
   ```

4. Run the Flask application:
   ```bash
   python app.py
   ```

5. Access the application:
   Open your browser and navigate to `http://127.0.0.1:5000`.

## Usage

### Uploading a PDF
1. Navigate to the homepage.
2. Upload a PDF file using the file upload button.
3. Once uploaded, you can perform the following actions:
   - **Summarize PDF**: Generate a brief or detailed summary of the PDF.
   - **Ask Questions**: Ask questions about the PDF content.
   - **Extract Organization Info**: Extract key details about the organization mentioned in the PDF.
   - **Extract Images**: Extract images from the PDF and generate descriptions.

### Example Workflow
1. Upload a PDF file.
2. Click on **Summarize PDF** to generate a summary.
3. Use the **Ask Questions** feature to query specific information from the PDF.
4. Extract images and view their descriptions.

## API Endpoints

- **POST /process_pdf**: Upload and process a PDF file.
- **POST /summarize_pdf**: Generate a summary of the uploaded PDF.
- **POST /ask_question**: Answer questions based on the PDF content.
- **POST /fetch_org_info**: Extract organization information from the PDF.
- **POST /extract_images**: Extract images from the PDF and generate descriptions.

## Contributing

Contributions are welcome! If you'd like to contribute, please follow these steps:
1. Fork the repository.
2. Create a new branch for your feature or bugfix.
3. Commit your changes.
4. Submit a pull request with a detailed description of your changes.

## License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.

## Acknowledgments

- **Google Generative AI**: For providing powerful AI models.
- **LangChain**: For simplifying conversational chains and document processing.
- **FAISS**: For efficient similarity search and vector storage.

## Screenshots

![Homepage](screenshots/homepage.png)
*Homepage of the application.*

![Summary](screenshots/summary.png)
*Example of a PDF summary.*

![Question Answering](screenshots/question.png)
*Example of question answering.*

For any questions or issues, please open an issue on the [GitHub repository](https://github.com/Sid3503/Major).
