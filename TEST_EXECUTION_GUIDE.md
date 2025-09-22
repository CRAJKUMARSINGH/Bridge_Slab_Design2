# Bridge Slab Design System - Test Execution Guide

## Overview
This guide provides instructions for executing the comprehensive test plan for the Bridge Slab Design application with 5 different input combinations.

## Prerequisites
1. Python 3.11 or higher installed
2. All required dependencies installed (`pip install -e .` or `pip install anthropic numpy openpyxl pandas plotly reportlab streamlit`)
3. Application running (`streamlit run app.py`)

## Test Scenarios Summary

### Test 1: Standard Submersible Bridge
- **Bridge Name**: "Main Street Submersible Bridge"
- **Location**: "Downtown Area"
- **Bridge Type**: "Submersible Bridge"
- **Effective Span**: 12.0 m
- **Bridge Width**: 8.5 m
- **Number of Spans**: 3
- **Skew Angle**: 0.0 degrees
- **Design Code**: "IRC-6"
- **Concrete Grade**: "M30"
- **Steel Grade**: "Fe500"
- **Design Life**: 100 years

### Test 2: High-Level Bridge with Skew
- **Bridge Name**: "River Crossing High-Level Bridge"
- **Location**: "Northern Highway"
- **Bridge Type**: "High Level Bridge"
- **Effective Span**: 25.0 m
- **Bridge Width**: 12.0 m
- **Number of Spans**: 5
- **Skew Angle**: 30.0 degrees
- **Design Code**: "IRC-21"
- **Concrete Grade**: "M35"
- **Steel Grade**: "Fe500"
- **Design Life**: 120 years

### Test 3: Narrow Culvert Bridge
- **Bridge Name**: "Forest Road Culvert"
- **Location**: "Mountain Region"
- **Bridge Type**: "Culvert"
- **Effective Span**: 6.0 m
- **Bridge Width**: 4.0 m
- **Number of Spans**: 1
- **Skew Angle**: 15.0 degrees
- **Design Code**: "IRC-112"
- **Concrete Grade**: "M25"
- **Steel Grade**: "Fe415"
- **Design Life**: 75 years

### Test 4: Wide Aqueduct Bridge
- **Bridge Name**: "Irrigation Aqueduct Bridge"
- **Location**: "Agricultural Zone"
- **Bridge Type**: "Aqueduct"
- **Effective Span**: 15.0 m
- **Bridge Width**: 18.0 m
- **Number of Spans**: 4
- **Skew Angle**: 5.0 degrees
- **Design Code**: "IS-456"
- **Concrete Grade**: "M40"
- **Steel Grade**: "Fe550"
- **Design Life**: 100 years

### Test 5: Short Urban Pedestrian Bridge
- **Bridge Name**: "City Park Pedestrian Bridge"
- **Location**: "Urban Park"
- **Bridge Type**: "Submersible Bridge"
- **Effective Span**: 8.0 m
- **Bridge Width**: 3.5 m
- **Number of Spans**: 1
- **Skew Angle**: 0.0 degrees
- **Design Code**: "IRC-6"
- **Concrete Grade**: "M30"
- **Steel Grade**: "Fe415"
- **Design Life**: 50 years

## Test Execution Steps

### 1. Start the Application
```bash
streamlit run app.py
```

### 2. Open Browser
Navigate to `http://localhost:8501` in your web browser.

### 3. Execute Each Test

#### For Each Test Scenario:
1. **Project Setup**
   - Enter all parameters as specified for the test scenario
   - Click "Create Project Configuration"

2. **Excel File Upload**
   - For each analysis module, upload the corresponding Excel file:
     - Stability Analysis
     - Hydraulic Analysis
     - Live Load Analysis
     - Cross Section Design
     - Abutment Design
   - Process each file after upload

3. **Run Analysis Modules**
   - Navigate to each analysis module page
   - Run the analysis for that module
   - Verify results are displayed correctly

4. **Claude AI Validation** (Optional)
   - If you have an Anthropic API key, navigate to "Claude AI Validation"
   - Run validation for each analysis result
   - Review AI feedback

5. **Generate Reports**
   - Navigate to "Generate Reports"
   - Configure report settings:
     - Select "Comprehensive Report"
     - Include all sections
     - Try all output formats (PDF, HTML, Word Document)
   - Generate report
   - Download each format
   - Verify files are saved to organized output folders

6. **Verify Output Organization**
   - Check that files are saved in the correct folder structure:
     ```
     outputs/
     ├── YYYY-MM-DD/
     │   ├── Bridge_Type/
     │   │   ├── YYYY-MM-DD_Bridge_Type_001_HHMMSS.pdf
     │   │   ├── YYYY-MM-DD_Bridge_Type_002_HHMMSS.html
     │   │   └── YYYY-MM-DD_Bridge_Type_003_HHMMSS.docx
     ```

### 4. Document Results
For each test, record:
- Date and time of execution
- Any errors or issues encountered
- Files successfully generated
- Output folder organization verification
- Overall test status (Pass/Fail/Partial)

## Expected Results

### All Tests Should:
1. Complete without application crashes
2. Process all Excel files without errors
3. Generate results for all analysis modules
4. Create reports in all requested formats
5. Save files to correctly organized output folders
6. Maintain proper serial numbering across tests

### Specific Module Expectations:
- **Stability Analysis**: Calculate factors of safety correctly
- **Hydraulic Analysis**: Process flow calculations appropriately
- **Load Analysis**: Handle different load types per bridge category
- **Cross Section Design**: Generate appropriate reinforcement details
- **Abutment Design**: Calculate stability factors correctly

## Troubleshooting

### Common Issues:
1. **Missing Dependencies**: Ensure all packages in pyproject.toml are installed
2. **Port Conflicts**: Change port in .streamlit/config.toml if 8501 is in use
3. **Excel Processing Errors**: Verify Excel files are in .xlsx format
4. **Output Folder Permissions**: Ensure write permissions in application directory

### If Tests Fail:
1. Document the specific error message
2. Take screenshots if applicable
3. Check application logs
4. Try the test again after addressing the issue
5. Report persistent issues to development team

## Test Completion Checklist

Before marking tests as complete, verify:

- [ ] All 5 test scenarios executed
- [ ] Project setup completed for each scenario
- [ ] Excel files uploaded and processed for each scenario
- [ ] All analysis modules run successfully
- [ ] Reports generated in all formats (PDF, HTML, DOCX)
- [ ] Files saved to organized output folders
- [ ] Serial numbering works correctly
- [ ] Results documented in COMPREHENSIVE_TEST_PLAN.md
- [ ] Any issues reported and addressed

## Rollback Plan

If critical issues prevent testing:

1. Document the issue with detailed information
2. Check Git history for previous stable versions
3. Revert to last known good commit if necessary
4. Report issue to development team
5. Continue testing with workaround if possible

## Test Success Metrics

Testing is considered successful if:

1. **Functionality**: 100% of test scenarios execute without critical errors
2. **Performance**: Reports generate within reasonable timeframes (<5 minutes)
3. **Accuracy**: Calculations appear mathematically sound
4. **Organization**: Output files correctly stored in date/bridge_type structure
5. **Completeness**: All output formats generated for all scenarios
6. **Serial Numbering**: Proper incrementing across multiple runs on same date

## Next Steps After Testing

1. Compile detailed test results report
2. Identify and prioritize any issues found
3. Validate fixes for reported issues
4. Conduct regression testing if changes are made
5. Prepare final test summary for stakeholders