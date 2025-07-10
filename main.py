from fastapi import FastAPI, Form, File, UploadFile
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
#from fastapi.staticfiles import StaticFiles
from typing import Optional
import docx2txt
import PyPDF2

app = FastAPI()

# Enable access to static frontend
#app.mount("/static", StaticFiles(directory="static"), name="static")

# Allow frontend (JS) to talk to backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple dummy summarizer
def dummy_summarizer(text: str):
    lines = text.split('. ')
    summary = '. '.join(lines[:3])
    highlights = lines[:5]
    keywords = list(set([word.strip('.,') for word in text.split() if len(word) > 5]))[:10]
    return summary, highlights, keywords

@app.post("/summarize")
async def summarize(text: Optional[str] = Form(None), file: Optional[UploadFile] = File(None)):
    content = ""

    if file:
        filename = file.filename.lower()
        if filename.endswith(".txt"):
            content = (await file.read()).decode("utf-8")
        elif filename.endswith(".pdf"):
            reader = PyPDF2.PdfReader(file.file)
            for page in reader.pages:
                content += page.extract_text()
        elif filename.endswith(".docx"):
            content = docx2txt.process(file.file)
        else:
            return JSONResponse(status_code=400, content={"error": "Unsupported file type"})

    elif text:
        content = text
    else:
        return JSONResponse(status_code=400, content={"error": "No input provided"})

    summary, highlights, keywords = dummy_summarizer(content)

    return {
        "summary": summary,
        "highlights": highlights,
        "keywords": keywords
    }
