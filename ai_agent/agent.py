"""AI Agent for analyzing code and generating documentation."""
import os
from typing import Dict, List, TypedDict
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from langchain.schema import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import settings
from services.file_analyzer import FileAnalyzer
from ai_agent.utils import (
    detect_languages, detect_frameworks, extract_functions,
    extract_classes, extract_imports, create_file_tree
)
from ai_agent.prompts import (
    MAIN_README_PROMPT, FOLDER_README_PROMPT,
    FUNCTION_EXPLANATION_PROMPT, SETUP_GUIDE_PROMPT
)


class AgentState(TypedDict):
    """State for the documentation agent."""
    repo_path: str
    repo_name: str
    analysis: Dict
    main_readme: str
    folder_readmes: Dict[str, str]
    function_docs: Dict[str, str]
    setup_guide: str
    status: str
    error: str


class DocumentationAgent:
    """LangGraph agent for generating comprehensive documentation."""
    
    def __init__(self):
        if settings.llm_provider == "groq":
            self.llm = ChatGroq(
                temperature=0,
                model_name=settings.groq_model,
                groq_api_key=settings.groq_api_key
            )
        else:
            self.llm = ChatOpenAI(
                temperature=0,
                model_name=settings.openai_model,
                openai_api_key=settings.openai_api_key
            )
        self.file_analyzer = FileAnalyzer()
        self.workflow = self._create_workflow()
    
    def _create_workflow(self) -> StateGraph:
        """Create the LangGraph workflow."""
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("analyze_repository", self.analyze_repository)
        workflow.add_node("generate_main_readme", self.generate_main_readme)
        workflow.add_node("generate_folder_readmes", self.generate_folder_readmes)
        workflow.add_node("generate_function_docs", self.generate_function_docs)
        workflow.add_node("generate_setup_guide", self.generate_setup_guide)
        
        # Define edges
        workflow.set_entry_point("analyze_repository")
        workflow.add_edge("analyze_repository", "generate_main_readme")
        workflow.add_edge("generate_main_readme", "generate_folder_readmes")
        workflow.add_edge("generate_folder_readmes", "generate_function_docs")
        workflow.add_edge("generate_function_docs", "generate_setup_guide")
        workflow.add_edge("generate_setup_guide", END)
        
        return workflow.compile()
    
    def analyze_repository(self, state: AgentState) -> AgentState:
        """Analyze repository structure and extract metadata."""
        try:
            repo_path = state["repo_path"]
            analysis = self.file_analyzer.analyze_repository(repo_path)
            
            # Detect languages and frameworks
            languages = detect_languages(analysis['code_files'])
            frameworks = detect_frameworks(analysis['code_files'], repo_path)
            
            # Create file tree
            file_tree = create_file_tree(analysis['directories'], analysis['code_files'])
            
            analysis['languages'] = languages
            analysis['frameworks'] = frameworks
            analysis['file_tree'] = file_tree
            
            state["analysis"] = analysis
            state["status"] = "analyzed"
            return state
        except Exception as e:
            state["error"] = f"Analysis failed: {str(e)}"
            state["status"] = "failed"
            return state
    
    def generate_main_readme(self, state: AgentState) -> AgentState:
        """Generate main README.md for the repository."""
        try:
            analysis = state["analysis"]
            
            # Get key files summary
            key_files = self._get_key_files(analysis['code_files'], state["repo_path"])
            
            prompt = MAIN_README_PROMPT.format(
                repo_name=state["repo_name"],
                total_files=analysis['total_files'],
                code_file_count=analysis['code_file_count'],
                languages=", ".join(analysis['languages'].keys()),
                file_structure=analysis['file_tree'],
                key_files_summary=key_files
            )
            
            messages = [
                SystemMessage(content="You are an expert technical writer."),
                HumanMessage(content=prompt)
            ]
            
            response = self.llm.invoke(messages)
            state["main_readme"] = response.content
            state["status"] = "main_readme_generated"
            return state
        except Exception as e:
            state["error"] = f"Main README generation failed: {str(e)}"
            return state
    
    def generate_folder_readmes(self, state: AgentState) -> AgentState:
        """Generate README.md for each major directory."""
        try:
            analysis = state["analysis"]
            folder_readmes = {}
            
            # Group files by directory
            grouped_files = self.file_analyzer.group_files_by_directory(analysis['code_files'])
            
            # Generate README for top-level directories only
            for directory, files in list(grouped_files.items())[:5]:  # Limit to 5 directories
                if directory == '.':
                    continue
                
                # Get code snippets
                code_snippets = self._get_code_snippets(files[:3], state["repo_path"])
                
                prompt = FOLDER_README_PROMPT.format(
                    directory_path=directory,
                    inferred_purpose=self._infer_directory_purpose(directory, files),
                    files_list="\n".join([f"- {f['path']}" for f in files]),
                    code_snippets=code_snippets
                )
                
                messages = [
                    SystemMessage(content="You are an expert technical writer."),
                    HumanMessage(content=prompt)
                ]
                
                response = self.llm.invoke(messages)
                folder_readmes[directory] = response.content
            
            state["folder_readmes"] = folder_readmes
            state["status"] = "folder_readmes_generated"
            return state
        except Exception as e:
            state["error"] = f"Folder README generation failed: {str(e)}"
            return state
    
    def generate_function_docs(self, state: AgentState) -> AgentState:
        """Generate detailed documentation for key files."""
        try:
            analysis = state["analysis"]
            function_docs = {}
            
            # Select key files for detailed documentation
            key_files = self._select_key_files(analysis['code_files'])
            
            for file_info in key_files[:3]:  # Limit to 3 files
                content = self.file_analyzer.get_file_content(file_info['full_path'])
                
                if content.startswith('['):
                    continue  # Skip if error or too large
                
                language = self._get_language_name(file_info['extension'])
                
                prompt = FUNCTION_EXPLANATION_PROMPT.format(
                    file_path=file_info['path'],
                    language=language,
                    code_content=content[:5000]  # Limit content size
                )
                
                messages = [
                    SystemMessage(content="You are an expert code analyst."),
                    HumanMessage(content=prompt)
                ]
                
                response = self.llm.invoke(messages)
                function_docs[file_info['path']] = response.content
            
            state["function_docs"] = function_docs
            state["status"] = "function_docs_generated"
            return state
        except Exception as e:
            state["error"] = f"Function documentation failed: {str(e)}"
            return state
    
    def generate_setup_guide(self, state: AgentState) -> AgentState:
        """Generate how-to-run guide."""
        try:
            analysis = state["analysis"]
            repo_path = state["repo_path"]
            
            # Detect package managers and config files
            config_files = self._detect_config_files(repo_path)
            dependencies = self._extract_dependencies(repo_path)
            
            prompt = SETUP_GUIDE_PROMPT.format(
                languages=", ".join(analysis['languages'].keys()),
                package_managers=", ".join(self._detect_package_managers(repo_path)),
                frameworks=", ".join(analysis['frameworks']),
                database=self._detect_database(repo_path),
                config_files="\n".join([f"- {cf}" for cf in config_files]),
                dependencies=dependencies
            )
            
            messages = [
                SystemMessage(content="You are an expert DevOps engineer."),
                HumanMessage(content=prompt)
            ]
            
            response = self.llm.invoke(messages)
            state["setup_guide"] = response.content
            state["status"] = "completed"
            return state
        except Exception as e:
            state["error"] = f"Setup guide generation failed: {str(e)}"
            return state
    
    def run(self, repo_path: str, repo_name: str) -> AgentState:
        """Run the documentation generation workflow."""
        initial_state: AgentState = {
            "repo_path": repo_path,
            "repo_name": repo_name,
            "analysis": {},
            "main_readme": "",
            "folder_readmes": {},
            "function_docs": {},
            "setup_guide": "",
            "status": "started",
            "error": ""
        }
        
        result = self.workflow.invoke(initial_state)
        return result
    
    # Helper methods
    def _get_key_files(self, code_files: List[Dict], repo_path: str) -> str:
        """Get summary of key files."""
        key_files = []
        for file_info in code_files[:10]:
            key_files.append(f"- {file_info['path']} ({file_info['extension']})")
        return "\n".join(key_files)
    
    def _get_code_snippets(self, files: List[Dict], repo_path: str) -> str:
        """Get code snippets from files."""
        snippets = []
        for file_info in files:
            content = self.file_analyzer.get_file_content(file_info['full_path'])
            if not content.startswith('['):
                snippets.append(f"### {file_info['path']}\n```\n{content[:500]}\n```")
        return "\n\n".join(snippets)
    
    def _infer_directory_purpose(self, directory: str, files: List[Dict]) -> str:
        """Infer the purpose of a directory."""
        dir_name = os.path.basename(directory).lower()
        
        purposes = {
            'src': 'Source code',
            'lib': 'Library code',
            'test': 'Test files',
            'tests': 'Test files',
            'docs': 'Documentation',
            'config': 'Configuration files',
            'utils': 'Utility functions',
            'models': 'Data models',
            'views': 'View components',
            'controllers': 'Controller logic',
            'services': 'Service layer',
            'api': 'API endpoints',
        }
        
        return purposes.get(dir_name, 'Application code')
    
    def _select_key_files(self, code_files: List[Dict]) -> List[Dict]:
        """Select key files for detailed documentation."""
        # Prioritize main files, index files, and larger files
        scored_files = []
        for file_info in code_files:
            score = 0
            basename = os.path.basename(file_info['path']).lower()
            
            if 'main' in basename or 'index' in basename or 'app' in basename:
                score += 10
            score += min(file_info['size'] / 1000, 5)  # Size bonus
            
            scored_files.append((score, file_info))
        
        scored_files.sort(reverse=True, key=lambda x: x[0])
        return [f[1] for f in scored_files]
    
    def _get_language_name(self, extension: str) -> str:
        """Get language name from extension."""
        lang_map = {
            '.py': 'python', '.js': 'javascript', '.ts': 'typescript',
            '.java': 'java', '.go': 'go', '.rs': 'rust', '.rb': 'ruby'
        }
        return lang_map.get(extension, 'text')
    
    def _detect_config_files(self, repo_path: str) -> List[str]:
        """Detect configuration files."""
        config_patterns = [
            'package.json', 'requirements.txt', 'Cargo.toml', 'go.mod',
            'pom.xml', 'build.gradle', '.env.example', 'docker-compose.yml',
            'Dockerfile', 'tsconfig.json', 'webpack.config.js'
        ]
        
        found = []
        for pattern in config_patterns:
            if os.path.exists(os.path.join(repo_path, pattern)):
                found.append(pattern)
        return found
    
    def _extract_dependencies(self, repo_path: str) -> str:
        """Extract dependencies from config files."""
        deps = []
        
        # Python
        req_file = os.path.join(repo_path, 'requirements.txt')
        if os.path.exists(req_file):
            with open(req_file, 'r') as f:
                deps.append("Python: " + ", ".join(f.read().split('\n')[:5]))
        
        # Node.js
        pkg_file = os.path.join(repo_path, 'package.json')
        if os.path.exists(pkg_file):
            import json
            with open(pkg_file, 'r') as f:
                data = json.load(f)
                if 'dependencies' in data:
                    deps.append("Node: " + ", ".join(list(data['dependencies'].keys())[:5]))
        
        return "\n".join(deps) if deps else "No dependencies file found"
    
    def _detect_package_managers(self, repo_path: str) -> List[str]:
        """Detect package managers used."""
        managers = []
        if os.path.exists(os.path.join(repo_path, 'package.json')):
            managers.append('npm/yarn')
        if os.path.exists(os.path.join(repo_path, 'requirements.txt')):
            managers.append('pip')
        if os.path.exists(os.path.join(repo_path, 'Cargo.toml')):
            managers.append('cargo')
        if os.path.exists(os.path.join(repo_path, 'go.mod')):
            managers.append('go modules')
        return managers or ['Unknown']
    
    def _detect_database(self, repo_path: str) -> str:
        """Detect database usage."""
        # Simple heuristic based on file names and imports
        return "Not detected"
