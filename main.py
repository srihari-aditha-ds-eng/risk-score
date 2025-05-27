import os
import argparse
from typing import List
from document_processor import DocumentProcessor
from embedding_manager import EmbeddingManager
from risk_analyzer import RiskAnalyzer

def process_reference_docs(reference_dir: str, embedding_manager: EmbeddingManager):
    """Process all reference documents and add them to the vector database."""
    doc_processor = DocumentProcessor()
    
    for filename in os.listdir(reference_dir):
        if filename.endswith(('.pdf', '.docx', '.doc')):
            file_path = os.path.join(reference_dir, filename)
            print(f"Processing reference document: {filename}")
            
            # Process document
            chunks = doc_processor.process_document(file_path)
            
            # Add to vector database
            embedding_manager.add_documents(chunks)

def analyze_document(file_path: str, embedding_manager: EmbeddingManager, risk_analyzer: RiskAnalyzer):
    """Analyze a document and provide risk assessment."""
    doc_processor = DocumentProcessor()
    
    # Process document
    print(f"Processing document: {file_path}")
    chunks = doc_processor.process_document(file_path)
    
    # Find similar documents
    print("Finding similar documents...")
    similar_docs = []
    for chunk in chunks:
        similar_docs.extend(embedding_manager.search_similar(chunk['text']))
    
    # Analyze document
    print("Analyzing document...")
    analysis = risk_analyzer.analyze_document(chunks, similar_docs)
    
    # Print results
    print("\n=== Risk Analysis Results ===")
    print(f"Risk Score: {analysis['risk_score']}/100")
    print("\nDetailed Analysis:")
    print(analysis['analysis'])

def main():
    parser = argparse.ArgumentParser(description="Document Risk Analysis System")
    parser.add_argument("--reference_dir", default="reference_docs",
                      help="Directory containing reference documents")
    parser.add_argument("--document", help="Path to document to analyze")
    args = parser.parse_args()
    
    # Create necessary directories
    os.makedirs(args.reference_dir, exist_ok=True)
    os.makedirs("vector_db", exist_ok=True)
    
    # Initialize components
    embedding_manager = EmbeddingManager()
    risk_analyzer = RiskAnalyzer()
    
    # Process reference documents if they exist
    if os.path.exists(args.reference_dir) and os.listdir(args.reference_dir):
        print("Processing reference documents...")
        process_reference_docs(args.reference_dir, embedding_manager)
    
    # Analyze document if provided
    if args.document:
        if not os.path.exists(args.document):
            print(f"Error: Document not found: {args.document}")
            return
        
        analyze_document(args.document, embedding_manager, risk_analyzer)
    else:
        print("No document provided for analysis. Use --document to specify a document.")

if __name__ == "__main__":
    main() 