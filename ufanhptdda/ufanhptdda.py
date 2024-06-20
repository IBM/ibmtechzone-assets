from fastapi import FastAPI

from pydantic import BaseModel

import subprocess
import os


class Payload(BaseModel):
    cobol_code: str


app = FastAPI()

# Get the current working directory


def compile_cobol_program(cobol_file):
    """
    Compiles the COBOL program using GnuCOBOL.

    Args:
    cobol_file (str): Path to the COBOL source file.

    Returns:
    bool: True if compilation is successful, False otherwise.
    """
    compile_command = ["cobc", "-x", "-o", "dummy", cobol_file]
    try:
        result = subprocess.run(
            compile_command,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        print(result.stdout.decode())
        return (True, False)
    except subprocess.CalledProcessError as e:
        print("Compilation failed:", e.stderr.decode())
        return (None, e.stderr.decode())


def run_cobol_program():
    """
    Runs the compiled COBOL program.

    Returns:
    str: The output of the COBOL program.
    """
    try:
        result = subprocess.run(
            ["./dummy"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        return result.stdout.decode()
    except subprocess.CalledProcessError as e:
        print("Execution failed:", e.stderr.decode())
        return e.stderr.decode()


@app.post("/compile/")
def compile_cobol(payload: Payload):

    pwd = os.getcwd()

    # Define the path to the COBOL source file
    cobol_file_path = os.path.join(pwd, "dummy.cbl")

    with open(cobol_file_path, "w") as file:
        file.write(payload.cobol_code)

    # Compile the COBOL program
    compilation = compile_cobol_program(cobol_file_path)

    if compilation[0]:
        # Run the COBOL program
        output = run_cobol_program()
        if output:
            return {"output": output}
    else:
        return {"output": compilation[1]}
