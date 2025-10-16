# Contributors & Responsibilities

This project is distributed among four contributors, each handling different processing capabilities and infrastructure. Each contributor has equal technical responsibilities across the distributed processing pipeline. Please follow the branch and PR guidelines below for smooth collaboration.

---

## Contributor 1: Image & OCR Processing Lead
- **Responsibilities:**
  - Master service architecture and task distribution (`master_service/`)
  - Image processing pipeline (grayscale conversion)
  - OCR (Optical Character Recognition) processing
  - Result aggregation and file management for visual data
- **Key Files:**
  - `master.py`
  - `master_service/app.py`
  - `master_service/routes.py` 
  - `master_service/worker.py`
  - `slave_service/processing.py` (image processing)
  - `slave_service/ocr_processing.py`
- **Technical Tasks:**
  - Multi-threaded task distribution
  - Image format handling and conversion
  - OCR text extraction and confidence scoring
  - Base64 encoding/decoding for images
- **Deliverables:**
  - Working master server with task routing
  - Image and OCR processing modules
  - Unit tests for image/OCR pipelines

---

## Contributor 2: Text Analysis & Embedding Generation Lead  
- **Responsibilities:**
  - Slave service architecture and multi-type processing support
  - Text analysis (sentiment, statistics, keyword extraction)
  - Vector embedding generation using TF-IDF
  - Natural language processing features
- **Key Files:**
  - `slave.py`
  - `slave_service/app.py`
  - `slave_service/routes.py` (multi-type routing)
  - `slave_service/text_processing.py`
  - `slave_service/embedding_processing.py`
- **Technical Tasks:**
  - Text preprocessing and tokenization
  - Sentiment analysis algorithms
  - TF-IDF vectorization and feature extraction
  - JSON result formatting and encoding
- **Deliverables:**
  - Multi-type slave processing router
  - Text analysis and embedding modules
  - Unit tests for NLP pipelines

---

## Contributor 3: Audio & Document Processing Lead
- **Responsibilities:**
  - Audio file analysis and feature extraction
  - Document processing (PDF, DOCX, generic text)
  - Client tools and testing infrastructure
  - Multi-format file handling
- **Key Files:**
  - `slave_service/audio_processing.py`
  - `slave_service/document_processing.py`
  - `client.py`
  - `.env.example`
  - Setup and testing scripts
- **Technical Tasks:**
  - WAV audio analysis (RMS, zero-crossings, duration)
  - PDF metadata and text extraction
  - DOCX structure parsing
  - Client HTTP file upload handling
- **Deliverables:**
  - Audio and document processing modules
  - Multi-type client testing tool
  - Setup scripts and environment configuration

---

## Contributor 4: Testing, Documentation & Quality Assurance
- **Responsibilities:**
  - Comprehensive testing framework for all processing types
  - Complete project documentation and API specs
  - Code quality, style consistency, and CI/CD
  - Performance monitoring and optimization
- **Key Files:**
  - `README.md`
  - `CONTRIBUTORS.md`
  - Test files and test data
  - Performance benchmarks
  - API documentation
- **Technical Tasks:**
  - Unit test development for all processing modules
  - Integration testing for master-slave communication
  - Performance benchmarking and optimization
  - API documentation and usage examples
- **Deliverables:**
  - Complete test suite (pytest)
  - Comprehensive documentation
  - Performance benchmarks and optimization recommendations

---

---

## Processing Capabilities Overview

The system now supports 6 different processing types:

1. **Image Processing** - Grayscale conversion, format handling
2. **OCR Processing** - Text extraction from images, confidence scoring  
3. **Text Analysis** - Sentiment analysis, statistics, keyword extraction
4. **Embedding Generation** - TF-IDF vectorization, feature extraction
5. **Audio Processing** - WAV analysis, RMS energy, zero-crossing rate
6. **Document Processing** - PDF/DOCX metadata, text extraction, structure analysis

## Additional Dependencies Required

Each contributor should install dependencies for their processing modules:

```powershell
# Base dependencies (all contributors)
python -m pip install Flask requests Pillow python-dotenv

# Contributor 1 (Image & OCR)
python -m pip install pytesseract

# Contributor 2 (Text & Embeddings) 
python -m pip install scikit-learn nltk

# Contributor 3 (Audio & Documents)
python -m pip install PyPDF2 python-docx numpy

# Contributor 4 (Testing)
python -m pip install pytest pytest-cov
```

## API Endpoints by Processing Type

- `POST /assign_task` with `task_type=image` and `images` files
- `POST /assign_task` with `task_type=text` and `texts` files  
- `POST /assign_task` with `task_type=embedding` and `texts` files
- `POST /assign_task` with `task_type=ocr` and `images` files
- `POST /assign_task` with `task_type=audio` and `audio_files` files
- `POST /assign_task` with `task_type=document` and `documents` files

## Branch & PR Guidelines
- Use feature branches named `feature/<processing-type>-<shortdesc>` (e.g., `feature/audio-analysis`)
- Open PRs with clear descriptions and reference assigned contributor
- At least one review from another contributor required before merge
- Keep documentation up to date with code changes
- Test your processing module independently before integration

## Milestones
- v1.0: Basic distributed processing for all 6 types with master/slave architecture
- v1.1: Advanced processing features (ML models, advanced NLP, audio spectrograms)
- v1.2: Performance optimization, caching, and horizontal scaling
- v1.3: Web UI, real-time processing, and monitoring dashboard

---

For questions, open an issue or tag the relevant contributor in your PR.
