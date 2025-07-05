import os
import re
import io
import pdfplumber
from personal import data_tokens, page_data_breakpoints, user_data

# Define directories
input_dir = "./test/files"
output_dir = "./test/output"
os.makedirs(output_dir, exist_ok=True)

# helper to clean relevant string
def slice_related_data(text: str, breakpoints: dict[str, str]) -> str:
    for breakpoint in breakpoints:
        match = re.search(
            re.escape(breakpoint), text, flags=re.IGNORECASE)
        if match:
            if breakpoints[breakpoint] == "before":
                index = match.start()
                text = text[:index]
            elif breakpoints[breakpoint] == "after":
                index = match.end()
                text = text[index:]
    return text  # strings immutable so this is local


def clean_text(pdf: pdfplumber.PDF, output_filename: str) -> str:
    file_token = f"<{output_filename}>"
    text = file_token
    for page_num in range(len(pdf.pages)):
        page = pdf.pages[page_num]
        page_text = page.extract_text()
        if page_text:
            valid_page = False
            for token in data_tokens:
                if len(re.findall(re.escape(token), page_text, flags=re.IGNORECASE)) > 0:
                    valid_page = True
                    break
            if not valid_page: continue

            page_text = slice_related_data(page_text, page_data_breakpoints)

            page_token = f"<page_{page_num + 1}>"
            text += f"\n{page_token}" + page_text
            text += f"{page_token}"

    text += f"\n{file_token}"
    text = text.strip()
    # clean sensitive data
    for data in user_data:
        text = re.sub(re.escape(data), "***",
                        text, flags=re.IGNORECASE)
    return text

def parse_pdf(input_dir: str, output_dir: str) -> dict[str, str]:
    if not os.path.exists(output_dir):
        raise FileNotFoundError(f"Output directory does not exist: {output_dir}")
    files = [f for f in os.listdir(input_dir) if f != ".gitkeep"]
    
    output = {}
    for filename in files:
        # Only process PDF files
        if not filename.lower().endswith(".pdf"):
            print(f"Skipping non-PDF file: {filename}")
            continue
            
        pdf_path = os.path.join(input_dir, filename)
        # Create output filename by replacing .pdf with .txt
        output_filename = filename.rsplit(".pdf", 1)[0] + ".txt"
        output_path = os.path.join(output_dir, output_filename)
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                text = clean_text(pdf, output_filename)
            
                # Write the extracted text to the output file
            with open(output_path, "w", encoding="utf-8") as output_file:
                output_file.write(text)
                print(f"Successfully extracted text from {filename} to {output_filename}")
                # small warn: this is inclusive of our special tokens
                print(f"Extracted {len(text)} characters from {len(pdf.pages)} pages")

            output[output_filename] = text
        except Exception as e:
            print(f"Error processing {filename}: {e}")
            
    return output

def parse_pdf_binary(filename: str, bytes: bytes, output_dir: str) -> dict[str, str]:
    if not os.path.exists(output_dir):
        raise FileNotFoundError(
            f"Output directory does not exist: {output_dir}")
    output = {}
    output_filename = filename.rsplit(".pdf", 1)[0] + ".txt"
    output_path = os.path.join(output_dir, output_filename)

    try:
        with pdfplumber.open(io.BytesIO(bytes)) as pdf:
            text = clean_text(pdf, output_filename)
            
        # Write the extracted text to the output file
        with open(output_path, "w", encoding="utf-8") as output_file:
            output_file.write(text)
            print(f"Successfully extracted text from {filename} to {output_filename}")
            # small warn: this is inclusive of our special tokens
            print(f"Extracted {len(text)} characters from {len(pdf.pages)} pages")

        output[output_filename] = text
    except Exception as e:
        print(f"Error processing {filename}: {e}")
            
    return output


if __name__ == "__main__":
    pass
    # parse_pdf(input_dir, output_dir)
    # with open("./test/files/name.pdf", "rb") as f:
    #     parse_pdf_binary("name.pdf", f.read(), output_dir)