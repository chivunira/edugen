import pdfplumber
import pandas as pd
import os
import re

# Get current script directory
script_dir = os.path.dirname(__file__)

# Path to the PDF file containing the notes
pdf_path = os.path.join(script_dir, '../topical_notes/grade_6_science.pdf')

# Path to the output TSV file
tsv_path = os.path.join(script_dir, 'grade_6_science_notes.tsv')

def convert_pdf_to_tsv(pdf_path, tsv_path):
    """
    Extract text from a PDF and save it to a .tsv file.
    Combines lines based on topics for more meaningful content in each row.
    """
    data = []
    current_topic = []

    # Define topic title by checking for full uppercase words
    header_pattern = re.compile(r'^[A-Z ]+$')

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                # Split text into lines
                lines = text.split('\n')
                for line in lines:
                    # Check if the line is a header (topic title)
                    if header_pattern.match(line.strip()):
                        # If there is an existing topic, save it as a row
                        if current_topic:
                            data.append([" ".join(current_topic)])
                            current_topic = []
                    # Append the line to the current topic
                    current_topic.append(line.strip())

    # Add the last topic if any
    if current_topic:
        data.append([" ".join(current_topic)])

    # Convert the data to a DataFrame
    df = pd.DataFrame(data)

    # Save the DataFrame to a TSV file
    df.to_csv(tsv_path, sep='\t', index=True, header=False)
    print(f'Successfully converted PDF to .tsv and saved at: {tsv_path}')

# Run the conversion function
convert_pdf_to_tsv(pdf_path, tsv_path)
