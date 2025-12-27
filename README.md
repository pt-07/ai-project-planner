# AI-Powered Project Planning Tool

An interactive CLI tool that helps gather requirements and generate system designs for coding projects using Claude AI (Sonnet 4.5).

## Features

- **Interactive Requirements Gathering**: Claude asks 8 focused questions to understand your project needs
- **Structured Requirements**: Automatically categorizes requirements as functional, non-functional, or constraints
- **SQLite Database**: Persistent storage for all projects and requirements
- **Markdown Export**: Export project documentation with full conversation history
- **Project Management**: Create, list, continue, and delete projects

## Tech Stack

- **Python 3.10+**
- **SQLAlchemy** - Database ORM with SQLite
- **Anthropic Claude API** - Claude Sonnet 4.5 for AI interactions
- **Python-dotenv** - Environment variable management

## Project Structure

```
ai-project-planner/
├── .env                    # Your API keys (create from .env.example)
├── .env.example           # Template for environment variables
├── requirements.txt       # Python dependencies
├── main.py               # CLI entry point
├── README.md             # This file
├── modules/
│   ├── __init__.py       # Module exports
│   ├── storage.py        # SQLAlchemy models (Project, Requirement, DesignArtifact)
│   ├── requirements.py   # Claude API integration for requirements gathering
│   ├── design.py         # Placeholder for design generation
│   └── export.py         # Markdown export functionality
├── data/
│   └── projects.db       # SQLite database (auto-generated)
└── exports/              # Exported markdown files (auto-generated)
```

## Installation

### 1. Clone or Download the Project

```bash
cd ai-project-planner
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

Or install manually:

```bash
pip install anthropic python-dotenv sqlalchemy
```

### 3. Set Up Environment Variables

1. Copy the example env file:
   ```bash
   cp .env.example .env
   ```

2. Get your Anthropic API key from [https://console.anthropic.com/settings/keys](https://console.anthropic.com/settings/keys)

3. Edit `.env` and add your API key:
   ```
   ANTHROPIC_API_KEY=your_actual_api_key_here
   ```

## Usage

### Start the Application

```bash
python main.py
```

### Main Menu Options

1. **Create new project** - Start a new project with requirements gathering
2. **Continue existing project** - Work on an existing project
3. **List all projects** - View all projects in the database
4. **Export project to markdown** - Export a project's documentation
5. **Delete project** - Remove a project from the database
6. **Exit** - Close the application

### Workflow Example

1. **Create a new project**
   - Enter project name and description
   - Choose to gather requirements immediately

2. **Answer 8 questions**
   - Claude will ask focused questions about your project
   - Provide detailed answers to help extract requirements

3. **Review extracted requirements**
   - Claude automatically categorizes your requirements
   - Requirements are saved to the database

4. **Generate system design** (NEW!)
   - Choose from complete system design or individual artifacts
   - Generate architecture, data models, API specs, tech stack, and more
   - All designs saved to database

5. **Export documentation**
   - Export to markdown with full conversation history and design artifacts
   - File saved to `exports/` directory

## Requirements Categories

The tool categorizes requirements into three types:

- **Functional Requirements**: What the system should do (features, capabilities)
- **Non-Functional Requirements**: How the system should perform (performance, security, usability)
- **Constraints**: Limitations and restrictions (platforms, technologies, budget)

## Database Schema

### Project
- `id`: Primary key
- `name`: Project name
- `description`: Project description
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

### Requirement
- `id`: Primary key
- `project_id`: Foreign key to Project
- `category`: 'functional', 'non-functional', or 'constraint'
- `description`: Requirement text
- `created_at`: Creation timestamp

### DesignArtifact
- `id`: Primary key
- `project_id`: Foreign key to Project
- `artifact_type`: Type of design artifact
- `content`: Design content
- `created_at`: Creation timestamp

## API Usage

The tool uses Claude Sonnet 4.5 (`claude-sonnet-4-5-20250929`) for:

- Generating focused questions based on project context
- Building upon previous answers for deeper understanding
- Extracting structured requirements from conversation
- Categorizing requirements appropriately

## Export Format

Exported markdown files include:

- Project metadata (name, description, timestamps)
- Full Q&A conversation history
- Categorized requirements lists
- Design artifacts (when available)

## Design Generation Features

The tool now includes comprehensive AI-powered design generation:

### Available Design Artifacts

1. **Complete System Design** - A comprehensive design document including all sections below
2. **System Architecture** - High-level architecture, components, interactions, and patterns
3. **Data Model** - Database schema, entity relationships, and data structures
4. **API Specification** - Endpoint definitions, request/response formats, authentication
5. **Technology Stack** - Recommended technologies with justifications and alternatives
6. **Implementation Plan** - Phased roadmap with milestones and complexity estimates

### Using Design Generation

From the "Continue existing project" menu:
- Select option 2 to generate design
- Choose which artifacts to generate (individual or all)
- Review the generated design in the terminal
- All designs are automatically saved to the database
- Export to markdown to get a complete document

### Design Quality

All designs are generated by Claude Sonnet 4.5 based on your project requirements and include:
- Practical, implementable solutions
- Modern best practices
- Detailed technical specifications
- Clear explanations and justifications

## Troubleshooting

### "ANTHROPIC_API_KEY not found"
- Make sure you created `.env` file from `.env.example`
- Verify your API key is correctly set in `.env`
- API key should not have quotes around it

### Import errors for SQLAlchemy or Anthropic
- Run `pip install -r requirements.txt`
- Verify you're using Python 3.10 or higher

### Database errors
- The `data/` directory and `projects.db` are created automatically
- If you encounter issues, delete `data/projects.db` and restart

## Contributing

This is a personal project tool. Feel free to fork and customize for your needs.

## License

MIT License - Use freely for personal or commercial projects.

## Notes

- All data is stored locally in SQLite
- API calls are made only during requirements gathering
- Conversation history is preserved for context
- Exports are human-readable markdown format
