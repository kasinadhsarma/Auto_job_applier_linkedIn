#!/bin/bash

# LinkedIn Auto Job Applier Setup Script

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Setting up LinkedIn Auto Job Applier...${NC}\n"

# Check Python version
python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
if (( $(echo "$python_version 3.8" | awk '{print ($1 < $2)}') )); then
    echo -e "${RED}Error: Python 3.8 or higher is required.${NC}"
    echo "Current version: $python_version"
    exit 1
fi

# Create virtual environment
echo -e "${YELLOW}Creating virtual environment...${NC}"
python3 -m venv venv
if [ $? -ne 0 ]; then
    echo -e "${RED}Failed to create virtual environment.${NC}"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo -e "${RED}Failed to activate virtual environment.${NC}"
    exit 1
fi

# Upgrade pip
echo -e "${YELLOW}Upgrading pip...${NC}"
python -m pip install --upgrade pip

# Install requirements
echo -e "${YELLOW}Installing requirements...${NC}"
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo -e "${RED}Failed to install requirements.${NC}"
    exit 1
fi

# Create configuration files
echo -e "${YELLOW}Setting up configuration files...${NC}"
for config in config/*.example; do
    if [ -f "$config" ]; then
        target="${config%.example}"
        if [ ! -f "$target" ]; then
            cp "$config" "$target"
            echo "Created $target"
        else
            echo "Config file $target already exists, skipping..."
        fi
    fi
done

# Create data directories
echo -e "${YELLOW}Creating data directories...${NC}"
mkdir -p data/{logs/screenshots,resumes,history}
touch data/resumes/.gitkeep data/logs/.gitkeep data/history/.gitkeep

# Set up Git hooks
if [ -d ".git" ]; then
    echo -e "${YELLOW}Setting up Git hooks...${NC}"
    cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
if git diff --cached --name-only | grep -q "config/secrets.py"; then
    echo "Error: Attempted to commit secrets.py file"
    exit 1
fi
EOF
    chmod +x .git/hooks/pre-commit
fi

# Final instructions
echo -e "\n${GREEN}Setup completed successfully!${NC}"
echo -e "\nNext steps:"
echo -e "${YELLOW}1. Copy your resume to data/resumes/${NC}"
echo -e "${YELLOW}2. Update configuration files in config/${NC}"
echo -e "${YELLOW}3. Create config/secrets.py with your LinkedIn credentials${NC}"
echo -e "\nTo activate the virtual environment, run:"
echo -e "${GREEN}source venv/bin/activate${NC}"
echo -e "\nTo start the application, run:"
echo -e "${GREEN}python main.py${NC}"
