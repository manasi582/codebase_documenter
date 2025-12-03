"""Prompts for AI documentation generation."""

MAIN_README_PROMPT = """You are an expert technical writer creating comprehensive README documentation for a software project.

Repository Information:
- Repository Name: {repo_name}
- Total Files: {total_files}
- Code Files: {code_file_count}
- Main Languages: {languages}

File Structure:
{file_structure}

Key Files Overview:
{key_files_summary}

Create a comprehensive README.md that includes:
1. Project title and brief description (infer from code structure)
2. Features (based on code analysis)
3. Technology stack (list all detected technologies)
4. Project structure overview
5. Installation instructions
6. Usage guide
7. Configuration (if config files detected)
8. Contributing guidelines
9. License information (if LICENSE file exists)

Make it professional, clear, and well-formatted in Markdown. Be specific and accurate based on the actual code.
"""

FOLDER_README_PROMPT = """Create a README.md for the following directory in a codebase:

Directory: {directory_path}
Purpose: {inferred_purpose}

Files in this directory:
{files_list}

Code snippets from key files:
{code_snippets}

Create a concise README.md that explains:
1. Purpose of this directory
2. Key files and their roles
3. How this directory fits into the larger project
4. Any important patterns or conventions used

Keep it focused and practical. Use Markdown formatting.
"""

FUNCTION_EXPLANATION_PROMPT = """Analyze and explain the following code:

File: {file_path}
Language: {language}

Code:
```{language}
{code_content}
```

Provide a detailed explanation including:
1. Overview of what this file does
2. Key functions/classes and their purposes
3. Important dependencies and imports
4. Design patterns or architectural decisions
5. Any notable algorithms or logic

Format as Markdown with clear sections. Be technical but accessible.
"""

SETUP_GUIDE_PROMPT = """Create a "How to Run" guide for this project.

Project Information:
- Languages: {languages}
- Package Managers: {package_managers}
- Frameworks: {frameworks}
- Database: {database}

Configuration Files Found:
{config_files}

Dependencies:
{dependencies}

Create a step-by-step guide including:
1. Prerequisites (required software, versions)
2. Installation steps
3. Configuration setup
4. Running the application (development mode)
5. Running tests (if test files found)
6. Building for production (if applicable)
7. Common troubleshooting tips

Be specific with actual commands based on the detected technologies.
"""

DEPENDENCY_ANALYSIS_PROMPT = """Analyze the dependencies and relationships in this codebase:

Import Graph:
{import_graph}

Key Modules:
{modules}

Identify:
1. Core modules and their responsibilities
2. Module dependencies and relationships
3. Potential circular dependencies
4. Architectural layers (if any)
5. External dependencies

Provide a clear dependency diagram description in Markdown.
"""
