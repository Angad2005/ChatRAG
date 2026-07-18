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

# Load the text generation model from Hugging Face.
# This happens only once when the server starts.
try:
    # Using GPT-2 for text generation, which is available in older transformers versions
    generator = pipeline("text-generation", model="gpt2")
    print("Text generation model loaded successfully.")
except Exception as e:
    print(f"Error loading model: {e}")
    generator = None

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
        doc.add_paragraph()  # Add a little space

    doc.save(buffer)
    buffer.seek(0)
    return buffer

# --- Helper Function for Text Generation ---

def generate_summary(text: str) -> str:
    """Generate a summary of the given text using the language model."""
    if not generator:
        return "Summarization model is not available."
    
    # Truncate input to a reasonable length (GPT-2 has a limit of 1024 tokens, but we'll be safe)
    max_input_length = 500
    truncated_text = text[:max_input_length]
    
    # Create a prompt that encourages summarization
    prompt = f"Summarize the following text:\n\n{truncated_text}\n\nSummary:"
    
    try:
        # Generate the summary
        result = generator(
            prompt,
            max_length=len(prompt.split()) + 150,  # Allow up to 150 tokens for the summary
            num_return_sequences=1,
            do_sample=False,
            truncation=True
        )
        # The generated text includes the prompt, so we extract the summary part
        generated_text = result[0]['generated_text']
        # Extract the summary after the "Summary:" prompt
        if "Summary:" in generated_text:
            summary = generated_text.split("Summary:")[-1].strip()
        else:
            # Fallback: take the part after the prompt
            summary = generated_text[len(prompt):].strip()
        return summary
    except Exception as e:
        print(f"Error during summary generation: {e}")
        return "Failed to generate summary."

# --- API Endpoint ---

@app.post("/summarize-and-create-document/")
async def summarize_and_create(request: SummarizationRequest):
    """
    Receives document texts, summarizes them, and returns a single
    consolidated PDF or DOCX file.
    """
    if not generator:
        return {"error": "Summarization model is not available."}, 503

    summaries = {}
    for filename, content in request.documents.items():
        summary = generate_summary(content)
        summaries[filename] = summary

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
    return {"status": "ok" if generator else "degraded"}