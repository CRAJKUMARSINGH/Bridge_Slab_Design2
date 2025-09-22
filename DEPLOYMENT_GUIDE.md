# Bridge Slab Design System - Streamlit Cloud Deployment Guide

## Overview
This guide provides detailed instructions for deploying the Bridge Slab Design application to Streamlit Cloud. The application is now fully configured for deployment with all necessary files.

## Prerequisites
1. A GitHub account
2. A Streamlit Cloud account (free to create at https://streamlit.io/cloud)
3. An Anthropic API key (optional, for Claude AI features)

## Deployment Steps

### Step 1: Verify Repository on GitHub
Ensure your repository is available on GitHub at:
```
https://github.com/CRAJKUMARSINGH/Bridge_Slab_Design2
```

The repository should contain:
- `app.py` - Main application file
- `requirements.txt` - Python dependencies
- `Procfile` - Deployment configuration
- `.streamlit/config.toml` - Streamlit configuration
- All modules and utility files

### Step 2: Access Streamlit Cloud
1. Go to https://streamlit.io/cloud
2. Sign in with your GitHub account
3. If this is your first time, you may need to authorize Streamlit Cloud to access your GitHub repositories

### Step 3: Create a New App
1. Click the "New app" button
2. Select your repository:
   - Repository: `CRAJKUMARSINGH/Bridge_Slab_Design2`
   - Branch: `main` (default)
   - Main file path: `app.py` (should be auto-detected)
3. Click "Deploy!"

### Step 4: Monitor Deployment
1. The deployment process will begin automatically
2. You can monitor the build logs in the "Settings" tab
3. Initial deployment may take 2-5 minutes

### Step 5: Configure Environment Variables (Optional)
If you want to use Claude AI features:

1. Go to your app's "Settings" tab
2. Scroll down to "Secrets" section
3. Add a new secret:
   - Name: `ANTHROPIC_API_KEY`
   - Value: Your actual Anthropic API key
4. Click "Save"

### Step 6: Access Your Deployed App
1. Once deployment is complete, you'll see a "Your app is deployed" message
2. Click the provided URL to access your application
3. The app should be available at a URL like:
   ```
   https://[your-app-name].streamlit.app
   ```

## Deployment Configuration Details

### Requirements File
The `requirements.txt` file contains all necessary dependencies:
```
anthropic>=0.68.0
numpy>=2.3.3
openpyxl>=3.1.5
pandas>=2.3.2
plotly>=6.3.0
reportlab>=4.4.4
streamlit>=1.49.1
```

### Procfile
The `Procfile` specifies how to run the application:
```
web: streamlit run app.py --server.port=$PORT
```

### Streamlit Configuration
The `.streamlit/config.toml` file configures Streamlit settings:
```toml
[server]
headless = true
address = "0.0.0.0"
port = 5000

[theme]
primaryColor = "#FF6B6B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
```

## Troubleshooting Deployment Issues

### Common Issues and Solutions

1. **Build Failures**
   - Check the build logs in the "Settings" tab
   - Ensure all dependencies in `requirements.txt` are correct
   - Verify `app.py` is in the root directory

2. **Application Crashes on Startup**
   - Check the application logs in the "Settings" tab
   - Ensure all required modules are imported correctly
   - Verify file paths are correct for Streamlit Cloud environment

3. **Missing Dependencies**
   - Make sure all required packages are listed in `requirements.txt`
   - Check for version conflicts between packages

4. **Port Configuration Issues**
   - The application uses the `Procfile` to set the port correctly
   - Streamlit Cloud automatically provides the `$PORT` environment variable

### Environment-Specific Considerations

1. **File System Access**
   - Streamlit Cloud provides write access to the application directory
   - The organized output folder system will work correctly
   - Files saved to the `outputs/` directory will persist during the app session

2. **Memory and Performance**
   - Streamlit Cloud apps have resource limits
   - Large PDF generation may take longer than on local machines
   - Consider optimizing large calculations if needed

3. **Security**
   - Environment variables are securely stored
   - Never commit API keys to the repository
   - Use the "Secrets" section for sensitive information

## Updating Your Deployed Application

To update your deployed application after making changes:

1. **Commit and push changes to GitHub:**
   ```bash
   git add .
   git commit -m "Description of changes"
   git push origin main
   ```

2. **Redeploy on Streamlit Cloud:**
   - Go to your app's "Settings" tab
   - Click "Reboot app" to pull the latest changes
   - Or click "Delete app" and recreate it to ensure a clean deployment

## Best Practices for Streamlit Cloud Deployment

1. **Keep Dependencies Minimal**
   - Only include necessary packages in `requirements.txt`
   - Regularly review and update dependencies

2. **Optimize for Performance**
   - Use `@st.cache_data` and `@st.cache_resource` decorators for expensive operations
   - Consider lazy loading for large datasets

3. **Handle Errors Gracefully**
   - Implement try/except blocks for external API calls
   - Provide informative error messages to users

4. **Monitor Usage**
   - Check Streamlit Cloud analytics for usage patterns
   - Monitor for any performance issues

## Support and Resources

- Streamlit Documentation: https://docs.streamlit.io/
- Streamlit Community: https://discuss.streamlit.io/
- This Repository Issues: https://github.com/CRAJKUMARSINGH/Bridge_Slab_Design2/issues

## Contact Information

For issues or questions about this deployment, contact:
- Rajkumar Singh Chauhan
- Email: crajkumarsingh@hotmail.com

## Version Information

- Application Version: 1.0.0
- Last Updated: September 23, 2025
- Deployment Target: Streamlit Cloud