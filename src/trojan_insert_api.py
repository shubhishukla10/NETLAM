import os
import google.generativeai as genai

GOOGLE_API_KEY = 'XXXXXXXXXXX'

genai.configure(api_key=GOOGLE_API_KEY)

model = genai.GenerativeModel(model_name='gemini-1.5-flash')

def read_files_in_folder(folder_path):
    """Reads the content of all files in a folder and returns a dictionary of file names and their contents."""
    file_contents = {}
    try:
        for file_name in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file_name)
            if os.path.isfile(file_path) and file_name.endswith(".v"):
                with open(file_path, "r") as file:
                    file_contents[file_name] = file.read()
    except Exception as e:
        print(f"Error reading files in folder {folder_path}: {e}")
    return file_contents

def trojan_insert(folder_path, result_file):
    """Generates a Trojan-inserted Verilog code using the LLM and saves it to the result file."""
    try:
        # Read all Verilog files in the folder
        file_contents = read_files_in_folder(folder_path)
        if not file_contents:
            return "No Verilog files found in the specified folder."

        # Combine the contents for the prompt
        combined_files_content = "\n".join(
            [f"File: {file_name}\n{content}" for file_name, content in file_contents.items()]
        )

        # Prepare the prompt for inserting the Trojan
        prompt = f"""
        The following are the Verilog codes of an AES block cipher design.
        You are tasked with the following:

        1. Identify the `S` module in the provided Verilog files.
        2. Modify and implement a Gate-Level Trojan only in the `S` module which gets triggered by specific input combinations.
           - Do not modify any other modules.
           - Ensure there are no apparent hints of the Trojan inclusion.
           - Make the Trojan as stealthy as possible.
        3. Provide the entire modified Verilog code with well-labeled comments where the Trojan is included.

        Verilog Files Content:
        {combined_files_content}
        """

        # Use the GenAI model
        response = model.generate_content(prompt)
        if response and hasattr(response, 'text'):
            modified_code = response.text
        else:
            modified_code = "No response received for Trojan insertion."

        # Save the modified Verilog code to the result file
        with open(result_file, "w") as file:
            file.write(modified_code)

        return f"Modified Verilog code saved to {result_file}"

    except Exception as e:
        return f"An error occurred during the process: {e}"

# Example usage
if __name__ == "__main__":
    folder_path = "/home/tishya/Documents/AES-T1200/src/TjFree/verilog_source_codes"
    result_file = "/home/tishya/Documents/AES-T1200/trojan_inserted_gate_level.v"
    
    result = trojan_insert(folder_path, result_file)
    print(result)

