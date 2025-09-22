# Bridge Slab Design System - README

## Overview
This is a comprehensive Bridge Slab Design application that processes Excel calculation sheets and generates detailed engineering reports. The system integrates all Excel calculation sheets with Claude AI validation for enhanced accuracy and reliability.

## How to Run

### Prerequisites
- Python 3.11 or higher
- Required Python packages (see pyproject.toml)
- Anthropic API key for Claude AI integration (optional but recommended)

### Installation Steps

1. **Clone the repository:**
   ```bash
   git clone https://github.com/CRAJKUMARSINGH/Bridge_Slab_Design2.git
   cd Bridge_Slab_Design2
   ```

2. **Install dependencies:**
   ```bash
   pip install -e .
   ```
   or
   ```bash
   pip install anthropic numpy openpyxl pandas plotly reportlab streamlit
   ```

3. **Set up environment variables (for Claude AI integration):**
   ```bash
   export ANTHROPIC_API_KEY="your-anthropic-api-key"
   ```

### Running the Application

1. **Start the Streamlit application:**
   ```bash
   streamlit run app.py
   ```

2. **Access the application:**
   Open your web browser and go to `http://localhost:8501`

### Application Workflow

1. **Project Setup**: Configure basic bridge parameters (name, location, type, dimensions, etc.)
2. **Excel File Upload**: Upload Excel files containing engineering calculations
3. **Analysis Modules**:
   - Stability Analysis
   - Hydraulic Analysis
   - Abutment Design
   - Cross Section Design
4. **Master Coordination**: Integrate all analysis results
5. **Claude AI Validation**: Validate calculations using Claude AI
6. **Report Generation**: Generate comprehensive PDF reports

## Key Features

- **Excel Integration**: Processes Excel files with original formulas intact
- **Multiple Analysis Modules**: Stability, hydraulic, abutment, and cross-section design
- **AI Validation**: Claude AI validation for enhanced accuracy
- **Report Generation**: Professional PDF reports with detailed calculations
- **Interactive UI**: Streamlit-based web interface for easy interaction

## File Structure

```
Bridge_Slab_Design2/
├── app.py                 # Main application file
├── pyproject.toml         # Project dependencies
├── .streamlit/
│   └── config.toml        # Streamlit configuration
├── modules/               # Core functionality modules
│   ├── excel_processor.py
│   ├── bridge_designer.py
│   ├── hydraulic_analyzer.py
│   ├── stability_analyzer.py
│   ├── abutment_designer.py
│   ├── cross_section_designer.py
│   ├── claude_integration.py
│   ├── pdf_generator.py
│   └── master_coordinator.py
├── utils/
│   ├── data_structures.py
│   └── formula_extractor.py
└── static/                # Static assets
    └── styles.css
```

## Git Repository Management

### Configuration
```bash
git config user.email "crajkumarsingh@hotmail.com"
git config user.name "RAJKUMAR SINGH CHAUHAN"
```

### Basic Git Commands
```bash
# Add all changes
git add .

# Commit changes
git commit -m "Your descriptive commit message"

# Push to remote repository
git push origin main
```

## Deployment

### Streamlit Cloud Deployment
1. Push your code to GitHub
2. Connect your repository to Streamlit Cloud
3. Configure environment variables if needed
4. Deploy the application

### Local Deployment
The application can be run locally using the Streamlit command mentioned above.

## Testing

Run individual module tests:
```bash
python -m pytest tests/
```

## Troubleshooting

1. **Missing dependencies**: Ensure all packages in pyproject.toml are installed
2. **Claude AI integration**: Verify ANTHROPIC_API_KEY is set correctly
3. **Excel processing issues**: Check that Excel files are in .xls or .xlsx format
4. **Port conflicts**: Change the port in .streamlit/config.toml if 8501 is in use

## Contact
For issues or questions, contact Rajkumar Singh Chauhan at crajkumarsingh@hotmail.com