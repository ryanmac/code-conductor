"""Basic tests for code-conductor"""

import sys
import yaml
import requests


def test_python_version():
    """Test that we're running Python 3.9-3.12"""
    assert sys.version_info >= (3, 9), f"Python 3.9-3.12 required, got {sys.version}"
    assert sys.version_info < (3, 13), f"Python 3.13+ not yet supported, got {sys.version}"


def test_dependencies():
    """Test that core dependencies are available"""
    # Test PyYAML
    assert hasattr(yaml, '__version__'), "PyYAML not available"
    print(f"PyYAML version: {yaml.__version__}")

    # Test Requests
    assert hasattr(requests, '__version__'), "Requests not available"
    print(f"Requests version: {requests.__version__}")


def test_yaml_functionality():
    """Test basic YAML functionality"""
    test_data = {
        'name': 'test',
        'version': '1.0.0',
        'dependencies': ['pyyaml', 'requests']
    }

    # Test YAML serialization
    yaml_str = yaml.dump(test_data)
    assert isinstance(yaml_str, str)

    # Test YAML deserialization
    loaded_data = yaml.safe_load(yaml_str)
    assert loaded_data == test_data


def test_requests_functionality():
    """Test basic Requests functionality"""
    # Test that requests can be imported and has expected attributes
    assert hasattr(requests, 'get')
    assert hasattr(requests, 'post')
    assert hasattr(requests, 'Session')


if __name__ == "__main__":
    # Run tests
    test_python_version()
    test_dependencies()
    test_yaml_functionality()
    test_requests_functionality()
    print("✅ All basic tests passed!")
