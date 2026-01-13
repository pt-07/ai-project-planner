#!/usr/bin/env python3
"""
AI-Powered Project Planning Tool
Helps gather requirements and generate system designs for coding projects
"""

import sys
import os
from modules.storage import Database
from modules.requirements import RequirementsGatherer
from modules.export import MarkdownExporter
from modules.design import DesignGenerator
from modules.user_stories import UserStoryGenerator


def print_header():
    """Print application header"""
    print("\n" + "=" * 60)
    print(" AI-POWERED PROJECT PLANNING TOOL")
    print("=" * 60 + "\n")


def print_menu():
    """Print main menu"""
    print("\nMain Menu:")
    print("1. Create new project")
    print("2. Continue existing project")
    print("3. List all projects")
    print("4. Export project to markdown")
    print("5. Delete project")
    print("6. Exit")
    print()


def create_new_project(db):
    """Create a new project and gather requirements"""
    print("\n--- CREATE NEW PROJECT ---\n")

    # Get project details
    name = input("Project name: ").strip()
    if not name:
        print("Error: Project name cannot be empty")
        return

    description = input("Project description: ").strip()
    if not description:
        print("Error: Project description cannot be empty")
        return

    # Create project in database
    project = db.create_project(name, description)
    print(f"\n✓ Project created with ID: {project.id}")

    # Ask if user wants to gather requirements now
    gather_now = input("\nGather requirements now? (y/n): ").strip().lower()
    if gather_now == 'y':
        gather_requirements(db, project.id)


def gather_requirements(db, project_id):
    """Gather requirements for a project using Claude"""
    project = db.get_project(project_id)
    if not project:
        print(f"Error: Project with ID {project_id} not found")
        return

    print(f"\n--- GATHERING REQUIREMENTS FOR: {project.name} ---\n")
    print("The AI will ask you 8 questions to understand your project requirements.")
    print("Answer each question in detail.\n")

    try:
        gatherer = RequirementsGatherer()
        gatherer.start_session(project.name, project.description)

        # Ask first question
        question = gatherer.ask_next_question()

        # Ask 8 questions
        for i in range(8):
            if not question:
                break

            print(f"\n{question}\n")

            # Get user's answer
            answer = input("Your answer: ").strip()
            if not answer:
                print("Skipping empty answer...")
                answer = "No specific requirements for this area."

            # Submit answer and get next question
            answer = f'Q{i+1}: {answer}'
            question = gatherer.ask_next_question(answer)

        print("\n--- EXTRACTING REQUIREMENTS ---\n")
        print("Processing your answers...")

        # Extract structured requirements
        requirements = gatherer.extract_requirements()

        # Save requirements to database
        saved_count = 0

        for req_desc in requirements.get('functional', []):
            db.add_requirement(project.id, 'functional', req_desc)
            saved_count += 1

        for req_desc in requirements.get('non_functional', []):
            db.add_requirement(project.id, 'non_functional', req_desc)
            saved_count += 1

        for constraint_desc in requirements.get('constraints', []):
            db.add_requirement(project.id, 'constraint', constraint_desc)
            saved_count += 1

        print(f"\n✓ Extracted and saved {saved_count} requirements")

        # Display summary
        print("\n--- REQUIREMENTS SUMMARY ---\n")

        if requirements.get('functional'):
            print("Functional Requirements:")
            for i, req in enumerate(requirements['functional'], 1):
                print(f"  {i}. {req}")
            print()

        if requirements.get('non_functional'):
            print("Non-Functional Requirements:")
            for i, req in enumerate(requirements['non_functional'], 1):
                print(f"  {i}. {req}")
            print()

        if requirements.get('constraints'):
            print("Constraints:")
            for i, constraint in enumerate(requirements['constraints'], 1):
                print(f"  {i}. {constraint}")
            print()

        # Ask if user wants to export
        export_now = input("\nExport to markdown? (y/n): ").strip().lower()
        if export_now == 'y':
            exporter = MarkdownExporter()
            conversation_summary = gatherer.get_conversation_summary()
            filepath = exporter.export_project(project, db, conversation_summary)
            print(f"\n✓ Exported to: {filepath}")

    except ValueError as e:
        print(f"\nError: {e}")
        print("Make sure you have set ANTHROPIC_API_KEY in your .env file")
    except Exception as e:
        print(f"\nError gathering requirements: {e}")
        import traceback
        traceback.print_exc()


def list_projects(db):
    """List all projects"""
    print("\n--- ALL PROJECTS ---\n")

    projects = db.get_all_projects()

    if not projects:
        print("No projects found.")
        return

    for project in projects:
        req_count = len(project.requirements)
        design_count = len(project.design_artifacts)

        print(f"ID: {project.id}")
        print(f"Name: {project.name}")
        print(f"Description: {project.description}")
        print(f"Requirements: {req_count}")
        print(f"Design Artifacts: {design_count}")
        print(f"Created: {project.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        print("-" * 60)


def export_project(db):
    """Export a project to markdown"""
    print("\n--- EXPORT PROJECT ---\n")

    project_id = input("Enter project ID to export: ").strip()
    if not project_id.isdigit():
        print("Error: Invalid project ID")
        return

    project = db.get_project(int(project_id))
    if not project:
        print(f"Error: Project with ID {project_id} not found")
        return

    exporter = MarkdownExporter()
    filepath = exporter.export_project(project, db)
    print(f"\n✓ Exported to: {filepath}")


def delete_project(db):
    """Delete a project"""
    print("\n--- DELETE PROJECT ---\n")

    project_id = input("Enter project ID to delete: ").strip()
    if not project_id.isdigit():
        print("Error: Invalid project ID")
        return

    project = db.get_project(int(project_id))
    if not project:
        print(f"Error: Project with ID {project_id} not found")
        return

    print(f"\nProject: {project.name}")
    print(f"Description: {project.description}")

    confirm = input("\nAre you sure you want to delete this project? (yes/no): ").strip().lower()
    if confirm == 'yes':
        db.delete_project(int(project_id))
        print("\n✓ Project deleted")
    else:
        print("\nDeletion cancelled")


def generate_design_menu(db, project_id):
    """Design generation menu"""
    project = db.get_project(project_id)
    if not project:
        print(f"Error: Project with ID {project_id} not found")
        return

    if not project.requirements:
        print("\nError: No requirements found for this project.")
        print("Please gather requirements first before generating design.")
        return

    print("\n--- GENERATE DESIGN ---\n")
    print("Choose what to generate:")
    print("1. Complete system design (comprehensive)")
    print("2. System architecture only")
    print("3. Data model only")
    print("4. API specification only")
    print("5. Technology stack recommendations")
    print("6. Implementation plan/roadmap")
    print("7. Mermaid diagrams (architecture, ERD, sequence, deployment)")
    print("8. Architecture recommendations (patterns, scalability, security)")
    print("9. User stories with acceptance criteria")
    print("10. Generate all individually")
    print("11. Back")

    choice = input("\nChoice: ").strip()

    try:
        generator = DesignGenerator()

        if choice == '1':
            print("\nGenerating complete system design...")
            design = generator.generate_complete_design(project, db)
            print("\n" + "="*60)
            print(design)
            print("="*60)
            print("\n✓ Complete system design generated and saved!")

        elif choice == '2':
            print("\nGenerating system architecture...")
            architecture = generator.generate_architecture(project, db)
            print("\n" + "="*60)
            print(architecture)
            print("="*60)
            print("\n✓ Architecture design generated and saved!")

        elif choice == '3':
            print("\nGenerating data model...")
            data_model = generator.generate_data_model(project, db)
            print("\n" + "="*60)
            print(data_model)
            print("="*60)
            print("\n✓ Data model generated and saved!")

        elif choice == '4':
            print("\nGenerating API specification...")
            api_spec = generator.generate_api_spec(project, db)
            print("\n" + "="*60)
            print(api_spec)
            print("="*60)
            print("\n✓ API specification generated and saved!")

        elif choice == '5':
            print("\nGenerating technology stack recommendations...")
            tech_stack = generator.generate_tech_stack(project, db)
            print("\n" + "="*60)
            print(tech_stack)
            print("="*60)
            print("\n✓ Technology stack recommendations generated and saved!")

        elif choice == '6':
            print("\nGenerating implementation plan...")
            impl_plan = generator.generate_implementation_plan(project, db)
            print("\n" + "="*60)
            print(impl_plan)
            print("="*60)
            print("\n✓ Implementation plan generated and saved!")

        elif choice == '7':
            print("\nGenerating Mermaid diagrams...")
            diagrams = generator.generate_diagrams(project, db)
            print("\n" + "="*60)
            print(diagrams)
            print("="*60)
            print("\n✓ Mermaid diagrams generated and saved!")

        elif choice == '8':
            print("\nGenerating architecture recommendations...")
            arch_rec = generator.generate_architecture_recommendations(project, db)
            print("\n" + "="*60)
            print(arch_rec)
            print("="*60)
            print("\n✓ Architecture recommendations generated and saved!")

        elif choice == '9':
            print("\nGenerating user stories with acceptance criteria...")
            story_gen = UserStoryGenerator()
            user_stories = story_gen.generate_user_stories(project, db)

            if user_stories:
                print("\n" + "="*60)
                print(f"Generated {len(user_stories)} user stories")
                print("="*60)

                # Ask if user wants CSV export
                export_csv = input("\nExport user stories to CSV? (y/n): ").strip().lower()
                if export_csv == 'y':
                    csv_path = story_gen.export_to_csv(user_stories, project.name)
                    print(f"✓ Exported to CSV: {csv_path}")

                # Ask if user wants markdown export
                export_md = input("\nExport user stories to markdown? (y/n): ").strip().lower()
                if export_md == 'y':
                    md_path = story_gen.export_to_markdown(user_stories, project.name)
                    print(f"✓ Exported to markdown: {md_path}")

                print("\n✓ User stories generated and saved!")
            else:
                print("\n✗ Failed to generate user stories")

        elif choice == '10':
            print("\nGenerating all design artifacts...")
            print("This will take a few moments...\n")

            print("1/8 Generating architecture...")
            generator.generate_architecture(project, db)
            print("✓ Architecture complete")

            print("2/8 Generating data model...")
            generator.generate_data_model(project, db)
            print("✓ Data model complete")

            print("3/8 Generating API specification...")
            generator.generate_api_spec(project, db)
            print("✓ API specification complete")

            print("4/8 Generating technology stack...")
            generator.generate_tech_stack(project, db)
            print("✓ Technology stack complete")

            print("5/8 Generating implementation plan...")
            generator.generate_implementation_plan(project, db)
            print("✓ Implementation plan complete")

            print("6/8 Generating Mermaid diagrams...")
            generator.generate_diagrams(project, db)
            print("✓ Diagrams complete")

            print("7/8 Generating architecture recommendations...")
            generator.generate_architecture_recommendations(project, db)
            print("✓ Architecture recommendations complete")

            print("8/8 Generating user stories...")
            story_gen = UserStoryGenerator()
            user_stories = story_gen.generate_user_stories(project, db)
            if user_stories:
                story_gen.export_to_csv(user_stories, project.name)
                story_gen.export_to_markdown(user_stories, project.name)
            print("✓ User stories complete")

            print("\n✓ All design artifacts generated and saved!")

        elif choice == '11':
            return
        else:
            print("Invalid choice")
            return

        # Ask if user wants to export
        export_now = input("\nExport project with design to markdown? (y/n): ").strip().lower()
        if export_now == 'y':
            exporter = MarkdownExporter()
            filepath = exporter.export_project(project, db)
            print(f"\n✓ Exported to: {filepath}")

    except ValueError as e:
        print(f"\nError: {e}")
    except Exception as e:
        print(f"\nError generating design: {e}")
        import traceback
        traceback.print_exc()


def continue_existing_project(db):
    """Continue working on an existing project"""
    print("\n--- CONTINUE EXISTING PROJECT ---\n")

    project_id = input("Enter project ID: ").strip()
    if not project_id.isdigit():
        print("Error: Invalid project ID")
        return

    project = db.get_project(int(project_id))
    if not project:
        print(f"Error: Project with ID {project_id} not found")
        return

    print(f"\nProject: {project.name}")
    print(f"Description: {project.description}")
    print(f"Requirements: {len(project.requirements)}")
    print(f"Design Artifacts: {len(project.design_artifacts)}")

    print("\nWhat would you like to do?")
    print("1. Gather/re-gather requirements")
    print("2. Generate design")
    print("3. Export to markdown")
    print("4. Back to main menu")

    choice = input("\nChoice: ").strip()

    if choice == '1':
        # Clear existing requirements if any
        if project.requirements:
            confirm = input("\nThis will replace existing requirements. Continue? (y/n): ").strip().lower()
            if confirm != 'y':
                return
            for req in project.requirements:
                db.session.delete(req)
            db.session.commit()

        gather_requirements(db, project.id)
    elif choice == '2':
        generate_design_menu(db, project.id)
    elif choice == '3':
        exporter = MarkdownExporter()
        filepath = exporter.export_project(project, db)
        print(f"\n✓ Exported to: {filepath}")
    elif choice == '4':
        return
    else:
        print("Invalid choice")


def main():
    """Main application loop"""
    print_header()

    # Initialize database
    db = Database()

    try:
        while True:
            print_menu()
            choice = input("Enter your choice (1-6): ").strip()

            if choice == '1':
                create_new_project(db)
            elif choice == '2':
                continue_existing_project(db)
            elif choice == '3':
                list_projects(db)
            elif choice == '4':
                export_project(db)
            elif choice == '5':
                delete_project(db)
            elif choice == '6':
                print("\nGoodbye!\n")
                break
            else:
                print("\nInvalid choice. Please try again.")

    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Goodbye!\n")
    finally:
        db.close()


if __name__ == "__main__":
    main()
