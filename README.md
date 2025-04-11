# OCR Agent with Mistral OCR and Anthropic Claude

A powerful document analysis agent that combines Mistral's OCR capabilities with Anthropic Claude's language understanding, orchestrated through LangGraph.

## Overview

This project implements a conversational AI agent that can:

- Extract text from various document types (PDFs, images) using Mistral OCR
- Process and understand document content
- Answer questions about documents through natural language conversation
- Store and retrieve document information using a RAG system

## Features

- **Document OCR**: Accurately extract text and preserve document structure using Mistral OCR
- **Natural Language Understanding**: Process queries and generate responses using Anthropic Claude
- **Streamlit UI**: User-friendly interface for document upload and interaction
- **LangGraph Architecture**: Modular, state-based agent design for complex document workflows

## Getting Started

### Prerequisites

- Python 3.9+
- Mistral API key
- Anthropic API key

### Installation

1. Clone this repository
2. Create and activate a virtual environment:
   ```bash
   python -m venv myocr
   # On Windows
   myocr\Scripts\activate
   # On macOS/Linux
   source myocr/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Create a `.env` file with your API keys:
   ```
   MISTRAL_API_KEY=your_mistral_api_key_here
   ANTHROPIC_API_KEY=your_anthropic_api_key_here
   ```

## Directory Structure

```
ocr-agent/
│
├── app/                      # Main application code
│   ├── agent/                # LangGraph agent components
│   │   ├── graph.py          # Agent workflow definition
│   │   ├── state.py          # State management
│   │   └── tools/            # Agent tools
│   ├── ocr/                  # OCR processing
│   │   └── processor.py      # Mistral OCR integration
│   └── utils/                # Utility functions
│
├── ui/                       # Streamlit user interface
│   └── app.py                # Main Streamlit application
│
├── data/                     # Data storage
│   ├── uploads/              # Uploaded documents
│   └── vector_store/         # Vector database files
│
└── tests/                    # Test scripts
```

## Usage

### Running the Agent

Start the full application with:
```bash
python run.py
```

Or start just the Streamlit UI:
```bash
streamlit run ui/app.py
```

### Testing OCR Functionality

Test OCR on a file from the command line:
```bash
python ocr_test_wrapper.py --file path/to/your/document.pdf
```

Test OCR on a URL:
```bash
python ocr_test_wrapper.py --url https://example.com/document.pdf
```

Run the simplified OCR tester app:
```bash
streamlit run tiny_ocr_app.py
```

## OCR Processing Details

The system uses Mistral OCR for document processing, which offers:

- High-quality text extraction
- Structure preservation (headings, paragraphs, lists)
- Support for PDF documents and various image formats
- Pricing at 1000 pages per dollar (or 2000 pages per dollar with batch processing)

## LangGraph Agent Flow

1. **User Input**: The agent receives a query about a document
2. **Document Processing**: If a document is provided, it is processed with Mistral OCR
3. **Query Analysis**: The agent determines the user's intent
4. **RAG Retrieval**: Relevant information is retrieved from the document
5. **Response Generation**: Anthropic Claude generates a contextual response
6. **User Interaction**: The agent presents the information and can follow up on additional queries

## Development

### Simple Testing

For basic testing of the OCR functionality:
```bash
python test_ocr.py
```

For testing the Mistral API connection:
```bash
python test_mistral.py
```

### Environment Variables

The following environment variables can be configured in `.env`:

```
MISTRAL_API_KEY=your_mistral_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
MISTRAL_OCR_MODEL=mistral-ocr-latest
ANTHROPIC_MODEL=claude-3-7-sonnet-20250219
VECTOR_DB_PATH=./data/vector_store
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- [Mistral AI](https://www.mistral.ai/) for the OCR capabilities
- [Anthropic](https://www.anthropic.com/) for the Claude language model
- [LangChain](https://www.langchain.com/) for the LangGraph framework