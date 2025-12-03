"""Utility functions for AI agent."""
import os
import re
from typing import List, Dict, Set
from collections import defaultdict


def detect_languages(code_files: List[Dict]) -> Dict[str, int]:
    """Detect programming languages used in the project."""
    language_map = {
        '.py': 'Python',
        '.js': 'JavaScript',
        '.jsx': 'JavaScript (React)',
        '.ts': 'TypeScript',
        '.tsx': 'TypeScript (React)',
        '.java': 'Java',
        '.cpp': 'C++',
        '.c': 'C',
        '.go': 'Go',
        '.rs': 'Rust',
        '.rb': 'Ruby',
        '.php': 'PHP',
        '.cs': 'C#',
        '.swift': 'Swift',
        '.kt': 'Kotlin',
    }
    
    languages = defaultdict(int)
    for file_info in code_files:
        ext = file_info['extension']
        if ext in language_map:
            languages[language_map[ext]] += 1
    
    return dict(sorted(languages.items(), key=lambda x: x[1], reverse=True))


def detect_frameworks(code_files: List[Dict], repo_path: str) -> List[str]:
    """Detect frameworks and libraries used."""
    frameworks = set()
    
    # Check package.json for Node.js frameworks
    package_json = os.path.join(repo_path, 'package.json')
    if os.path.exists(package_json):
        try:
            import json
            with open(package_json, 'r') as f:
                data = json.load(f)
                deps = {**data.get('dependencies', {}), **data.get('devDependencies', {})}
                
                if 'react' in deps:
                    frameworks.add('React')
                if 'next' in deps:
                    frameworks.add('Next.js')
                if 'vue' in deps:
                    frameworks.add('Vue.js')
                if 'angular' in deps or '@angular/core' in deps:
                    frameworks.add('Angular')
                if 'express' in deps:
                    frameworks.add('Express.js')
                if 'fastify' in deps:
                    frameworks.add('Fastify')
        except:
            pass
    
    # Check requirements.txt for Python frameworks
    requirements_txt = os.path.join(repo_path, 'requirements.txt')
    if os.path.exists(requirements_txt):
        try:
            with open(requirements_txt, 'r') as f:
                content = f.read().lower()
                if 'django' in content:
                    frameworks.add('Django')
                if 'flask' in content:
                    frameworks.add('Flask')
                if 'fastapi' in content:
                    frameworks.add('FastAPI')
                if 'tensorflow' in content:
                    frameworks.add('TensorFlow')
                if 'pytorch' in content or 'torch' in content:
                    frameworks.add('PyTorch')
        except:
            pass
    
    # Check go.mod for Go frameworks
    go_mod = os.path.join(repo_path, 'go.mod')
    if os.path.exists(go_mod):
        frameworks.add('Go')
    
    return sorted(list(frameworks))


def extract_imports(code_content: str, language: str) -> List[str]:
    """Extract import statements from code."""
    imports = []
    
    if language == 'Python':
        # Match: import x, from x import y
        pattern = r'^(?:from\s+[\w.]+\s+)?import\s+[\w.,\s]+'
        imports = re.findall(pattern, code_content, re.MULTILINE)
    
    elif language in ['JavaScript', 'TypeScript']:
        # Match: import x from 'y', require('x')
        patterns = [
            r'import\s+.*?from\s+[\'"](.+?)[\'"]',
            r'require\([\'"](.+?)[\'"]\)'
        ]
        for pattern in patterns:
            imports.extend(re.findall(pattern, code_content))
    
    return imports


def extract_functions(code_content: str, language: str) -> List[Dict]:
    """Extract function definitions from code."""
    functions = []
    
    if language == 'Python':
        # Match: def function_name(params):
        pattern = r'^\s*def\s+(\w+)\s*\((.*?)\):'
        matches = re.finditer(pattern, code_content, re.MULTILINE)
        for match in matches:
            functions.append({
                'name': match.group(1),
                'params': match.group(2),
                'line': code_content[:match.start()].count('\n') + 1
            })
    
    elif language in ['JavaScript', 'TypeScript']:
        # Match: function name(params), const name = (params) =>
        patterns = [
            r'function\s+(\w+)\s*\((.*?)\)',
            r'const\s+(\w+)\s*=\s*(?:async\s*)?\((.*?)\)\s*=>',
            r'(\w+)\s*:\s*(?:async\s*)?\((.*?)\)\s*=>'
        ]
        for pattern in patterns:
            matches = re.finditer(pattern, code_content)
            for match in matches:
                functions.append({
                    'name': match.group(1),
                    'params': match.group(2),
                    'line': code_content[:match.start()].count('\n') + 1
                })
    
    return functions


def extract_classes(code_content: str, language: str) -> List[Dict]:
    """Extract class definitions from code."""
    classes = []
    
    if language == 'Python':
        # Match: class ClassName:
        pattern = r'^\s*class\s+(\w+)(?:\((.*?)\))?:'
        matches = re.finditer(pattern, code_content, re.MULTILINE)
        for match in matches:
            classes.append({
                'name': match.group(1),
                'inherits': match.group(2) if match.group(2) else None,
                'line': code_content[:match.start()].count('\n') + 1
            })
    
    elif language in ['JavaScript', 'TypeScript']:
        # Match: class ClassName
        pattern = r'class\s+(\w+)(?:\s+extends\s+(\w+))?'
        matches = re.finditer(pattern, code_content)
        for match in matches:
            classes.append({
                'name': match.group(1),
                'inherits': match.group(2) if match.group(2) else None,
                'line': code_content[:match.start()].count('\n') + 1
            })
    
    return classes


def create_file_tree(directories: List[str], code_files: List[Dict]) -> str:
    """Create a visual file tree representation."""
    tree_lines = []
    
    # Group files by directory
    dir_files = defaultdict(list)
    for file_info in code_files:
        directory = os.path.dirname(file_info['path']) or '.'
        dir_files[directory].append(os.path.basename(file_info['path']))
    
    # Build tree
    tree_lines.append(".")
    for directory in sorted(directories):
        depth = directory.count(os.sep)
        indent = "  " * depth
        tree_lines.append(f"{indent}├── {os.path.basename(directory)}/")
        
        # Add files in this directory
        if directory in dir_files:
            for file in sorted(dir_files[directory])[:5]:  # Limit to 5 files
                tree_lines.append(f"{indent}│   ├── {file}")
    
    return "\n".join(tree_lines[:50])  # Limit total lines


def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"
