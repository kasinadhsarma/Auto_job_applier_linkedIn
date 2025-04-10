# LinkedIn Auto Job Applier

A modular and configurable automation tool for applying to jobs on LinkedIn.

## Project Structure

```
Auto_job_applier_linkedIn/
├── app/                      # Main application package
│   ├── core/                # Core application logic
│   │   ├── __init__.py     # Application initialization
│   │   ├── config.py       # Configuration management
│   │   ├── application.py  # Job application logic
│   │   ├── browser.py      # Browser interactions
│   │   ├── filters.py      # Job search filters
│   │   └── scheduler.py    # Application scheduling
│   │
│   ├── modules/            # Functional modules
│   │   ├── ai/            # AI integrations
│   │   ├── jobs/          # Job processing
│   │   ├── platform/      # Platform handlers
│   │   └── utils/         # Utility functions
│   │
│   └── services/          # Supporting services
│       ├── resume/        # Resume management
│       └── tracking/      # Metrics tracking
│
├── config/                # Configuration files
│   ├── settings.py       # Main settings
│   ├── secrets.py        # Credentials (gitignored)
│   ├── search.py         # Search parameters
│   └── personals.py      # Personal information
│
├── data/                 # Application data
│   ├── logs/            # Application logs
│   ├── resumes/         # Resume storage
│   └── history/         # Application history
│
└── main.py              # Entry point
```

## Setup

1. Clone the repository:
```bash
git clone https://github.com/username/Auto_job_applier_linkedIn.git
cd Auto_job_applier_linkedIn
```

2. Create a virtual environment and install dependencies:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Configure the application:
   - Copy example configuration files:
     ```bash
     cp config/settings.py.example config/settings.py
     cp config/search.py.example config/search.py
     cp config/personals.py.example config/personals.py
     ```
   - Create `config/secrets.py` with your LinkedIn credentials:
     ```python
     username = "your_email@example.com"
     password = "your_password"
     ```
   - Update configuration files with your preferences

4. Place your resume in the data/resumes directory:
```bash
mkdir -p data/resumes
cp your_resume.pdf data/resumes/
```

5. Update the resume path in config/settings.py:
```python
default_resume_path = "data/resumes/your_resume.pdf"
```

## Usage

Run the application:
```bash
python main.py
```

The application will:
1. Load your configuration
2. Log in to LinkedIn
3. Search for jobs based on your criteria
4. Apply to jobs that match your filters
5. Track application history and metrics

## Configuration

### Settings (settings.py)
- Browser behavior
- Application preferences
- File paths and directories

### Search Parameters (search.py)
- Search terms
- Location preferences
- Experience levels
- Job types
- Other search filters

### Personal Information (personals.py)
- Contact details
- Experience
- Education
- Skills
- Other application details

## Features

- **Automated Login**: Securely log in to LinkedIn
- **Smart Job Search**: Configurable search criteria and filters
- **Easy Apply**: Automatic application for compatible jobs
- **Application Tracking**: Track application history and success rates
- **Resume Management**: Support for multiple resumes
- **Error Handling**: Robust error handling and recovery
- **Metrics**: Detailed application statistics and reporting

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This tool is for educational purposes only. Use at your own risk and responsibility. Make sure to review LinkedIn's terms of service and use the tool accordingly.
