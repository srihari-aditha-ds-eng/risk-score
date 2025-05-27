# Risk Analysis System

A Dockerized application that analyzes legal documents to identify risky clauses and assign risk scores using Google's Gemini AI.

## Prerequisites

- Docker
- Docker Compose
- Google API Key for Gemini AI

## Directory Structure

```
risk-score/
├── documents/              # Place your documents to analyze here
├── reference_documents/    # Place your reference documents here
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── run.sh
├── requirements.txt
└── ... (other Python files)
```

## Setup

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd risk-score
   ```

2. **Set up your environment:**
   - Create a `.env` file in the root directory
   - Add your Google API key:
     ```
     GOOGLE_API_KEY=your_api_key_here
     ```

3. **Place your documents:**
   - Put the documents you want to analyze in the `documents/` directory
   - Put any reference documents in the `reference_documents/` directory

## Building the Docker Image

```bash
docker-compose build
```

## Usage

### Using the run script (recommended)

```bash
# Make the script executable (if not already)
chmod +x run.sh

# Run with default document (sample_contract.txt)
./run.sh

# Run with a specific document
./run.sh documents/your_document.pdf
```

### Using Docker Compose directly

```bash
# Run with default document
docker-compose run --rm risk-analyzer

# Run with a specific document
docker-compose run --rm risk-analyzer --document documents/your_document.pdf
```

## Supported Document Types

- PDF (.pdf)
- Word (.docx, .doc)
- Text (.txt)

## Output

The analysis will provide:
1. A list of identified risky clauses
2. Risk score (0-100) with explanation
3. Comparison with similar clauses from reference documents
4. Mitigation suggestions

## Troubleshooting

1. **Permission Issues:**
   ```bash
   chmod +x run.sh
   ```

2. **API Key Issues:**
   - Ensure your `.env` file contains the correct API key
   - Verify the API key has access to Gemini AI

3. **Document Access Issues:**
   - Ensure documents are in the correct directories
   - Check file permissions

## Development

To modify the application:

1. Make your changes to the Python files
2. Rebuild the Docker image:
   ```bash
   docker-compose build
   ```
3. Test your changes using the run script

## License

[Your License Here] 