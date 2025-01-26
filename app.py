import streamlit as st
import pandas as pd
import re
import fitz  # PyMuPDF for faster PDF processing

# Function to extract text from a PDF using PyMuPDF
def extract_text_from_pdf(file_path):
    pdf_document = fitz.open(file_path)
    text = ""
    for page in pdf_document:
        text += page.get_text()
    pdf_document.close()
    return text

# Function to preprocess the text
def preprocess_text(text):
    # Remove excessive whitespace, line breaks, and unnecessary characters
    text = re.sub(r"\s+", " ", text)
    return text.strip()

# Function to extract and classify clauses
def extract_and_classify_clauses(text):
    # Define clause patterns and associated business areas
    patterns = {
        "Care Contingency / Patient Care Safeguard": r"(continuity of care|patient care)",
        "Contract Administration / Notices": r"(policy updates|emergency admission|changes to required documentation)",
        "Revenue Cycle Management": r"(requests for additional information|overpayment recovery|claim denial resolution)",
        "Billing and Collection": r"(prohibited billing practices|false claims|billing compliance)",
        "Contract Termination": r"(termination notice|termination process)",
    }

    clauses = []
    for category, pattern in patterns.items():
        # Match patterns in the text
        matches = re.finditer(pattern, text, flags=re.IGNORECASE)
        for match in matches:
            clause_text = match.group(0).strip()  # Extract the matched clause
            clauses.append({
                "Obligation Type": category,
                "Description": clause_text,
                "Business Area": "Operational Risk Management" 
                                if "Contract Administration" in category or "Care Contingency" in category 
                                else "Financial Risk Management"
            })
    return clauses

# Function to create a structured table
def create_table(clauses):
    return pd.DataFrame(clauses)

# Streamlit app
st.title("Document Clause Extractor")
st.write("Upload a PDF document to extract and generate a structured table with full clauses in the **Description** column.")

# File upload
uploaded_file = st.file_uploader("Upload your PDF document", type=["pdf"])

if uploaded_file is not None:
    # Extract text from PDF
    st.write("Processing PDF document...")
    document_text = extract_text_from_pdf(uploaded_file)

    # Preprocess the text
    processed_text = preprocess_text(document_text)

    # Display extracted text (optional for debugging)
    if st.checkbox("Show extracted text"):
        st.write(processed_text)

    # Extract and classify clauses
    st.write("Extracting and classifying clauses...")
    classified_clauses = extract_and_classify_clauses(processed_text)

    # Generate the table
    if classified_clauses:
        table = create_table(classified_clauses)
        st.write("Generated Table:")
        st.table(table)  # Display table on the page

        # Downloadable CSV
        csv = table.to_csv(index=False)
        st.download_button(
            label="Download Table as CSV",
            data=csv,
            file_name="extracted_clauses.csv",
            mime="text/csv"
        )
    else:
        st.warning("No clauses matched the predefined patterns. Try refining your document.")
