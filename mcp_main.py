# mcp_main.py
import io
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from transformers import pipeline
from docx import Document
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

# --- Model and App Initialization ---

# Initialize the FastAPI app
app = FastAPI(
    title="Document Summarization MCP",
    description="A microservice to summarize texts and generate a document.",
    version="1.0.0"
)

# Load the summarization model from Hugging Face.
# This happens only once when the server starts.
try:
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
    print("Summarization model loaded successfully.")
except Exception as e:
    print(f"Error loading model: {e}")
    summarizer = None

# --- Pydantic Models for Request Body ---

class SummarizationRequest(BaseModel):
    documents: dict[str, str] = Field(..., description="A dictionary where keys are filenames and values are the document's text content.")
    doc_type: str = Field("pdf", description="The desired output document type. Either 'pdf' or 'docx'.")

# --- Helper Functions for Document Generation ---

def create_pdf_from_summaries(summaries: dict[str, str]) -> io.BytesIO:
    """Generates a PDF document from a dictionary of summaries."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    for filename, summary in summaries.items():
        story.append(Paragraph(f"Summary for: {filename}", styles['h2']))
        story.append(Spacer(1, 12))
        story.append(Paragraph(summary, styles['BodyText']))
        story.append(Spacer(1, 24))

    doc.build(story)
    buffer.seek(0)
    return buffer

def create_docx_from_summaries(summaries: dict[str, str]) -> io.BytesIO:
    """Generates a DOCX document from a dictionary of summaries."""
    buffer = io.BytesIO()
    doc = Document()
    
    for filename, summary in summaries.items():
        doc.add_heading(f"Summary for: {filename}", level=2)
        doc.add_paragraph(summary)
        doc.add_paragraph() # Add a little space

    doc.save(buffer)
    buffer.seek(0)
    return buffer

# --- API Endpoint ---

@app.post("/summarize-and-create-document/")
async def summarize_and_create(request: SummarizationRequest):
    """
    Receives document texts, summarizes them, and returns a single
    consolidated PDF or DOCX file.
    """
    if not summarizer:
        return {"error": "Summarization model is not available."}, 503

    summaries = {}
    for filename, content in request.documents.items():
        # Truncate content to avoid overwhelming the model
        max_chunk_size = 1024 
        summary_text = summarizer(content[:max_chunk_size], max_length=150, min_length=40, do_sample=False)[0]['summary_text']
        summaries[filename] = summary_text

    if request.doc_type.lower() == 'pdf':
        buffer = create_pdf_from_summaries(summaries)
        media_type = "application/pdf"
        filename = "summaries.pdf"
    elif request.doc_type.lower() == 'docx':
        buffer = create_docx_from_summaries(summaries)
        media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        filename = "summaries.docx"
    else:
        return {"error": "Invalid doc_type. Must be 'pdf' or 'docx'."}, 400

    headers = {
        'Content-Disposition': f'attachment; filename="{filename}"'
    }

    return StreamingResponse(buffer, media_type=media_type, headers=headers)

@app.get("/health")
def health_check():
    return {"status": "ok" if summarizer else "degraded"}