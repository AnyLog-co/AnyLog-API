import os
import ast

def extract_classes_and_functions(file_path):
    with open(file_path, 'r') as file:
        file_content = file.read()
    tree = ast.parse(file_content)
    classes = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            methods = [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
            classes[node.name] = methods
        elif isinstance(node, ast.FunctionDef):
            if None not in classes:
                classes[None] = []
            classes[None].append(node.name)
    return classes


def generate_detailed_readme(base_dir):
    readme_content = "# Project Documentation\n\n"
    for root, _, files in os.walk(base_dir):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                classes_and_functions = extract_classes_and_functions(file_path)
                if classes_and_functions:
                    relative_path = os.path.relpath(file_path, base_dir)
                    readme_content += f"## {relative_path}\n"
                    for cls, funcs in classes_and_functions.items():
                        if cls:
                            readme_content += f"### Class: {cls}\n"
                        else:
                            readme_content += "### Functions\n"
                        for func in funcs:
                            readme_content += f"- {func}\n"
                    readme_content += "\n"

    with open(os.path.join(base_dir, "README.md"), 'w') as readme_file:
        readme_file.write(readme_content)


if __name__ == "__main__":
    project_dir = os.path.dirname(os.path.abspath(__file__))  # Or set the path to your project
    generate_detailed_readme(project_dir)
