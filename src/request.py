import requests
import base64
import ollama

def test():
    filename = "aug-23.pdf"
    with open(f"../test/files/{filename}", "rb") as f:
        pdf_bytes = f.read()
    
    # Base64 encode bytes for JSON serialization
    encoded_bytes: str = base64.b64encode(pdf_bytes).decode('utf-8')
    print(f"Original bytes length: {len(pdf_bytes)}")
    print(f"Encoded string length: {len(encoded_bytes)}")
    
    # Test decode locally
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
        messages = [
            {"role": "user", "content": "allocate each bank statement row by category: " + res.json()[filename.split(".")[0] + ".txt"]}
        ]

        llm = ollama.chat(
            model="llama3.2:latest",
            messages=messages
        )
        content = llm.message.content
        print("Bot:", content)
        messages.append(
            {"role": "assistant", "content": content}
        )

if __name__ == "__main__":
    test() 