"""
User Stories module

Generates user stories with acceptance criteria from requirements
and exports them to CSV format for project management tools
"""

import os
import csv
import json
from datetime import datetime
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()


class UserStoryGenerator:
    """Generates user stories with acceptance criteria using Claude API"""

    def __init__(self):
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment variables")
        self.client = Anthropic(api_key=api_key)
        self.model = "claude-sonnet-4-5-20250929"

    def _format_requirements(self, requirements):
        """Format requirements into a structured text"""
        formatted = []

        functional = [r for r in requirements if r.category == 'functional']
        non_functional = [r for r in requirements if r.category == 'non_functional']
        constraints = [r for r in requirements if r.category == 'constraint']

        if functional:
            formatted.append("FUNCTIONAL REQUIREMENTS:")
            for i, req in enumerate(functional, 1):
                formatted.append(f"{i}. {req.description}")
            formatted.append("")

        if non_functional:
            formatted.append("NON-FUNCTIONAL REQUIREMENTS:")
            for i, req in enumerate(non_functional, 1):
                formatted.append(f"{i}. {req.description}")
            formatted.append("")

        if constraints:
            formatted.append("CONSTRAINTS:")
            for i, constraint in enumerate(constraints, 1):
                formatted.append(f"{i}. {constraint.description}")
            formatted.append("")

        return "\n".join(formatted)

    def generate_user_stories(self, project, db):
        """Generate user stories with acceptance criteria from requirements"""

        project = db.get_project(project.id)

        if not project.requirements:
            raise ValueError("Cannot generate user stories: No requirements found")

        requirements_text = self._format_requirements(project.requirements)

        system_prompt = """You are an expert Agile product owner and business analyst. Generate comprehensive user stories with detailed acceptance criteria.

Return your response as a JSON array of user stories. Each story must follow this exact structure:
{
    "id": "US-001",
    "title": "Short descriptive title",
    "user_story": "As a [role], I want [feature] so that [benefit]",
    "description": "Detailed description of what needs to be built",
    "priority": "High|Medium|Low",
    "story_points": "1|2|3|5|8|13",
    "epic": "Epic name this story belongs to",
    "acceptance_criteria": [
        "Given [context], when [action], then [outcome]",
        "Given [context], when [action], then [outcome]"
    ],
    "notes": "Additional technical notes or dependencies"
}

Ensure all user stories are:
- Written in proper user story format
- Have clear, testable acceptance criteria
- Prioritized appropriately
- Estimated with story points
- Grouped into logical epics"""

        user_prompt = f"""Generate comprehensive user stories for:

PROJECT: {project.name}
DESCRIPTION: {project.description}

{requirements_text}

Create a complete set of user stories that cover all functional requirements. Include:
- Clear user story format (As a... I want... So that...)
- Detailed acceptance criteria in Given/When/Then format
- Appropriate priority (High/Medium/Low)
- Story point estimates
- Epic grouping
- Technical notes where relevant

Return ONLY a valid JSON array of user stories, no additional text."""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=6000,
            system=system_prompt,
            messages=[{
                "role": "user",
                "content": user_prompt
            }]
        )

        stories_json = response.content[0].text.strip()

        # Parse JSON response
        try:
            # Remove markdown code blocks if present
            if stories_json.startswith('```'):
                stories_json = stories_json.split('```')[1]
                if stories_json.startswith('json'):
                    stories_json = stories_json[4:]
                stories_json = stories_json.strip()

            user_stories = json.loads(stories_json)

            # Convert to formatted text for database storage
            formatted_stories = self._format_stories_for_display(user_stories)

            # Save to database
            db.add_design_artifact(
                project_id=project.id,
                artifact_type='user_stories',
                content=formatted_stories
            )

            return user_stories

        except json.JSONDecodeError as e:
            print(f"Error parsing user stories JSON: {e}")
            print(f"Raw response: {stories_json}")
            return []

    def _format_stories_for_display(self, user_stories):
        """Format user stories for readable display"""
        formatted = []

        for story in user_stories:
            formatted.append(f"ID: {story.get('id', 'N/A')}")
            formatted.append(f"Title: {story.get('title', 'N/A')}")
            formatted.append(f"Epic: {story.get('epic', 'N/A')}")
            formatted.append(f"Priority: {story.get('priority', 'N/A')}")
            formatted.append(f"Story Points: {story.get('story_points', 'N/A')}")
            formatted.append(f"\nUser Story:")
            formatted.append(f"  {story.get('user_story', 'N/A')}")
            formatted.append(f"\nDescription:")
            formatted.append(f"  {story.get('description', 'N/A')}")
            formatted.append(f"\nAcceptance Criteria:")
            for i, criterion in enumerate(story.get('acceptance_criteria', []), 1):
                formatted.append(f"  {i}. {criterion}")
            if story.get('notes'):
                formatted.append(f"\nNotes:")
                formatted.append(f"  {story.get('notes')}")
            formatted.append("\n" + "="*80 + "\n")

        return "\n".join(formatted)

    def export_to_csv(self, user_stories, project_name, output_dir='exports'):
        """Export user stories to CSV format"""

        os.makedirs(output_dir, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_name = "".join(c if c.isalnum() else "_" for c in project_name)
        filename = f"{safe_name}_user_stories_{timestamp}.csv"
        filepath = os.path.join(output_dir, filename)

        # CSV headers
        headers = [
            'Story ID',
            'Epic',
            'Title',
            'User Story',
            'Description',
            'Priority',
            'Story Points',
            'Acceptance Criteria',
            'Notes'
        ]

        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writeheader()

            for story in user_stories:
                # Join acceptance criteria into a single field with newlines
                ac_text = "\n".join(story.get('acceptance_criteria', []))

                writer.writerow({
                    'Story ID': story.get('id', ''),
                    'Epic': story.get('epic', ''),
                    'Title': story.get('title', ''),
                    'User Story': story.get('user_story', ''),
                    'Description': story.get('description', ''),
                    'Priority': story.get('priority', ''),
                    'Story Points': story.get('story_points', ''),
                    'Acceptance Criteria': ac_text,
                    'Notes': story.get('notes', '')
                })

        return filepath

    def export_to_markdown(self, user_stories, project_name, output_dir='exports'):
        """Export user stories to markdown format"""

        os.makedirs(output_dir, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_name = "".join(c if c.isalnum() else "_" for c in project_name)
        filename = f"{safe_name}_user_stories_{timestamp}.md"
        filepath = os.path.join(output_dir, filename)

        content = []
        content.append(f"# User Stories: {project_name}\n")
        content.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        content.append("---\n\n")

        # Group by epic
        epics = {}
        for story in user_stories:
            epic = story.get('epic', 'Uncategorized')
            if epic not in epics:
                epics[epic] = []
            epics[epic].append(story)

        # Write stories by epic
        for epic, stories in epics.items():
            content.append(f"## Epic: {epic}\n")

            for story in stories:
                content.append(f"### {story.get('id', 'N/A')}: {story.get('title', 'N/A')}\n")
                content.append(f"**Priority:** {story.get('priority', 'N/A')} | **Story Points:** {story.get('story_points', 'N/A')}\n\n")

                content.append(f"**User Story:**  \n")
                content.append(f"_{story.get('user_story', 'N/A')}_\n\n")

                content.append(f"**Description:**  \n")
                content.append(f"{story.get('description', 'N/A')}\n\n")

                content.append(f"**Acceptance Criteria:**\n")
                for i, criterion in enumerate(story.get('acceptance_criteria', []), 1):
                    content.append(f"{i}. {criterion}\n")
                content.append("\n")

                if story.get('notes'):
                    content.append(f"**Notes:**  \n")
                    content.append(f"{story.get('notes')}\n\n")

                content.append("---\n\n")

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("".join(content))

        return filepath
