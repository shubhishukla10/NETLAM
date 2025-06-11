import subprocess
import google.generativeai as genai

GOOGLE_API_KEY = 'XXXXXXXXXXXX'

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
    Compares two Verilog files for functional equivalence using Yosys and DAG analysis for vulnerabilities.
    The DAG creation and vulnerability analysis will be done by the LLM.
    """
    try:
        # Paths for outputs
        file1_netlist = "mapped_netlist_free.v"
        file2_netlist = "mapped_netlist_in.v"

        # Yosys processing for the first file
        yosys_script1 = f"""
            read_verilog /home/tishya/Documents/AES-T1200/src/TjFree/verilog_source_codes/*.v;
            synth -top top;
            dfflibmap -liberty {liberty_file};
            abc -liberty {liberty_file};
            opt;
            write_verilog {file1_netlist};
        """
        subprocess.run(f"yosys -p '{yosys_script1}'", shell=True, check=True)

        # Yosys processing for the second file
        yosys_script2 = f"""
            read_verilog /home/tishya/Documents/AES-T1200/src/TjIn/verilog_source_codes/*.v;
            synth -top top;
            dfflibmap -liberty {liberty_file};
            abc -liberty {liberty_file};
            opt;
            write_verilog {file2_netlist};
        """
        subprocess.run(f"yosys -p '{yosys_script2}'", shell=True, check=True)

        # Read netlist file contents
        file1_content = read_file(file1_netlist)
        file2_content = read_file(file2_netlist)

        # Prepare the prompt for DAG creation, vulnerability analysis, and functional equivalence check
        prompt = f"""
        The following are two synthesized gate-level netlists.
        You are tasked with the following:

        1. DAG Conversion and Analysis:
	Give a small description of the circuit, what it does and what are the components involved.
	Convert the Verilog code to a Directed Acyclic Graph (DAG) to map all signals, registers, and logic blocks.
	Provide the DAG in a clear adjacency list(if possible or if not then make something of your choice) format for readability and the nodes in the DAG must be -
	    a.input and output ports and registers
	    b.wires 
	    c.input and output ports of the components.
	    
	2. Identify Vulnerable Points:
	Detect vulnerable locations (e.g., specific registers, data paths, logic gates) in the first netlist that could be exploited for hardware trojans utilizing the DAG.
	Evaluate vulnerabilities based on placement, signal flow, and sensitivity to conditions.
	For each vulnerable point, recommend the most stealthy trojan types that should pass any functional equivalence check with the original design, including:
	Trigger mechanisms (e.g., specific input sequences, clock cycles)
	Payload actions (e.g., bit-flipping, signal tampering)
	Stealth features (e.g., random activation, intermittent triggering)
	Rank the top 4-5 trojans with descriptions that align with the vulnerabilities identified.
	Print the DAG as an adjacency list.
	List the top 4-5 trojans with targeted vulnerable points in the design. Rank the Trojans using the CVSS framework, evaluating its stealth, impact, and exploitability. Also provide a justified 	CVSS score for each of them.

	Example:
	Code:
	module c17 (N1,N2,N3,N6,N7,N22,N23);

	input N1,N2,N3,N6,N7;

	output N22,N23;

	wire N10,N11,N16,N19;

	nand NAND2_1 (N10, N1, N3);
	nand NAND2_2 (N11, N3, N6);
	nand NAND2_3 (N16, N2, N11);
	nand NAND2_4 (N19, N11, N7);
	nand NAND2_5 (N22, N10, N16);
	nand NAND2_6 (N23, N16, N19);

	endmodule

	DAG:
	(1A. DAG Adjacency List)

	```
	N1:  N10
	N2:  N16
	N3:  N10, N11
	N6:  N11
	N7:  N19
	N10: N22
	N11: N16, N19
	N16: N22, N23
	N19: N23
	N22: 
	N23: 
	```
	
        File 1 Netlist Content:
        {file1_content}

        File 2 Netlist Content:
        
        {file2_content}
        """

        # Use the GenAI model to analyze the netlists, generate DAG, and check functional equivalence
        response = model.generate_content(prompt)
        if response and hasattr(response, 'text'):
            result = response.text
        else:
            result = "No response received for functional equivalence and vulnerability analysis."

        # Save the result to a file
        with open(result_file, "w") as f:
            f.write(result)

        return f"Comparison results and vulnerability analysis saved to {result_file}"

    except Exception as e:
        return f"An error occurred during the process: {e}"

# Example usage
if __name__ == "__main__":
    file1 = "/home/tishya/Documents/AES-T1200/src/TjFree/verilog_source_codes/top.v"
    file2 = "/home/tishya/Documents/AES-T1200/src/TjIn/verilog_source_codes/top.v"
    liberty = "/home/tishya/freepdk-45nm/stdcells.lib"
    result_file = "/home/tishya/Documents/AES-T1200/final_analysis_dag_with_CVSS.txt"

    comparison_result = compare_verilog_files_with_yosys(file1, file2, liberty, result_file)
    print(comparison_result)

