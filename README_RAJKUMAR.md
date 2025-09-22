# Bridge Slab Design System - README

## Overview
This is a comprehensive Bridge Slab Design application that processes Excel calculation sheets and generates detailed engineering reports. The system integrates all Excel calculation sheets with Claude AI validation for enhanced accuracy and reliability.

The application now includes an organized output folder system that stores files in date-based subfolders with bridge type and serial numbering.

## How to Run

### Prerequisites
- Python 3.11 or higher
- Required Python packages (see pyproject.toml or requirements.txt)
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
   pip install -r requirements.txt
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
- **Organized Output Storage**: Files saved in date-based subfolders with bridge type and serial numbers

## Output Folder System

The application now automatically organizes generated reports in a structured folder system:

```
outputs/
├── 2025-09-23/
│   ├── Submersible_Bridge/
│   │   ├── 2025-09-23_Submersible_Bridge_001_143022.pdf
│   │   └── 2025-09-23_Submersible_Bridge_002_143545.pdf
│   └── High_Level_Bridge/
│       └── 2025-09-23_High_Level_Bridge_001_144012.pdf
└── 2025-09-24/
    └── Aqueduct/
        └── 2025-09-24_Aqueduct_001_101530.pdf
```

Each generated report is automatically saved to:
- A date-based folder (YYYY-MM-DD)
- A bridge type subfolder
- A filename that includes:
  - Date (YYYY-MM-DD)
  - Bridge type
  - Serial number (001, 002, etc.)
  - Timestamp (HHMMSS)
  - File extension

This organization makes it easy to locate specific reports and prevents filename conflicts when multiple reports are generated on the same date.

## File Structure

```
Bridge_Slab_Design2/
├── app.py                 # Main application file
├── requirements.txt       # Python dependencies for deployment
├── pyproject.toml         # Project dependencies
├── Procfile               # Deployment configuration for Streamlit Cloud
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
├── utils/                 # Utility modules
│   ├── data_structures.py
│   ├── formula_extractor.py
│   └── output_manager.py  # New output folder system
├── outputs/               # Generated reports (automatically created)
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

### Streamlit Cloud Deployment (Recommended)
1. **Push your code to GitHub:**
   ```bash
   git add .
   git commit -m "Prepare for Streamlit Cloud deployment"
   git push origin main
   ```

2. **Connect to Streamlit Cloud:**
   - Go to [Streamlit Cloud](https://streamlit.io/cloud)
   - Sign in with your GitHub account
   - Click "New app"
   - Select your repository (CRAJKUMARSINGH/Bridge_Slab_Design2)
   - Set the main file path to `app.py`
   - Click "Deploy!"

3. **Configure environment variables (if using Claude AI):**
   - In the Streamlit Cloud app settings, add the environment variable:
     - Key: `ANTHROPIC_API_KEY`
     - Value: Your Anthropic API key

4. **Advanced configuration:**
   - The app will automatically use the `Procfile` for deployment
   - The app will automatically install dependencies from `requirements.txt`
   - Custom Streamlit settings are in `.streamlit/config.toml`

### Local Deployment
The application can be run locally using the Streamlit command mentioned above.

## Testing

Run individual module tests:
```bash
python -m pytest tests/
```

Test the output manager:
```bash
python test_output_manager.py
```

## Troubleshooting

1. **Missing dependencies**: Ensure all packages in pyproject.toml are installed
2. **Claude AI integration**: Verify ANTHROPIC_API_KEY is set correctly
3. **Excel processing issues**: Check that Excel files are in .xls or .xlsx format
4. **Port conflicts**: Change the port in .streamlit/config.toml if 8501 is in use

## Contact
For issues or questions, contact Rajkumar Singh Chauhan at crajkumarsingh@hotmail.com