#!/usr/bin/env python
"""
Dependency Compatibility Checker for NeuroSim

This script analyzes package dependencies and checks for compatibility issues
before installation. It provides detailed reports about version conflicts
and suggests resolutions.
"""

import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Tuple
import json
import pkg_resources


class DependencyAnalyzer:
    """Analyzes Python package dependencies for compatibility issues."""

    def __init__(self, requirements_file: str = "requirements.txt"):
        self.requirements_file = Path(requirements_file)
        self.installed_packages = self._get_installed_packages()

    def _get_installed_packages(self) -> Dict[str, str]:
        """Get currently installed packages and their versions."""
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "list", "--format=json"],
                capture_output=True,
                text=True,
                check=True
            )
            packages = json.loads(result.stdout)
            return {pkg["name"].lower(): pkg["version"] for pkg in packages}
        except Exception as e:
            print(f"Warning: Could not get installed packages: {e}")
            return {}

    def parse_requirements(self) -> List[Tuple[str, str]]:
        """Parse requirements file and extract package names and version specs."""
        requirements = []
        if not self.requirements_file.exists():
            print(f"Requirements file {self.requirements_file} not found!")
            return requirements

        with open(self.requirements_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    # Simple parsing - split on >= or ==
                    if '>=' in line:
                        name, version = line.split('>=', 1)
                        requirements.append((name.strip(), f">={version.strip()}"))
                    elif '==' in line:
                        name, version = line.split('==', 1)
                        requirements.append((name.strip(), f"=={version.strip()}"))
                    else:
                        requirements.append((line.strip(), ""))
        return requirements

    def check_compatibility(self) -> Dict[str, List[str]]:
        """Check for potential compatibility issues."""
        issues = {"missing": [], "conflicts": [], "warnings": []}
        requirements = self.parse_requirements()

        for package, version_spec in requirements:
            package_lower = package.lower()
            
            # Check if package is installed
            if package_lower not in self.installed_packages:
                issues["missing"].append(f"{package} {version_spec}")
                continue

            # Check version compatibility (basic check)
            installed_version = self.installed_packages[package_lower]
            if version_spec.startswith(">="):
                required_version = version_spec[2:]
                try:
                    if pkg_resources.parse_version(installed_version) < pkg_resources.parse_version(required_version):
                        issues["conflicts"].append(
                            f"{package}: installed {installed_version}, requires {version_spec}"
                        )
                except Exception:
                    issues["warnings"].append(f"Could not compare versions for {package}")

        return issues

    def suggest_installation_order(self) -> List[str]:
        """Suggest optimal installation order based on dependencies."""
        requirements = self.parse_requirements()
        
        # Core packages should be installed first
        core_packages = ["pydantic", "typing-extensions", "packaging"]
        langchain_packages = [pkg for pkg, _ in requirements if "langchain" in pkg.lower()]
        other_packages = [pkg for pkg, _ in requirements if pkg not in core_packages and "langchain" not in pkg.lower()]
        
        installation_order = []
        
        # Add core packages first
        for pkg, version in requirements:
            if pkg in core_packages:
                installation_order.append(f"{pkg}{version}")
        
        # Add LangChain packages in dependency order
        langchain_order = [
            "langchain-core", "langchain-community", "langchain-openai", 
            "langchain-huggingface", "langchain"
        ]
        
        for target in langchain_order:
            for pkg, version in requirements:
                if pkg == target:
                    installation_order.append(f"{pkg}{version}")
                    break
        
        # Add remaining packages
        for pkg, version in requirements:
            full_spec = f"{pkg}{version}"
            if full_spec not in installation_order:
                installation_order.append(full_spec)
        
        return installation_order

    def generate_install_script(self) -> str:
        """Generate a PowerShell script for safe installation."""
        order = self.suggest_installation_order()
        
        script = """# NeuroSim Dependency Installation Script
# This script installs packages in optimal order to avoid conflicts

Write-Host "Installing NeuroSim dependencies..." -ForegroundColor Green

# Function to install package with error handling
function Install-Package {
    param($PackageName)
    Write-Host "Installing $PackageName..." -ForegroundColor Yellow
    try {
        pip install $PackageName
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ Successfully installed $PackageName" -ForegroundColor Green
        } else {
            Write-Host "✗ Failed to install $PackageName" -ForegroundColor Red
            return $false
        }
    } catch {
        Write-Host "✗ Error installing $PackageName: $_" -ForegroundColor Red
        return $false
    }
    return $true
}

# Install packages in dependency order
"""
        
        for package in order:
            script += f'Install-Package "{package}"\n'
        
        script += """
Write-Host "Installation complete!" -ForegroundColor Green
Write-Host "Run 'python -c \"import neurosim; print('Import successful')\"' to test" -ForegroundColor Cyan
"""
        
        return script

    def run_analysis(self):
        """Run complete dependency analysis and provide recommendations."""
        print("🔍 NeuroSim Dependency Compatibility Analysis")
        print("=" * 50)
        
        issues = self.check_compatibility()
        
        if issues["missing"]:
            print("\n❌ Missing Packages:")
            for pkg in issues["missing"]:
                print(f"  - {pkg}")
        
        if issues["conflicts"]:
            print("\n⚠️  Version Conflicts:")
            for conflict in issues["conflicts"]:
                print(f"  - {conflict}")
        
        if issues["warnings"]:
            print("\n⚠️  Warnings:")
            for warning in issues["warnings"]:
                print(f"  - {warning}")
        
        if not any(issues.values()):
            print("\n✅ All dependencies appear compatible!")
        
        print("\n📋 Recommended Installation Order:")
        for i, package in enumerate(self.suggest_installation_order(), 1):
            print(f"  {i:2d}. {package}")
        
        # Generate install script
        script_path = Path("install_dependencies.ps1")
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(self.generate_install_script())
        
        print(f"\n💾 Generated installation script: {script_path}")
        print("   Run with: powershell -ExecutionPolicy Bypass -File install_dependencies.ps1")


if __name__ == "__main__":
    analyzer = DependencyAnalyzer()
    analyzer.run_analysis()
