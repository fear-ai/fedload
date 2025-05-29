# Python Virtual Environment Guide

## Virtual Environment Setup

### Creating a Virtual Environment

1. **Using venv (Recommended)**
```bash
# Create virtual environment in project directory
python -m venv .venv

# Or create in a separate directory
python -m venv venv
```

2. **Using virtualenv**
```bash
# Install virtualenv if needed
pip install virtualenv

# Create virtual environment
virtualenv .venv
```

### Activating the Virtual Environment

#### Windows PowerShell
```powershell
# Using .venv
.\.venv\Scripts\Activate.ps1

# Using venv
.\venv\Scripts\Activate.ps1
```

#### Command Prompt
```cmd
# Using .venv
.venv\Scripts\activate.bat

# Using venv
venv\Scripts\activate.bat
```

### Deactivating the Virtual Environment
```bash
# Deactivate from any shell
deactivate
```

## Environment Structure

### .venv Directory Structure
```
.venv/
├── bin/                 # Linux/MacOS executables
├── Scripts/             # Windows executables
├── include/             # Python headers
├── lib/                 # Python libraries
├── pyvenv.cfg           # Configuration file
└── pip-selfcheck.json   # Pip self-check cache
```

### venv Directory Structure (same as .venv)
```
venv/
├── bin/                 # Linux/MacOS executables
├── Scripts/             # Windows executables
├── include/             # Python headers
├── lib/                 # Python libraries
├── pyvenv.cfg           # Configuration file
└── pip-selfcheck.json   # Pip self-check cache
```

## Best Practices

1. **Directory Naming**
   - Use `.venv` for project-specific environments
   - Use `venv` for shared environments
   - `.venv` is hidden on Unix systems, making it less intrusive

2. **Version Control**
   ```gitignore
   # Ignore virtual environment directories
   .venv/
   venv/
   
   # Keep configuration files
   !.venv/pyvenv.cfg
   !venv/pyvenv.cfg
   ```

3. **Environment Configuration**
   ```bash
   # Create environment configuration
   # .venv/pyvenv.cfg
   home = C:\Python39
   include-system-site-packages = false
   version = 3.9.5
   ```

## Managing Dependencies

1. **Requirements Files**
   ```bash
   # Create requirements.txt
   pip freeze > requirements.txt
   
   # Create development requirements
   pip freeze > requirements-dev.txt
   ```

2. **Installing Dependencies**
   ```bash
   # Install from requirements
   pip install -r requirements.txt
   
   # Install development dependencies
   pip install -r requirements-dev.txt
   ```

## Advanced Configuration

### Environment Variables
```bash
# Create .env file
PYTHONPATH=${workspaceFolder}
PATH=${workspaceFolder}/.venv/Scripts:${env:PATH}
VIRTUAL_ENV=${workspaceFolder}/.venv
```

### Custom Scripts
```bash
# Create custom activation script
# activate_custom.ps1
function global:Activate-Custom {
    param(
        [string]$envPath = "${PSScriptRoot}/.venv"
    )
    
    # Set environment variables
    $env:VIRTUAL_ENV = $envPath
    $env:PYTHONPATH = $PSScriptRoot
    $env:PATH = Join-Path $envPath "Scripts" + ";" + $env:PATH
    
    # Update prompt
    function global:prompt {
        "($env:VIRTUAL_ENV) $(Get-Location)" + "> "
    }
}
```

### Version Management
```bash
# Create pyproject.toml for version management
[tool.uv]
python = "3.9"
venv = ".venv"

[tool.uv.dependencies]
black = "^22.12.0"
isort = "^5.12.0"
flake8 = "^6.0.0"
```

## Troubleshooting

1. **Common Issues**
   - **Activation Fails**
     - **Cause**: PowerShell execution policy is too restrictive
     - **Solution**: Run PowerShell as administrator and execute:
       ```powershell
       Set-ExecutionPolicy RemoteSigned
       ```
   - **Missing Scripts**
     - **Cause**: Virtual environment creation failed or Python installation is incomplete
     - **Solution**: Verify Python installation and reinstall virtual environment:
       ```powershell
       python -m venv --clear .venv
       .\.venv\Scripts\Activate.ps1
       ```
   - **Permission Errors**
     - **Cause**: Insufficient permissions to create or modify files
     - **Solution**: Run terminal as administrator or modify permissions:
       ```powershell
       icacls .venv /grant:r "${env:USERNAME}":(OI)(CI)F
       ```
   - **Python Version Mismatch**
     - **Cause**: Virtual environment created with different Python version
     - **Solution**: Delete old environment and recreate with correct Python version:
       ```powershell
       Remove-Item -Recurse -Force .venv
       python -m venv .venv --python="C:\Python39\python.exe"
       ```
   - **Package Installation Fails**
     - **Cause**: Network issues or package not found
     - **Solution**: Use specific package index or install from source:
       ```powershell
       pip install --index-url https://pypi.org/simple package_name
       pip install --no-index --find-links="path/to/local/packages" package_name
       ```

2. **Common Commands**
   ```powershell
   # List installed packages
   pip list
   
   # Upgrade pip
   python -m pip install --upgrade pip
   
   # Freeze requirements
   pip freeze > requirements.txt
   
   # Install from requirements
   pip install -r requirements.txt
   
   # Remove package
   pip uninstall package_name
   
   # Show package details
   pip show package_name
   ```

3. **Best Practices**
   - Always activate virtual environment before running Python commands
   - Keep requirements.txt up to date
   - Use separate requirements files for development and production
   - Regularly update packages to their latest compatible versions
   - Document Python version and package versions in project documentation

## Integration with IDEs

### Windsurf
```json
// .windsurf/settings.json
{
    "python": {
        "venvPath": "${workspaceFolder}/.venv",
        "venvActivate": "${workspaceFolder}/.venv/Scripts/Activate.ps1",
        "venvCreate": true,
        "venvPythonPath": "${workspaceFolder}/.venv/Scripts/python.exe",
        "venvPipPath": "${workspaceFolder}/.venv/Scripts/pip.exe"
    },
    "terminal": {
        "env": {
            "PYTHONPATH": "${workspaceFolder}",
            "PATH": "${workspaceFolder}/.venv/Scripts:${env:PATH}",
            "VIRTUAL_ENV": "${workspaceFolder}/.venv",
            "VIRTUAL_ENV_DISABLE_PROMPT": "false"
        }
    },
    "debug": {
        "python": {
            "pathMappings": [
                {
                    "localRoot": "${workspaceFolder}",
                    "remoteRoot": "/app"
                }
            ]
        }
    }
}
```

### VSCode
```json
// .vscode/settings.json
{
    "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python",
    "terminal.integrated.env.windows": {
        "PYTHONPATH": "${workspaceFolder}",
        "PATH": "${workspaceFolder}/.venv/Scripts;${env:PATH}"
    }
}
```

## Best Practices for Team Development

1. **Documentation**
   - Document virtual environment setup in README
   - Include required Python version
   - List necessary dependencies

2. **Consistency**
   - Use consistent naming conventions
   - Standardize Python version
   - Maintain centralized requirements files

3. **Automation**
   ```powershell
   # Create setup-project.ps1
   param(
       [Parameter(Mandatory=$false)]
       [string]$venvName = ".venv",
       [Parameter(Mandatory=$false)]
       [string]$requirements = "requirements.txt",
       [Parameter(Mandatory=$false)]
       [string]$devRequirements = "requirements-dev.txt"
   )
   
   # Check if virtual environment exists
   if (Test-Path $venvName) {
       Write-Host "Virtual environment already exists. Skipping creation."
   } else {
       Write-Host "Creating virtual environment: $venvName"
       python -m venv $venvName
   }
   
   # Activate virtual environment
   Write-Host "Activating virtual environment..."
   & "$venvName\Scripts\Activate.ps1"
   
   # Install dependencies
   if (Test-Path $requirements) {
       Write-Host "Installing production dependencies..."
       pip install -r $requirements
   }
   
   if (Test-Path $devRequirements) {
       Write-Host "Installing development dependencies..."
       pip install -r $devRequirements
   }
   
   Write-Host "Setup complete! Virtual environment is activated."
   ```

This guide provides a comprehensive overview of Python virtual environment setup and usage, covering both `.venv` and `venv` directory structures, along with best practices for development and team collaboration.
