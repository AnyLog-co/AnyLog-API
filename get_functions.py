import os
import ast


def extract_function_names(file_path):
    """
    Extracts function names from a given Python file.

    Parameters:
    file_path (str): The path to the Python file.

    Returns:
    list: A list of function names defined in the file.
    """
    with open(file_path, 'r') as file:
        file_content = file.read()
    tree = ast.parse(file_content)
    function_names = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
    return function_names


def generate_content_md(base_dir, output_file):
    """
    Generates a content.md file listing directories, files, and their functions.

    Parameters:
    base_dir (str): The base directory to traverse.
    output_file (str): The output markdown file path.
    """
    content = "# Project Content\n\n"

    for root, dirs, files in os.walk(base_dir):
        # Exclude __pycache__ directories
        dirs[:] = [d for d in dirs if d != '__pycache__']

        relative_root = os.path.relpath(root, base_dir)
        content += f"## {relative_root}\n"

        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                function_names = extract_function_names(file_path)
                if function_names:
                    content += f"### {file}\n"
                    for name in function_names:
                        content += f"- {name}\n"
                    content += "\n"

    with open(output_file, 'w') as f:
        f.write(content)


if __name__ == "__main__":
    base_dir = '/Users/orishadmon/AnyLog-API/anylog_api'
    output_file = os.path.join(base_dir, 'content.md')
    generate_content_md(base_dir, output_file)
