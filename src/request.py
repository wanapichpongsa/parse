import requests
import base64
import openai
import os
from dotenv import load_dotenv
load_dotenv()

def test():
    filename = "dec-24.pdf"
    with open(f"../test/files/{filename}", "rb") as f:
        pdf_bytes = f.read()
    
    # Base64 encode bytes for JSON serialization
    encoded_bytes: str = base64.b64encode(pdf_bytes).decode('utf-8')
    print(f"Original bytes length: {len(pdf_bytes)}")
    print(f"Encoded string length: {len(encoded_bytes)}")
    
    try:
        test_decode = base64.b64decode(encoded_bytes)
        print(f"Decode test: {len(test_decode)} bytes, matches: {test_decode == pdf_bytes}")
    except Exception as e:
        print(f"Decode test failed: {e}")
    
    res = requests.post(
                        "http://127.0.0.1:5000/parse/binary", 
                        json={
                            "filename": filename, 
                            "bytes": encoded_bytes, 
                            "output_dir": "../test/output"
                        }
                    )
    if res.status_code != 200:
        print(f"Error: {res.json()}")
    else:
        key = filename.split(".")[0] + ".txt"
        data = res.json()[key]
        messages = [
            {"role": "user", "content": "allocate each bank statement row by category as json: " + data}
        ]
        if not os.getenv("OPENAI_API_KEY"):
            raise ValueError("OPENAI_API_KEY is not set")
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        # 99486 bytes -> 1519 tokens. Not bad. (Keep under 32K tokens)
        # Possible to build own fine-tuned tokenizer?
        llm = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            response_format={"type": "json_object"}
        )
        content = llm.choices[0].message.content
        print("Bot JSON:", content)
        import json
        parsed_obj = json.loads(content)
        print("Parsed object:", parsed_obj)
        messages.append(
            {"role": "assistant", "content": content}
        )

if __name__ == "__main__":
    test() 