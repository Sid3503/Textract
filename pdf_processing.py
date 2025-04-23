# pdf_processing.py
import os
from PyPDF2 import PdfReader
from flask import Flask, request, render_template, jsonify
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
import google.generativeai as genai
from langchain.memory import ConversationBufferMemory
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
from langchain_community.vectorstores import FAISS, Chroma
from langchain_community.embeddings import HuggingFaceInstructEmbeddings
from langchain_community.llms import HuggingFaceHub
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from tabula.io import read_pdf
import fitz
from PIL import Image
import pandas as pd

# Load environment variables
load_dotenv()
os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def get_pdf_text(pdf_path):
    """Extract text from the PDF."""
    text = ""
    pdf_reader = PdfReader(pdf_path)
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

def get_text_chunks(text):
    """Split text into chunks for processing."""
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    chunks = text_splitter.split_text(text)
    return chunks

def load_vector_store():
    """Load or initialize FAISS vector store."""
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    if os.path.exists("faiss_index"):
        # Load the vector store from the saved index
        return FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
    else:
        raise ValueError("Vector store not found. Please upload and process a PDF first.")

def get_conversational_chain():
    """Initialize the conversational chain using Google Generative AI."""
    prompt_template = """
    Based on the following context items from the organizational document, please provide a comprehensive summary of the answer related to context...
    The user question can be anything like a word related or in the pdf, be robust to extract relevant answers according to given word or words.
    Sometimes the user would just give some word or 2-3 words as question.
    So extract answers from context according to those words.
    {context}
    User query: {question}
    Answer:
    """
    model = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.8)
    prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
    chain = load_qa_chain(model, chain_type="stuff", prompt=prompt)
    return chain

def summarize_data(pdf_path):
    """Summarize content from PDF."""
    text_data = get_pdf_text(pdf_path)
    summray_type = request.form.get('summary_type')
    if summray_type == "brief":
        default_prompt = "Summarize and extract text (keyword information) from documents relevant to organizational needs in brief in 5-6 lines mentioning about company name and core components of the pdf."
        model = genai.GenerativeModel("gemini-1.5-flash")
        response_stream = model.generate_content(
            [default_prompt, text_data],
            generation_config=genai.types.GenerationConfig(temperature=0.7),
            stream=True
        )
        summary_output = ""
        for message in response_stream:
            summary_output += message.text
        response_stream.resolve()
        return summary_output
    
    else:
        default_prompt = "Summarize and extract text (keyword information) from documents relevant to organizational needs."
        model = genai.GenerativeModel("gemini-1.5-flash")
        response_stream = model.generate_content(
            [default_prompt, text_data],
            generation_config=genai.types.GenerationConfig(temperature=0.7),
            stream=True
        )
        summary_output = ""
        for message in response_stream:
            summary_output += message.text
        response_stream.resolve()
        return summary_output

def user_input(user_question):
    """Handle user queries using a conversational chain and Gemini API, merging both responses."""
    try:
        new_db = load_vector_store()
        docs = new_db.similarity_search(user_question)
        
        # Extract information using the conversational chain
        chain = get_conversational_chain()
        response = chain({"input_documents": docs, "question": user_question}, return_only_outputs=True)
        document_response = response["output_text"]
        
        # Generate a complementary answer using Gemini API
        model = genai.GenerativeModel("gemini-1.5-flash")
        response_stream = model.generate_content(
            [f"Based on the following document context, provide a detailed answer:\n{document_response}"],
            generation_config=genai.types.GenerationConfig(temperature=0.7),
            stream=True
        )
        general_answer = ""
        for message in response_stream:
            general_answer += message.text
        response_stream.resolve()
        
        # Merge both responses intelligently
        combine_prompt = f"""
        You are an AI assistant combining insights from multiple sources into a structured answer.

        Document-based insights:
        {document_response}

        Additional AI-generated insights:
        {general_answer}

        Please merge these responses into a well-structured, informative, and comprehensive answer.
        """
        
        combined_response_stream = model.generate_content(
            [combine_prompt],
            generation_config=genai.types.GenerationConfig(temperature=0.5),
            stream=True
        )
        final_response = ""
        for message in combined_response_stream:
            final_response += message.text
        combined_response_stream.resolve()
        
        return final_response
    except Exception as e:  
        return f"Error: {str(e)}"
    

def fetch_org_info_from_genai(filepath):
    text_data = get_pdf_text(filepath)

    # Generalized prompt to adapt to different PDF types
    dynamic_prompt = (
        "Analyze the following document and extract details about the organization it is associated with. "
        "If the document is an HR manual or policy document, focus on the organization name, policies, and structure. "
        "If it is a research paper, thesis, or technical report, identify the institution, funding sources, and affiliations. "
        "For business reports, contracts, or legal documents, extract relevant company details and contractual entities. "
        "Ensure the response is structured and relevant to the document type."
    )

    model = genai.GenerativeModel("gemini-1.5-flash")

    response_stream = model.generate_content(
        [dynamic_prompt, text_data],
        generation_config=genai.types.GenerationConfig(temperature=0.7),
        stream=True
    )
    
    org_info_output = ""
    for message in response_stream:
        if hasattr(message, 'text'):
            org_info_output += message.text
        else:
            raise ValueError("No valid text in the response part.")

    response_stream.resolve()

    return org_info_output


def fetch_images(pdf_path):
    folder_path = os.path.dirname(pdf_path)
    image_folder = os.path.join(folder_path, "images")
    os.makedirs(image_folder, exist_ok=True)

    pdf_document = fitz.open(pdf_path)
    for page_number in range(len(pdf_document)):
        page = pdf_document[page_number]
        image_list = page.get_images(full=True)
        for image_index, img in enumerate(image_list):
            xref = img[0]
            base_image = pdf_document.extract_image(xref)
            image_bytes = base_image["image"]
            image_name = f"image_page_{page_number + 1}_index_{image_index}.png"
            image_path = os.path.join(image_folder, image_name)
            with open(image_path, "wb") as image_file:
                image_file.write(image_bytes)

def fetch_and_display_image_info(folder_path):
    parent_directory = os.path.dirname(folder_path)
    # st.write(parent_directory)
    image_folder = os.path.join(parent_directory, "images")
    # st.write(image_folder)
    image_files = os.listdir(image_folder)
    for image_file in image_files:
        image_path = os.path.join(image_folder, image_file)
        image = Image.open(image_path)

        # image_data = input_image_setup(image_path)
        # response = get_gemini_response(input_prompt, image_data, input_prompt)
        model = genai.GenerativeModel("gemini-1.5-flash")
        # def to_markdown(text):
        #     text = text.replace("•", "  *")
        #     return Markdown(textwrap.indent(text, "> ", predicate=lambda _: True))
        # response = get_gemini_response(input, image, input_prompt)
        response = model.generate_content(["Describe in detail the image", image], stream=True)
        response.resolve()

def fetch_tables_and_images(pdf_path):
    """Extract tables from PDF and save them as CSV files."""
    # Extract tables
    dfs = read_pdf(pdf_path, pages='all', multiple_tables=True)
    
    # Create tables folder
    folder_path = os.path.dirname(pdf_path)
    table_folder = os.path.join(folder_path, "tables")
    os.makedirs(table_folder, exist_ok=True)
    
    # Save each table as CSV
    table_files = []
    for i, df in enumerate(dfs):
        if not df.empty:  # Only save non-empty tables
            table_filename = f"table_no_{i+1}.csv"
            table_path = os.path.join(table_folder, table_filename)
            df.to_csv(table_path, index=False)
            table_files.append(table_filename)
    
    return table_files
