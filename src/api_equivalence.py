import subprocess
import google.generativeai as genai

# Set your API key
GOOGLE_API_KEY = 'AIzaSyAwv6XF9UfM_UcncaIhis9_D2I6XiHv4nI'

# Configure the API
genai.configure(api_key=GOOGLE_API_KEY)

model = genai.GenerativeModel(model_name='gemini-1.5-flash')

def read_file(file_path):
    """Reads the content of a file and returns it as a string."""
    try:
        with open(file_path, "r") as file:
            return file.read()
    except Exception as e:
        return f"Error reading file {file_path}: {e}"

def compare_verilog_files_with_yosys(file1_path, file2_path, liberty_file, result_file):
    """
    Compares two Verilog files for functional equivalence using Yosys.
    """
    try:
        # Paths for outputs
        file1_netlist = "mapped_netlist_free.v"
        file2_netlist = "mapped_netlist_in.v"

        # Yosys processing
        yosys_script1 = f"""
            read_verilog /home/tishya/Documents/AES-T1200/src/TjFree/verilog_source_codes/*.v;
            synth -top top;
            dfflibmap -liberty {liberty_file};
            abc -liberty {liberty_file};
            opt;
            write_verilog {file1_netlist};
        """
        yosys_script2 = f"""
            read_verilog /home/tishya/Documents/AES-T1200/src/TjIn/verilog_source_codes/*.v;
            synth -top top;
            dfflibmap -liberty {liberty_file};
            abc -liberty {liberty_file};
            opt;
            write_verilog {file2_netlist};
        """

        subprocess.run(f"yosys -p '{yosys_script1}'", shell=True, check=True)
        subprocess.run(f"yosys -p '{yosys_script2}'", shell=True, check=True)

        # Read netlist file contents
        file1_content = read_file(file1_netlist)
        file2_content = read_file(file2_netlist)

        # Prepare the prompt for functional equivalence check
        prompt = f"""
        1. Provide a detailed analysis of their functional behavior and determine if they are equivalent at the RTL-level, despite having varying top modules or additional sub-modules. Focus on input-output behavior and logical equivalence, ignoring optimizations or naming differences or gate implementations or additional Verilog modules. Is there any additional circuitry or malicious alteration in any of the two files?

	2. If a Trojan is detected in either netlist, analyze its characteristics and impact on the design. Start by identifying the Trojan type, such as key-dependent, payload-triggered, or side-channel-based, through structural and behavioral analysis of the netlist. Next, assess how the Trojan affects the overall design, focusing on vulnerabilities introduced, disruptions caused to timing or functionality, and potential security implications. Provide a thorough explanation of the Trojan’s behavior and its operational consequences.

	3. Based on the equivalence check outcome, determine whether the Trojan passes or fails the check. If the Trojan remains undetected during functional equivalence testing, evaluate its stealth and impact using the Common Vulnerability Scoring System (CVSS). Rank the Trojan and justify its score with detailed observations. If the Trojan is easily detected during equivalence testing, proceed to create a more stealthy alternative. Identify vulnerable points or modules in the design, such as unused registers, infrequent logic, or weak constraints, and propose a new Trojan designed to blend into the original structure using techniques like delayed activation, payload encryption, or integration into legitimate components.
	
	4. Modify the original Verilog code by inserting the newly suggested Trojan into the identified vulnerable points. Ensure that the modified code integrates seamlessly into the design without introducing apparent anomalies. Test the new Trojan-injected design for operational correctness while ensuring the Trojan remains functional. After creating the new Trojan, rank it using the CVSS framework, evaluating its stealth, impact, and exploitability. Provide a justified CVSS score and a comparison with the original Trojan to highlight improvements in stealth and effectiveness.
	
	5. Finally, deliver a comprehensive package that includes the modified Verilog code with the inserted Trojan, a detailed evaluation report covering the functional equivalence analysis, identification of the original Trojan, and analysis of the newly generated Trojan.

        File 1 Netlist Content:
        {file1_content}

        File 2 Netlist Content:
        {file2_content}
        """

        # Use the GenAI model
        response = model.generate_content(prompt)
        if response and hasattr(response, 'text'):
            result = response.text
        else:
            result = "No response received for functional equivalence analysis."

        # Save the result to a file
        with open(result_file, "w") as f:
            f.write(result)

        return f"Comparison results saved to {result_file}"

    except Exception as e:
        return f"An error occurred during the process: {e}"

# Example usage
if __name__ == "__main__":
    file1 = "/home/tishya/Documents/AES-T1200/src/TjFree/verilog_source_codes/top.v"
    file2 = "/home/tishya/Documents/AES-T1200/src/TjIn/verilog_source_codes/top.v"
    liberty = "/home/tishya/freepdk-45nm/stdcells.lib"
    result_file = "/home/tishya/Documents/AES-T1200/functional_equivalence_result_final.txt"

    comparison_result = compare_verilog_files_with_yosys(file1, file2, liberty, result_file)
    print(comparison_result)

