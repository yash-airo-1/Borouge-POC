import streamlit as st
import pdfplumber
import openai
import os
from dotenv import load_dotenv
from fpdf import FPDF
import io

load_dotenv()

st.title('Sample RBI Analyzer')
st.write('Upload an RBI PDF document to analyze.')

openai_api_key = os.getenv('OPENAI_API_KEY')

uploaded_file = st.file_uploader('Choose a PDF file', type='pdf')

full_text = ''
tables_content = []

if uploaded_file and openai_api_key:
    with pdfplumber.open(uploaded_file) as pdf:
        for page in pdf.pages:
            full_text += page.extract_text() or ''
            tables = page.extract_tables()
            for table in tables:
                tables_content.append(table)

    # Filter out tables with signature/closing phrases
    signature_phrases = [
        "yours faithfully", "regards", "sincerely", "truly yours", "faithfully yours",
        "best regards", "kind regards", "warm regards", "yours truly"
    ]
    def is_signature_table(table):
        for row in table:
            for cell in row:
                if cell and any(phrase in cell.lower() for phrase in signature_phrases):
                    return True
        return False
    filtered_tables_content = [
        table for table in tables_content if not is_signature_table(table)
    ]

    col1, col2 = st.columns(2)
    view_tables = col1.button('View Table Content')
    summarize = col2.button('Summarize Document')

    if view_tables:
        st.subheader('Extracted Table Content')
        if filtered_tables_content:
            for idx, table in enumerate(filtered_tables_content):
                st.write(f'Table {idx+1}:')
                st.table(table)
        else:
            st.write('No tables found in the document.')

    if summarize:
        st.subheader('Analysis Results')
        prompt = f"""
You are an expert at analyzing RBI documents. Given the following document text, extract:
- Issued date
- Publisher
- Target groups
- Actions needed according to the document

Document text:
{full_text}

Please provide ONLY the extracted information in a clear, structured format. Do NOT include any introductory or summary lines.
"""
        try:
            client = openai.OpenAI(api_key=openai_api_key)
            response = client.chat.completions.create(
                model='gpt-4o',
                messages=[{"role": "user", "content": prompt}],
                temperature=0
            )
            analysis_result = response.choices[0].message.content
            st.write(analysis_result)

            # PDF generation and download (robust)
            font_path = os.path.join(os.path.dirname(__file__), 'DejaVuSans.ttf')
            if not os.path.exists(font_path) or os.path.getsize(font_path) < 100000:
                st.error('DejaVuSans.ttf font file is missing or invalid. Please download and place it in the analyzer directory.')
            elif not analysis_result.strip():
                st.error('No analysis result to export. Please run the analysis first.')
            else:
                pdf = FPDF()
                pdf.add_page()
                pdf.add_font('DejaVu', '', font_path, uni=True)
                pdf.set_font('DejaVu', '', 12)
                pdf.set_auto_page_break(auto=True, margin=15)
                for line in analysis_result.split('\n'):
                    pdf.multi_cell(0, 10, line)
                pdf_output = pdf.output(dest='S')
                # Handle both str and bytes return types for compatibility
                if isinstance(pdf_output, str):
                    pdf_bytes = pdf_output.encode('latin1')
                else:
                    pdf_bytes = pdf_output
                st.download_button(
                    label='Download Analysis as PDF',
                    data=pdf_bytes,
                    file_name='analysis_result.pdf',
                    mime='application/pdf'
                )
        except Exception as e:
            st.error(f'Error communicating with OpenAI or generating PDF: {e}')
elif not openai_api_key:
    st.error('OpenAI API key not found. Please set OPENAI_API_KEY in your .env file.') 