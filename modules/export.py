import os
from datetime import datetime


class MarkdownExporter:
    """Exports project requirements and design artifacts to markdown format"""

    def __init__(self, output_dir='exports'):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def export_project(self, project, db, conversation_summary=None):
        """Export a complete project to markdown"""

        # Create filename based on project name and timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_name = "".join(c if c.isalnum() else "_" for c in project.name)
        filename = f"{safe_name}_{timestamp}.md"
        filepath = os.path.join(self.output_dir, filename)

        # Build markdown content
        content = []

        # Header
        content.append(f"# {project.name}\n")
        content.append(f"**Created:** {project.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n")
        content.append(f"**Last Updated:** {project.updated_at.strftime('%Y-%m-%d %H:%M:%S')}\n")
        content.append("---\n")

        # Description
        content.append("## Project Description\n")
        content.append(f"{project.description}\n")
        content.append("---\n")

        # Requirements gathering conversation (if provided)
        if conversation_summary:
            content.append("## Requirements Gathering Session\n")
            content.append(conversation_summary)
            content.append("\n---\n")

        # Requirements
        content.append("## Requirements\n")

        # Group requirements by category
        functional_reqs = [r for r in project.requirements if r.category == 'functional']
        non_functional_reqs = [r for r in project.requirements if r.category == 'non_functional']
        constraints = [r for r in project.requirements if r.category == 'constraint']

        if functional_reqs:
            content.append("### Functional Requirements\n")
            for i, req in enumerate(functional_reqs, 1):
                content.append(f"{i}. {req.description}\n")
            content.append("\n")

        if non_functional_reqs:
            content.append("### Non-Functional Requirements\n")
            for i, req in enumerate(non_functional_reqs, 1):
                content.append(f"{i}. {req.description}\n")
            content.append("\n")

        if constraints:
            content.append("### Constraints\n")
            for i, constraint in enumerate(constraints, 1):
                content.append(f"{i}. {constraint.description}\n")
            content.append("\n")

        if not project.requirements:
            content.append("*No requirements defined yet.*\n\n")

        content.append("---\n")

        # Design Artifacts
        if project.design_artifacts:
            content.append("## Design Artifacts\n")
            for artifact in project.design_artifacts:
                content.append(f"### {artifact.artifact_type.replace('_', ' ').title()}\n")
                content.append(f"{artifact.content}\n")
                content.append("\n")
        else:
            content.append("## Design Artifacts\n")
            content.append("*No design artifacts generated yet.*\n")

        # Write to file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("".join(content))

        return filepath

    def export_requirements_only(self, project):
        """Export only the requirements section"""

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_name = "".join(c if c.isalnum() else "_" for c in project.name)
        filename = f"{safe_name}_requirements_{timestamp}.md"
        filepath = os.path.join(self.output_dir, filename)

        content = []
        content.append(f"# Requirements: {project.name}\n")
        content.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        # Group requirements by category
        functional_reqs = [r for r in project.requirements if r.category == 'functional']
        non_functional_reqs = [r for r in project.requirements if r.category == 'non_functional']
        constraints = [r for r in project.requirements if r.category == 'constraint']

        if functional_reqs:
            content.append("## Functional Requirements\n")
            for i, req in enumerate(functional_reqs, 1):
                content.append(f"{i}. {req.description}\n")
            content.append("\n")

        if non_functional_reqs:
            content.append("## Non-Functional Requirements\n")
            for i, req in enumerate(non_functional_reqs, 1):
                content.append(f"{i}. {req.description}\n")
            content.append("\n")

        if constraints:
            content.append("## Constraints\n")
            for i, constraint in enumerate(constraints, 1):
                content.append(f"{i}. {constraint.description}\n")

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("".join(content))

        return filepath
