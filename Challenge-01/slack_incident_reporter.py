#!/usr/bin/env python3
"""
Slack Incident Reporter

This script fetches Slack conversation threads, analyzes them using Amazon Bedrock (Claude),
and generates structured incident reports as local HTML files.
"""

import os
import sys
import json
import datetime
import webbrowser
from pathlib import Path
import markdown
import requests
import re
from dotenv import load_dotenv
import groq

# Load environment variables
load_dotenv()

# Environment variables
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_USER_TOKEN = os.getenv("SLACK_USER_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
SLACK_CHANNEL_ID = os.getenv("SLACK_CHANNEL_ID", "C085J2WR1TN")

# Validate environment variables
required_env_vars = [
    "SLACK_BOT_TOKEN", "SLACK_USER_TOKEN", 
    "GROQ_API_KEY"
]

missing_vars = [var for var in required_env_vars if not os.getenv(var)]
if missing_vars:
    print(f"Error: Missing required environment variables: {', '.join(missing_vars)}")
    print("Please set these variables in a .env file or in your environment.")
    sys.exit(1)

class SlackIncidentReporter:
    def __init__(self):
        """Initialize the Slack Incident Reporter."""
        # Groq client
        self.groq_client = groq.Groq(api_key=GROQ_API_KEY)
        
        # Create reports directory if it doesn't exist
        self.reports_dir = Path("incident_reports")
        self.reports_dir.mkdir(exist_ok=True)
        
        # CSS for styling the HTML reports
        self.css = """
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                line-height: 1.6;
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f5f5f5;
            }
            .container {
                background: white;
                padding: 30px;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            h1 {
                color: #2c3e50;
                border-bottom: 3px solid #3498db;
                padding-bottom: 10px;
            }
            h2 {
                color: #34495e;
                margin-top: 30px;
            }
            h3 {
                color: #7f8c8d;
            }
            table {
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
            }
            th, td {
                border: 1px solid #ddd;
                padding: 12px;
                text-align: left;
            }
            th {
                background-color: #3498db;
                color: white;
                font-weight: bold;
            }
            tr:nth-child(even) {
                background-color: #f2f2f2;
            }
            .priority-high {
                color: #e74c3c;
                font-weight: bold;
            }
            .priority-medium {
                color: #f39c12;
                font-weight: bold;
            }
            .priority-low {
                color: #27ae60;
                font-weight: bold;
            }
            .status-resolved {
                color: #27ae60;
                font-weight: bold;
            }
            .status-investigating {
                color: #f39c12;
                font-weight: bold;
            }
            .status-monitoring {
                color: #3498db;
                font-weight: bold;
            }
            ul, ol {
                margin: 10px 0;
                padding-left: 20px;
            }
            li {
                margin: 5px 0;
            }
            .metadata {
                background-color: #ecf0f1;
                padding: 15px;
                border-radius: 5px;
                margin: 20px 0;
            }
            .section {
                margin-bottom: 30px;
                border-bottom: 1px solid #eee;
                padding-bottom: 20px;
            }
        </style>
        """

    def get_slack_user(self, user_id):
        """Fetches user information from Slack."""
        headers = {"Authorization": f"Bearer {SLACK_BOT_TOKEN}"}
        url = "https://slack.com/api/users.info"
        params = {"user": user_id}
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            if data.get('ok'):
                return data['user']
            else:
                print(f"Warning: Could not fetch user {user_id}. Error: {data.get('error')}")
                return {}
        except requests.exceptions.RequestException as e:
            print(f"Warning: Could not fetch user {user_id}. Error: {e}")
            return {}

    def clean_slack_formatting(self, text):
        """Removes Slack-specific formatting from text."""
        # Remove user mentions <@U123456>
        text = re.sub(r'<@[A-Z0-9]+>', '', text)
        
        # Remove channel mentions <#C123456>
        text = re.sub(r'<#[A-Z0-9]+>', '', text)
        
        # Remove URLs <https://example.com>
        text = re.sub(r'<https?://[^>]+>', '', text)
        
        # Remove bold formatting *text*
        text = re.sub(r'\*(.*?)\*', r'\1', text)
        
        # Remove italic formatting _text_
        text = re.sub(r'_(.*?)_', r'\1', text)
        
        # Remove strikethrough formatting ~text~
        text = re.sub(r'~(.*?)~', r'\1', text)
        
        # Remove code formatting `text`
        text = re.sub(r'`(.*?)`', r'\1', text)
        
        # Clean up extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text

    def fetch_slack_thread(self, channel_id, thread_ts):
        """Fetches all messages in a Slack thread."""
        print(f"Fetching Slack thread for channel: {channel_id}, thread_ts: {thread_ts}...")
        headers = {"Authorization": f"Bearer {SLACK_BOT_TOKEN}"}
        url = "https://slack.com/api/conversations.replies"
        params = {
            "channel": channel_id,
            "ts": thread_ts
        }
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            if not data.get('ok'):
                print(f"Slack API error: {data.get('error')}")
                sys.exit(1)
            print("Successfully fetched thread.")
            return data
        except requests.exceptions.RequestException as e:
            print(f"Error fetching Slack thread: {e}")
            sys.exit(1)

    def format_conversation(self, thread_data):
        """Formats the thread messages into a single string."""
        messages = thread_data['messages']
        
        conversation = []
        for message in messages:
            # Get timestamp
            ts = float(message.get('ts', 0))
            timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
            
            # Get user info
            user_id = message.get('user', 'unknown_user')
            user_info = self.get_slack_user(user_id)
            username = user_info.get('real_name', user_info.get('name', 'unknown_user'))
            
            # Get message text
            text = message.get('text', '')
            
            # Handle message formatting (remove Slack formatting)
            text = self.clean_slack_formatting(text)
            
            conversation.append(f"[{timestamp}] {username}: {text}")
            
        return "\n".join(conversation)

    def analyze_with_groq(self, conversation):
        """
        Sends the conversation to Groq API for analysis and returns a
        structured summary and root cause analysis.
        """
        print("Analyzing conversation with Groq API...")

        try:
            # This detailed prompt guides the AI to give us the exact format we need.
            system_prompt = """
            You are an expert incident response analyst tasked with creating a structured report from a Slack conversation transcript.
            Your response MUST be a single, valid JSON object and nothing else. All values in the JSON object must be strings.
            Analyze the conversation to identify key events, user actions, and outcomes.
            
            IMPORTANT: Use the EXACT timestamps from the conversation in the timeline_markdown field. Do not use generic times like "Unknown Time" or "10:09 PM". Use the full timestamp format [YYYY-MM-DD HH:MM:SS] as shown in the conversation.

            The JSON object must contain these exact keys:
            - "summary"
            - "author" (Identify the primary person who resolved the issue)
            - "priority" (Value must be one of: "High", "Medium", "Low")
            - "status" (Value must be one of: "Resolved", "Investigating", "Monitoring")
            - "description"
            - "category" (e.g., "Infrastructure", "Application", "Database")
            - "environment" (e.g., "Production", "Staging")
            - "affected_resources" (Comma-separated list, e.g., "Jenkins, API Server")
            - "root_cause_text"
            - "remediation_steps_text"
            - "impact_text"
            - "timeline_markdown": "A detailed, multi-line timeline as a single JSON string. Each event must be a Markdown bullet point on a new line, using the EXACT timestamps from the conversation (format: [YYYY-MM-DD HH:MM:SS]). All newlines MUST be escaped as \\n. Example format: '- [2025-01-22 15:30:45] - Ajay noticed that storage is full.\\n- [2025-01-22 15:32:12] - Yuga cleaned up storage to free space.'"
            - "what_went_well_markdown": "A Markdown numbered list as a single JSON string, describing what went well during the incident response. All newlines MUST be escaped as \\n."
            - "what_went_wrong_markdown": "A Markdown numbered list as a single JSON string, describing what could be improved. All newlines MUST be escaped as \\n."
            """

            chat_completion = self.groq_client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt,
                    },
                    {
                        "role": "user",
                        "content": f"Here is the Slack thread transcript:\n\n{conversation}",
                    },
                ],
                model="llama3-70b-8192",
                temperature=0.2,
                response_format={"type": "json_object"},
            )

            response_text = chat_completion.choices[0].message.content
            print("Analysis complete.")
            
            # Parse the JSON string from the AI into a Python dictionary
            return json.loads(response_text)

        except Exception as e:
            print(f"Error during Groq API call: {e}")
            sys.exit(1)

    def create_local_report(self, title, content, incident_date):
        """Creates a local HTML incident report."""
        print("Creating local incident report...")
        
        # Generate filename
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_title = safe_title.replace(' ', '_')
        html_filename = f"{incident_date}_{safe_title}.html"
        md_filename = f"{incident_date}_{safe_title}.md"
        html_filepath = self.reports_dir / html_filename
        md_filepath = self.reports_dir / md_filename
        
        # Save the original markdown content
        try:
            with open(md_filepath, 'w', encoding='utf-8') as f:
                # Add title and metadata to the markdown file
                md_header = f"# {title}\n\n"
                md_header += f"**Generated on:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  \n"
                md_header += f"**Incident Date:** {incident_date}\n\n"
                f.write(md_header + content)
            print(f"Successfully created markdown report: {md_filepath}")
        except Exception as e:
            print(f"Error creating markdown report: {e}")
        
        # Convert markdown to HTML
        html_content = markdown.markdown(content, extensions=['tables'])
        
        # Create full HTML document
        html_document = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    {self.css}
</head>
<body>
    <div class="container">
        <h1>{title}</h1>
        <div class="metadata">
            <strong>Generated on:</strong> {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br>
            <strong>Incident Date:</strong> {incident_date}
        </div>
        {html_content}
    </div>
</body>
</html>
"""
        
        try:
            with open(html_filepath, 'w', encoding='utf-8') as f:
                f.write(html_document)
            
            print(f"Successfully created HTML report: {html_filepath}")
            
            # Open the report in the default browser
            webbrowser.open(f'file://{os.path.abspath(html_filepath)}')
            
            return str(html_filepath)
        except Exception as e:
            print(f"Error creating HTML report: {e}")
            return None

    def process_incident(self, channel_id, thread_ts):
        """
        Process an incident from a Slack conversation.
        
        Args:
            channel_id (str): The ID of the Slack channel
            thread_ts (str): The timestamp of the thread
            
        Returns:
            str: Path to the generated HTML report
        """
        # 1. Fetch Slack thread
        thread_data = self.fetch_slack_thread(channel_id, thread_ts)
        if not thread_data or 'messages' not in thread_data:
            print("Could not retrieve thread data. Exiting.")
            sys.exit(1)

        # Determine the incident date from the timestamp of the first message
        first_message = thread_data['messages'][0]
        incident_timestamp = float(first_message['ts'])
        incident_date = datetime.datetime.fromtimestamp(incident_timestamp).strftime('%Y-%m-%d')
        
        # 2. Format conversation
        conversation_text = self.format_conversation(thread_data)
        
        # 3. Analyze with Groq API
        analysis = self.analyze_with_groq(conversation_text)
        if not analysis:
            print("Analysis failed. Exiting.")
            sys.exit(1)
            
        # 4. Assemble the local document from the AI's analysis
        # Use .get() for safety in case the AI misses a field
        summary = analysis.get("summary", "")
        author = analysis.get("author", "")
        priority = analysis.get("priority", "Medium")
        status = analysis.get("status", "")
        description = analysis.get("description", "")
        category = analysis.get("category", "")
        environment = analysis.get("environment", "")
        affected_resources = analysis.get("affected_resources", "")
        root_cause = analysis.get("root_cause_text", "")
        remediation = analysis.get("remediation_steps_text", "")
        timeline = analysis.get("timeline_markdown", "")
        impact = analysis.get("impact_text", "")
        what_went_well = analysis.get("what_went_well_markdown", "")
        what_went_wrong = analysis.get("what_went_wrong_markdown", "")

        report_title = f"Incident Report: {summary}"
        
        # Construct the markdown table and the rest of the document
        document_content = f"""
| | |
| --- | --- |
| **Summary** | {summary} |
| **Author** | {author} |
| **Priority Level** | {priority} |
| **Status** | {status} |
| **Description** | {description} |
| **Date** | {incident_date} |
| **Category** | {category} |
| **Environment** | {environment} |
| **Affected Resource(s)** | {affected_resources} |

### Root Cause:
{root_cause}

### Remediation Steps:
{remediation}

### Timelines:
{timeline}

### Impact:
{impact}

### Lessons Learned:
#### What went well
{what_went_well}

#### What went wrong
{what_went_wrong}
"""

        return self.create_local_report(report_title, document_content, incident_date)


def main():
    """Main function to orchestrate the workflow."""
    if len(sys.argv) < 2:
        print("Usage: python slack_incident_reporter.py <message-id>")
        print("Example: python slack_incident_reporter.py p1753168536411769")
        print("Note: Channel ID is set in .env file (default: C085J2WR1TN)")
        sys.exit(1)
        
    message_id = sys.argv[1]
    
    # Convert message ID to timestamp if needed
    if message_id.startswith('p'):
        # Remove the 'p' prefix and convert to timestamp
        # The message ID format is p1753168536411769, we need to convert to timestamp
        timestamp_str = message_id[1:]  # Remove 'p' prefix
        print(f"Converting message ID: {message_id} -> timestamp: {timestamp_str}")
        
        # Slack timestamps are in microseconds, convert to seconds
        if len(timestamp_str) > 10:
            # Convert from microseconds to seconds
            thread_ts = str(float(timestamp_str) / 1000000)
            print(f"Converted from microseconds to seconds: {thread_ts}")
        else:
            thread_ts = timestamp_str
            print(f"Using as-is: {thread_ts}")
    else:
        thread_ts = message_id
        print(f"Using message ID as timestamp: {thread_ts}")
    
    reporter = SlackIncidentReporter()
    report_path = reporter.process_incident(SLACK_CHANNEL_ID, thread_ts)
    
    if report_path:
        # Get the markdown file path by replacing .html with .md
        md_path = report_path.replace('.html', '.md')
        print(f"\nWorkflow finished!")
        print(f"HTML report saved to: {report_path}")
        print(f"Markdown report saved to: {md_path}")
    else:
        print("\nWorkflow failed to generate report.")


if __name__ == "__main__":
    main()
