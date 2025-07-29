# NeuroSim Dependency Management Guide

## 🎯 Overview

This guide covers the dependency management tools created for NeuroSim to analyze package compatibility and prevent installation conflicts.

## 🔧 Tools Available

### 1. **Dependency Compatibility Analyzer** (`check_dependencies.py`)

A comprehensive tool that analyzes your Python packages for compatibility issues:

**Features:**
- ✅ Identifies missing packages
- ⚠️ Detects version conflicts
- 📋 Suggests optimal installation order
- 💾 Generates PowerShell installation scripts
- 🔍 Provides detailed compatibility reports

**Usage:**
```bash
python check_dependencies.py
```

### 2. **Requirements Files**

Two requirements files for different purposes:

#### `requirements.txt` - Lock file with specific versions
```
gradio>=3.44.0
langchain>=0.1.0
langchain-community>=0.0.38
# ... etc
```

#### `requirements.in` - High-level dependencies
```
# Core requirements for NeuroSim
gradio>=3.44.0
langchain>=0.1.0
# ... etc
```

### 3. **Auto-generated Installation Script** (`install_dependencies.ps1`)

PowerShell script that installs packages in optimal order with error handling.

## 🚀 Quick Start

### Step 1: Check Compatibility
```bash
cd c:\Neurosim
python check_dependencies.py
```

### Step 2: Install Missing Packages
If the analyzer finds missing packages, run:
```bash
pip install langchain-huggingface sentence-transformers vaderSentiment
```

Or use the generated PowerShell script:
```powershell
powershell -ExecutionPolicy Bypass -File install_dependencies.ps1
```

### Step 3: Verify Installation
```bash
python -c "from neurosim.core.agent_manager import AgentManager; print('✓ Success')"
```

## 📊 Dependency Analysis Results

Current status: **✅ All dependencies compatible!**

### Critical Dependencies Fixed:
1. **LangChain Imports**: Updated to use newer modular structure
   - `langchain-community` for embeddings and vector stores
   - `langchain-openai` for ChatOpenAI
   - `langchain-huggingface` for HuggingFace embeddings

2. **Embedding System**: Fixed HuggingFaceEmbeddings import
3. **Sentiment Analysis**: Added vaderSentiment package
4. **Development Tools**: Added pip-tools for better dependency management

## 🔄 Recommended Installation Order

The analyzer suggests this order to prevent conflicts:

1. Core packages (`pydantic`, `typing-extensions`)
2. LangChain ecosystem (in dependency order)
3. ML/AI packages (`sentence-transformers`, `torch`)
4. UI and visualization (`gradio`, `matplotlib`)
5. Optional tools (`pip-tools`)

## 🛠️ Advanced Usage

### Using pip-tools for Lock Files

Generate exact versions:
```bash
pip-compile requirements.in
```

Sync environment:
```bash
pip-sync requirements.txt
```

### Custom Compatibility Checks

The analyzer can be extended to check for:
- Python version compatibility
- OS-specific dependencies  
- Security vulnerabilities
- License compatibility

## 🐛 Troubleshooting

### Common Issues:

1. **Import Errors**: Usually resolved by following installation order
2. **Version Conflicts**: Use `pip install --upgrade` for specific packages
3. **Environment Issues**: Consider using virtual environments

### Debug Commands:
```bash
# Check installed packages
pip list

# Show package info
pip show langchain-huggingface

# Check for conflicts
pip check
```

## 📝 Best Practices

1. **Always check compatibility** before installing new packages
2. **Use virtual environments** to isolate dependencies
3. **Pin versions** in production environments
4. **Run the analyzer** after any dependency changes
5. **Keep requirements files** updated and synchronized

## 🔗 Integration with NeuroSim

The dependency management is integrated with NeuroSim's architecture:

- **AgentManager**: Automatically handles missing dependencies gracefully
- **Optional imports**: Uses try/except blocks for optional packages
- **Configuration**: Environment variables control which packages to use
- **Fallbacks**: Graceful degradation when packages are missing

This ensures NeuroSim can run with minimal dependencies while providing full functionality when all packages are available.
