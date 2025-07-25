"""Tests for enhanced stack detection logic"""

import json
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch
import pytest

# Import the setup module
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from setup import ConductorSetup


class TestStackDetection:
    """Test the enhanced stack detection functionality"""
    
    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.project_root = Path(self.temp_dir)
        
    def teardown_method(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir)
    
    def test_detect_react_nextjs(self):
        """Test detection of React/Next.js projects"""
        # Create package.json with React dependencies
        package_json = {
            "name": "test-app",
            "dependencies": {
                "react": "^18.0.0",
                "react-dom": "^18.0.0",
                "next": "^14.0.0"
            }
        }
        (self.project_root / "package.json").write_text(json.dumps(package_json))
        
        # Run detection
        with patch('pathlib.Path.cwd', return_value=self.project_root):
            setup = ConductorSetup(auto_mode=True)
            setup._detect_project_info()
        
        # Verify detection
        assert len(setup.detected_stack) > 0
        stack = setup.detected_stack[0]
        assert stack["tech"] == "nodejs"
        assert "detected_subtypes" in stack
        assert "react" in stack["detected_subtypes"]
        assert "nextjs" in stack["detected_subtypes"]
        assert "frontend" in stack["suggested_roles"]
    
    def test_detect_python_django(self):
        """Test detection of Python Django projects"""
        # Create requirements.txt with Django
        requirements = """
django==4.2.0
djangorestframework==3.14.0
celery==5.3.0
redis==5.0.0
        """
        (self.project_root / "requirements.txt").write_text(requirements.strip())
        
        # Run detection
        with patch('pathlib.Path.cwd', return_value=self.project_root):
            setup = ConductorSetup(auto_mode=True)
            setup._detect_project_info()
        
        # Verify detection
        assert len(setup.detected_stack) > 0
        stack = setup.detected_stack[0]
        assert stack["tech"] == "python"
        assert "detected_subtypes" in stack
        assert "django" in stack["detected_subtypes"]
        assert "devops" in stack["suggested_roles"]
        assert "security" in stack["suggested_roles"]
    
    def test_detect_python_ml(self):
        """Test detection of Python ML projects"""
        # Create requirements.txt with ML libraries
        requirements = """
tensorflow==2.13.0
pandas==2.0.0
numpy==1.24.0
scikit-learn==1.3.0
jupyter==1.0.0
        """
        (self.project_root / "requirements.txt").write_text(requirements.strip())
        
        # Run detection
        with patch('pathlib.Path.cwd', return_value=self.project_root):
            setup = ConductorSetup(auto_mode=True)
            setup._detect_project_info()
        
        # Verify detection
        assert len(setup.detected_stack) > 0
        stack = setup.detected_stack[0]
        assert stack["tech"] == "python"
        assert "detected_subtypes" in stack
        assert "ml" in stack["detected_subtypes"]
        assert "data" in stack["detected_subtypes"]
        assert "ml-engineer" in stack["suggested_roles"]
        assert "data" in stack["suggested_roles"]
    
    def test_detect_go_microservices(self):
        """Test detection of Go microservices"""
        # Create go.mod with common frameworks
        go_mod = """
module example.com/myapp

go 1.21

require (
    github.com/gin-gonic/gin v1.9.1
    github.com/spf13/viper v1.16.0
)
        """
        (self.project_root / "go.mod").write_text(go_mod.strip())
        
        # Run detection
        with patch('pathlib.Path.cwd', return_value=self.project_root):
            setup = ConductorSetup(auto_mode=True)
            setup._detect_project_info()
        
        # Verify detection
        assert len(setup.detected_stack) > 0
        stack = setup.detected_stack[0]
        assert stack["tech"] == "go"
        assert "detected_subtypes" in stack
        assert "gin" in stack["detected_subtypes"]
        assert "devops" in stack["suggested_roles"]
        assert "security" in stack["suggested_roles"]
    
    def test_detect_mobile_flutter(self):
        """Test detection of Flutter mobile projects"""
        # Create pubspec.yaml
        pubspec = """
name: my_app
description: A Flutter application

dependencies:
  flutter:
    sdk: flutter
  cupertino_icons: ^1.0.2
        """
        (self.project_root / "pubspec.yaml").write_text(pubspec.strip())
        
        # Run detection
        with patch('pathlib.Path.cwd', return_value=self.project_root):
            setup = ConductorSetup(auto_mode=True)
            setup._detect_project_info()
        
        # Verify detection
        assert len(setup.detected_stack) > 0
        stack = setup.detected_stack[0]
        assert stack["tech"] == "flutter"
        assert "mobile" in stack["suggested_roles"]
        assert "frontend" in stack["suggested_roles"]
    
    def test_detect_dotnet_aspnet(self):
        """Test detection of .NET ASP.NET projects"""
        # Create a .csproj file
        csproj = """
<Project Sdk="Microsoft.NET.Sdk.Web">
  <PropertyGroup>
    <TargetFramework>net7.0</TargetFramework>
  </PropertyGroup>
  <ItemGroup>
    <PackageReference Include="Microsoft.AspNetCore.Mvc" Version="2.2.0" />
    <PackageReference Include="Microsoft.AspNetCore.Components" Version="7.0.0" />
  </ItemGroup>
</Project>
        """
        (self.project_root / "MyApp.csproj").write_text(csproj.strip())
        
        # Run detection
        with patch('pathlib.Path.cwd', return_value=self.project_root):
            setup = ConductorSetup(auto_mode=True)
            setup._detect_project_info()
        
        # Verify detection
        assert len(setup.detected_stack) > 0
        stack = setup.detected_stack[0]
        assert stack["tech"] == "dotnet"
        assert "detected_subtypes" in stack
        assert "aspnet" in stack["detected_subtypes"]
        assert "blazor" in stack["detected_subtypes"]
        assert "devops" in stack["suggested_roles"]
        assert "frontend" in stack["suggested_roles"]
    
    def test_multiple_stack_detection(self):
        """Test detection of projects with multiple technologies"""
        # Create both package.json and requirements.txt
        package_json = {
            "name": "fullstack-app",
            "dependencies": {
                "react": "^18.0.0",
                "express": "^4.18.0"
            }
        }
        (self.project_root / "package.json").write_text(json.dumps(package_json))
        
        requirements = "fastapi==0.100.0\nuvicorn==0.23.0"
        (self.project_root / "requirements.txt").write_text(requirements)
        
        # Run detection
        with patch('pathlib.Path.cwd', return_value=self.project_root):
            setup = ConductorSetup(auto_mode=True)
            setup._detect_project_info()
        
        # Verify multiple stacks detected
        assert len(setup.detected_stack) >= 2
        tech_stacks = [stack["tech"] for stack in setup.detected_stack]
        assert "nodejs" in tech_stacks
        assert "python" in tech_stacks


class TestAutoConfiguration:
    """Test the auto-configuration logic"""
    
    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.project_root = Path(self.temp_dir)
        
    def teardown_method(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir)
    
    def test_code_reviewer_always_included(self):
        """Test that code-reviewer role is always included"""
        # Create a simple project
        (self.project_root / "README.md").write_text("# Test Project")
        
        # Run auto-configuration
        with patch('pathlib.Path.cwd', return_value=self.project_root):
            setup = ConductorSetup(auto_mode=True)
            # Run the full setup process which includes auto configuration
            setup._detect_project_info()
            setup._gather_configuration()
        
        # Verify code-reviewer is included
        specialized_roles = setup.config["roles"]["specialized"]
        assert "code-reviewer" in specialized_roles
    
    def test_devops_role_for_docker(self):
        """Test that devops role is added when Docker files exist"""
        # Create Dockerfile
        (self.project_root / "Dockerfile").write_text("FROM node:18")
        (self.project_root / "docker-compose.yml").write_text("version: '3'")
        
        # Run auto-configuration
        with patch('pathlib.Path.cwd', return_value=self.project_root):
            setup = ConductorSetup(auto_mode=True)
            # Run the full setup process which includes auto configuration
            setup._detect_project_info()
            setup._gather_configuration()
        
        # Verify devops role is included
        specialized_roles = setup.config["roles"]["specialized"]
        assert "devops" in specialized_roles
    
    def test_github_issues_preference(self):
        """Test that GitHub Issues is preferred when .github exists"""
        # Create .github directory
        (self.project_root / ".github").mkdir()
        
        # Run auto-configuration
        with patch('pathlib.Path.cwd', return_value=self.project_root):
            setup = ConductorSetup(auto_mode=True)
            # Run the full setup process which includes auto configuration
            setup._detect_project_info()
            setup._gather_configuration()
        
        # Verify GitHub Issues is selected
        assert setup.config["task_management"] == "github-issues"


def test_role_template_creation():
    """Test that all role templates are created correctly"""
    with tempfile.TemporaryDirectory() as temp_dir:
        project_root = Path(temp_dir)
        
        # Set up config with all possible roles
        with patch('pathlib.Path.cwd', return_value=project_root):
            setup = ConductorSetup(auto_mode=True)
            setup.conductor_dir = project_root / ".conductor"
            setup.conductor_dir.mkdir()
            
            setup.config = {
                "roles": {
                    "default": "dev",
                    "specialized": [
                        "code-reviewer", "frontend", "mobile", 
                        "devops", "security", "ml-engineer", 
                        "ui-designer", "data"
                    ]
                }
            }
            
            # Create role definitions
            setup._create_role_definitions()
            
            # Verify all role files exist
            roles_dir = setup.conductor_dir / "roles"
            assert (roles_dir / "dev.md").exists()
            
            for role in setup.config["roles"]["specialized"]:
                role_file = roles_dir / f"{role}.md"
                assert role_file.exists(), f"Role file {role}.md not created"
                
                # Verify content is not empty
                content = role_file.read_text()
                assert len(content) > 100, f"Role {role} has insufficient content"
                assert "## Overview" in content
                assert "## Responsibilities" in content


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])