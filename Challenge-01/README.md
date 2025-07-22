# Slack Incident Reporter - AI-Powered Incident Analysis Automation

## 🚀 Overview

This project automates the creation of professional incident reports from Slack conversations using AI analysis. It addresses a critical productivity pain point for DevOps teams and incident responders who spend hours manually documenting incidents.

**Key Features:**
- 🔍 **Smart Analysis**: Uses Groq AI to analyze Slack threads and extract incident details
- 📊 **Structured Reports**: Generates both HTML and Markdown reports with consistent formatting
- ⏱️ **Time Tracking**: Automatically extracts and formats timestamps from Slack messages
- 🎯 **Real-time Processing**: Processes incidents instantly with just a message ID
- 📁 **Local Storage**: Saves reports locally for easy access and version control

## 🎯 The Problem It Solves

**Before this automation:**
- Manual incident documentation took 30-60 minutes per incident
- Inconsistent report formats across team members
- Missing critical details due to human oversight
- Time-consuming copy-paste from Slack to documentation tools
- Delayed incident reports affecting post-mortem analysis

**After this automation:**
- Incident reports generated in under 30 seconds
- Consistent, professional formatting every time
- Complete timeline extraction with exact timestamps
- Structured analysis including root cause, impact, and remediation steps
- Immediate availability for stakeholders and compliance

## 🛠️ Technical Architecture

### Components
1. **Slack API Integration**: Fetches conversation threads and user information
2. **Groq AI Analysis**: Processes conversation content using Llama3-70B model
3. **Report Generation**: Creates both HTML and Markdown outputs
4. **Local File Management**: Organizes reports with timestamped filenames

### Technology Stack
- **Python 3.8+**: Core automation logic
- **Groq API**: Fast AI inference (Llama3-70B model)
- **Slack API**: Message retrieval and user management
- **Markdown/HTML**: Report formatting and styling
- **Environment Variables**: Secure configuration management

## 📋 Prerequisites

- Python 3.8 or higher
- Slack workspace with admin access
- Groq API key (free tier available)
- Basic knowledge of command line operations

## 🔧 Setup Instructions

### 1. Clone and Install Dependencies

```bash
git clone 
cd Challenge-1
pip install -r requirements.txt
```

### 2. Slack App Configuration

#### Create a Slack App
1. Go to [api.slack.com/apps](https://api.slack.com/apps)
2. Click "Create New App" → "From scratch"
3. Name your app: "Incident Reporter"
4. Select your workspace

#### Configure Bot Token Scopes
1. Go to "OAuth & Permissions"
2. Add these Bot Token Scopes:
   - `channels:history` - Read channel messages
   - `users:read` - Read user information
   - `groups:history` - Read private channel messages
3. Install the app to your workspace
4. Copy the "Bot User OAuth Token" (starts with `xoxb-`)

#### Configure User Token Scopes
1. Add these User Token Scopes:
   - `channels:history` - Read channel messages
   - `users:read` - Read user information
2. Copy the "User OAuth Token" (starts with `xoxp-`)

#### Get Channel ID
1. In Slack, right-click the channel name
2. Select "Copy link"
3. Extract the channel ID (e.g., `C085J2WR1TN` from the URL)

### 3. Groq API Setup

1. Sign up at [console.groq.com](https://console.groq.com)
2. Create an API key
3. Copy the API key (starts with `gsk_`)

### 4. Environment Configuration

Create a `.env` file in the project root:

```env
# Slack Configuration
SLACK_BOT_TOKEN=xoxb-your-bot-token-here
SLACK_USER_TOKEN=xoxp-your-user-token-here
SLACK_CHANNEL_ID=C085J2WR1TN

# Groq Configuration
GROQ_API_KEY=gsk_your-groq-api-key-here
```

## 🚀 Usage

### Basic Usage
```bash
python slack_incident_reporter.py <message-id>
```

### Example
```bash
python slack_incident_reporter.py p1753168536411769
```

### What Happens
1. **Fetches Thread**: Retrieves all messages in the Slack thread
2. **AI Analysis**: Groq analyzes the conversation and extracts incident details
3. **Report Generation**: Creates both HTML and Markdown reports
4. **Auto-Open**: Opens the HTML report in your default browser

### Output Files
- `incident_reports/2025-01-22_Incident_Report_Storage_Issue.html`
- `incident_reports/2025-01-22_Incident_Report_Storage_Issue.md`

## 📊 Sample Output

### Generated Report Structure
```markdown
# Incident Report: Storage Issue on Shared Runner

**Generated on:** 2025-01-22 15:45:30  
**Incident Date:** 2025-01-22

## Summary
Resolved storage issue on shared runner causing GitLab pipeline failures

## Timeline
- [2025-01-22 15:30:45] - Ajay noticed that storage is full
- [2025-01-22 15:32:12] - Ajay checked pipeline logs and found storage issue
- [2025-01-22 15:35:20] - Ajay SSH into shared runner and ran df -h command
- [2025-01-22 15:38:15] - Ajay found docker images and cache taking more space
- [2025-01-22 15:40:30] - Ajay ran docker system prune -af
- [2025-01-22 15:42:45] - Ajay created automation to remove unused images

## Impact
- GitLab pipelines were failing due to insufficient storage
- Development workflow was blocked for 2 hours
- Affected all projects using the shared runner

## Root Cause
Docker images and cache accumulated over time, consuming 95% of available storage space
```

## 🎯 How Q Developer Assisted

### Initial Problem Analysis
Q Developer helped identify the core productivity pain point:
- Manual incident documentation was time-consuming and error-prone
- Teams needed a way to quickly generate structured reports from Slack conversations
- The solution needed to be simple enough for non-technical users

### Architecture Design
Q Developer suggested:
- Using Groq for fast AI inference instead of slower alternatives
- Implementing both HTML and Markdown outputs for flexibility
- Creating a simple CLI interface that only requires a message ID

### Code Implementation
Q Developer assisted with:
- Slack API integration and message formatting
- Groq API setup and prompt engineering
- Error handling and user feedback
- Report generation with proper styling

### Testing and Refinement
Q Developer helped:
- Debug timestamp extraction issues
- Optimize the AI prompt for better analysis
- Improve error messages and user experience
- Add markdown output alongside HTML

## 📈 Impact and Results

### Time Savings
- **Before**: 30-60 minutes per incident report
- **After**: 30 seconds per incident report
- **Improvement**: 98% reduction in documentation time

### Quality Improvements
- Consistent report format across all incidents
- Complete timeline extraction with exact timestamps
- Structured analysis including root cause and impact
- Professional presentation for stakeholders

### Team Adoption
- Reduced documentation burden on incident responders
- Faster availability of reports for post-mortem analysis
- Improved compliance with incident documentation requirements
- Better knowledge sharing across the organization

## 🔧 Troubleshooting

### Common Issues

#### "Missing required environment variables"
**Solution**: Ensure all variables are set in your `.env` file

#### "Slack API error: thread_not_found"
**Solution**: Verify the message ID is correct and the bot has access to the channel

#### "Error during Groq API call"
**Solution**: Check your Groq API key and ensure you have sufficient credits

#### "Permission denied" errors
**Solution**: Verify your Slack app has the correct scopes and is installed to the workspace

### Debug Mode
Add debug logging by modifying the script to print more detailed information about API calls and responses.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Groq Team**: For providing fast and reliable AI inference
- **Slack Platform**: For comprehensive API access
- **AWS Q Developer**: For assistance in building this automation
- **Open Source Community**: For the libraries that made this possible

---

**Built with ❤️ using AWS Q Developer**

*Tagged with #q-developer-challenge-1*
