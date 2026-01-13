"""
Design generation module

Uses Claude to generate comprehensive system design artifacts based on
gathered requirements, including:
- System architecture
- Component designs
- Data models
- API specifications
- Technology stack recommendations
"""

import os
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()


class DesignGenerator:
    """Generates system design artifacts using Claude API"""

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

    def generate_complete_design(self, project, db):
        """Generate a complete system design with all artifacts"""

        # Reload project to get latest requirements
        project = db.get_project(project.id)

        if not project.requirements:
            raise ValueError("Cannot generate design: No requirements found for this project")

        requirements_text = self._format_requirements(project.requirements)

        print("\nGenerating comprehensive system design...")
        print("This may take a moment...\n")

        # Generate the complete design
        system_prompt = """You are an expert software architect and system designer. Your task is to create a comprehensive, professional system design based on the provided requirements.

Your design should be:
- Practical and implementable
- Well-structured and organized
- Technically sound
- Aligned with modern best practices
- Detailed enough for developers to implement

Format your response as a complete system design document in markdown."""

        user_prompt = f"""Create a comprehensive system design for the following project:

PROJECT: {project.name}
DESCRIPTION: {project.description}

{requirements_text}

Generate a complete system design document that includes:

1. SYSTEM ARCHITECTURE
   - High-level architecture overview
   - System components and their responsibilities
   - Component interactions and data flow
   - Architecture diagram description (in text/ASCII)

2. TECHNOLOGY STACK
   - Recommended technologies for each layer
   - Justification for technology choices
   - Alternative options considered

3. DATA MODEL
   - Database schema design
   - Entity relationships
   - Key data structures
   - Data flow and storage strategy

4. API DESIGN
   - API endpoints specification
   - Request/response formats
   - Authentication and authorization approach
   - API versioning strategy

5. COMPONENT SPECIFICATIONS
   - Detailed component breakdown
   - Key classes/modules and their responsibilities
   - Important algorithms or logic

6. SECURITY CONSIDERATIONS
   - Security measures and best practices
   - Data protection strategies
   - Authentication/authorization details

7. DEPLOYMENT ARCHITECTURE
   - Deployment model (cloud, on-premise, hybrid)
   - Infrastructure requirements
   - Scalability considerations
   - Monitoring and logging strategy

8. IMPLEMENTATION ROADMAP
   - Suggested phases for implementation
   - Key milestones
   - Dependencies between components

Provide a well-structured, detailed design document that a development team can use to implement the system."""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=8000,
            system=[
                {
                    "type": "text",
                    "text": system_prompt,
                    "cache_control": {"type": "ephemeral"}
                }
            ],
            messages=[{
                "role": "user",
                "content": user_prompt
            }]
        )

        design_content = response.content[0].text

        # Save the complete design as a single artifact
        db.add_design_artifact(
            project_id=project.id,
            artifact_type='complete_system_design',
            content=design_content
        )

        return design_content

    def generate_architecture(self, project, db):
        """Generate system architecture design"""

        project = db.get_project(project.id)

        if not project.requirements:
            raise ValueError("Cannot generate architecture: No requirements found")

        requirements_text = self._format_requirements(project.requirements)

        system_prompt = """You are an expert software architect. Create a detailed system architecture design based on the requirements provided."""

        user_prompt = f"""Design a system architecture for:

PROJECT: {project.name}
DESCRIPTION: {project.description}

{requirements_text}

Provide:
1. High-level architecture overview
2. System components and their responsibilities
3. Component interactions and communication patterns
4. Data flow between components
5. Architecture diagram description (text/ASCII format)
6. Design patterns to be used
7. Scalability and performance considerations

Format as a detailed architecture document."""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=4000,
            system=[
                {
                    "type": "text",
                    "text": system_prompt,
                    "cache_control": {"type": "ephemeral"}
                }
            ],
            messages=[{
                "role": "user",
                "content": user_prompt
            }]
        )

        architecture_content = response.content[0].text

        db.add_design_artifact(
            project_id=project.id,
            artifact_type='architecture',
            content=architecture_content
        )

        return architecture_content

    def generate_data_model(self, project, db):
        """Generate data model design"""

        project = db.get_project(project.id)

        if not project.requirements:
            raise ValueError("Cannot generate data model: No requirements found")

        requirements_text = self._format_requirements(project.requirements)

        system_prompt = """You are an expert database architect. Design a comprehensive data model based on the requirements."""

        user_prompt = f"""Design a data model for:

PROJECT: {project.name}
DESCRIPTION: {project.description}

{requirements_text}

Provide:
1. Entity-Relationship diagram (text/ASCII format)
2. Detailed table/collection schemas
3. Relationships and foreign keys
4. Indexes for performance
5. Data types and constraints
6. Sample data structures
7. Data validation rules

Format as a detailed data model specification."""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=4000,
            system=[
                {
                    "type": "text",
                    "text": system_prompt,
                    "cache_control": {"type": "ephemeral"}
                }
            ],
            messages=[{
                "role": "user",
                "content": user_prompt
            }]
        )

        data_model_content = response.content[0].text

        db.add_design_artifact(
            project_id=project.id,
            artifact_type='data_model',
            content=data_model_content
        )

        return data_model_content

    def generate_api_spec(self, project, db):
        """Generate API specification"""

        project = db.get_project(project.id)

        if not project.requirements:
            raise ValueError("Cannot generate API spec: No requirements found")

        requirements_text = self._format_requirements(project.requirements)

        system_prompt = """You are an expert API designer. Create a comprehensive API specification based on the requirements."""

        user_prompt = f"""Design an API specification for:

PROJECT: {project.name}
DESCRIPTION: {project.description}

{requirements_text}

Provide:
1. API endpoint listing with HTTP methods
2. Request/response formats (JSON examples)
3. Authentication and authorization mechanism
4. Error handling and status codes
5. Rate limiting and pagination strategies
6. API versioning approach
7. Example request/response for key endpoints

Format as a detailed API specification document."""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=4000,
            system=[
                {
                    "type": "text",
                    "text": system_prompt,
                    "cache_control": {"type": "ephemeral"}
                }
            ],
            messages=[{
                "role": "user",
                "content": user_prompt
            }]
        )

        api_spec_content = response.content[0].text

        db.add_design_artifact(
            project_id=project.id,
            artifact_type='api_specification',
            content=api_spec_content
        )

        return api_spec_content

    def generate_tech_stack(self, project, db):
        """Generate technology stack recommendations"""

        project = db.get_project(project.id)

        if not project.requirements:
            raise ValueError("Cannot generate tech stack: No requirements found")

        requirements_text = self._format_requirements(project.requirements)

        system_prompt = """You are an expert technology consultant. Recommend an appropriate technology stack based on the requirements."""

        user_prompt = f"""Recommend a technology stack for:

PROJECT: {project.name}
DESCRIPTION: {project.description}

{requirements_text}

Provide:
1. Frontend technologies and frameworks
2. Backend technologies and frameworks
3. Database recommendations
4. DevOps and deployment tools
5. Third-party services and APIs
6. Development tools and libraries
7. Justification for each choice
8. Alternative options considered

Format as a detailed technology stack recommendation."""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=3000,
            system=[
                {
                    "type": "text",
                    "text": system_prompt,
                    "cache_control": {"type": "ephemeral"}
                }
            ],
            messages=[{
                "role": "user",
                "content": user_prompt
            }]
        )

        tech_stack_content = response.content[0].text

        db.add_design_artifact(
            project_id=project.id,
            artifact_type='technology_stack',
            content=tech_stack_content
        )

        return tech_stack_content

    def generate_implementation_plan(self, project, db):
        """Generate implementation roadmap"""

        project = db.get_project(project.id)

        if not project.requirements:
            raise ValueError("Cannot generate implementation plan: No requirements found")

        requirements_text = self._format_requirements(project.requirements)

        system_prompt = """You are an expert project manager and technical lead. Create a practical implementation roadmap."""

        user_prompt = f"""Create an implementation plan for:

PROJECT: {project.name}
DESCRIPTION: {project.description}

{requirements_text}

Provide:
1. Implementation phases (MVP, Phase 2, Phase 3, etc.)
2. Features/components for each phase
3. Dependencies between components
4. Key milestones
5. Recommended team structure
6. Estimated complexity for each phase (High/Medium/Low)
7. Risks and mitigation strategies

Format as a detailed implementation roadmap."""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=3000,
            system=[
                {
                    "type": "text",
                    "text": system_prompt,
                    "cache_control": {"type": "ephemeral"}
                }
            ],
            messages=[{
                "role": "user",
                "content": user_prompt
            }]
        )

        implementation_plan_content = response.content[0].text

        db.add_design_artifact(
            project_id=project.id,
            artifact_type='implementation_plan',
            content=implementation_plan_content
        )

        return implementation_plan_content

    def generate_diagrams(self, project, db):
        """Generate Mermaid diagrams for the system"""

        project = db.get_project(project.id)

        if not project.requirements:
            raise ValueError("Cannot generate diagrams: No requirements found")

        requirements_text = self._format_requirements(project.requirements)

        system_prompt = """You are an expert system architect. Create comprehensive Mermaid diagrams to visualize the system design.

Mermaid is a markdown-based diagramming language. Use proper Mermaid syntax for all diagrams."""

        user_prompt = f"""Create Mermaid diagrams for:

PROJECT: {project.name}
DESCRIPTION: {project.description}

{requirements_text}

Generate the following diagrams in Mermaid format:

1. **System Architecture Diagram** (C4 or component diagram)
   - Show main system components
   - Show data flow between components
   - Include external systems/APIs

2. **Entity Relationship Diagram (ERD)**
   - Show database entities
   - Show relationships and cardinality
   - Include key attributes

3. **Sequence Diagram** (for main user flow)
   - Show interaction between components
   - Show key processes/workflows

4. **Deployment Diagram**
   - Show infrastructure components
   - Show deployment architecture

For each diagram:
- Provide a clear title and description
- Use proper Mermaid syntax
- Make it detailed and accurate
- Add comments where helpful

Format your response with each diagram clearly labeled and separated."""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=4000,
            system=[
                {
                    "type": "text",
                    "text": system_prompt,
                    "cache_control": {"type": "ephemeral"}
                }
            ],
            messages=[{
                "role": "user",
                "content": user_prompt
            }]
        )

        diagrams_content = response.content[0].text

        db.add_design_artifact(
            project_id=project.id,
            artifact_type='mermaid_diagrams',
            content=diagrams_content
        )

        return diagrams_content

    def generate_architecture_recommendations(self, project, db):
        """Generate detailed architecture recommendations and patterns"""

        project = db.get_project(project.id)

        if not project.requirements:
            raise ValueError("Cannot generate architecture recommendations: No requirements found")

        requirements_text = self._format_requirements(project.requirements)

        system_prompt = """You are a senior software architect with expertise in system design patterns, cloud architecture, and best practices. Provide detailed, actionable architecture recommendations."""

        user_prompt = f"""Provide comprehensive architecture recommendations for:

PROJECT: {project.name}
DESCRIPTION: {project.description}

{requirements_text}

Provide detailed recommendations covering:

1. **ARCHITECTURE PATTERNS**
   - Recommended architectural style (microservices, monolith, serverless, etc.)
   - Design patterns to use (MVC, MVVM, Repository, etc.)
   - Justification for each choice

2. **LAYERING STRATEGY**
   - Presentation layer approach
   - Business logic layer design
   - Data access layer strategy
   - Cross-cutting concerns (logging, auth, etc.)

3. **SCALABILITY APPROACH**
   - Horizontal vs vertical scaling strategy
   - Caching strategy (where and what)
   - Load balancing recommendations
   - Database scaling approach

4. **RESILIENCE & RELIABILITY**
   - Fault tolerance mechanisms
   - Circuit breaker patterns
   - Retry policies
   - Disaster recovery approach

5. **PERFORMANCE OPTIMIZATION**
   - Performance bottleneck mitigation
   - Database query optimization strategies
   - Caching layers
   - CDN usage

6. **SECURITY ARCHITECTURE**
   - Authentication/authorization strategy
   - Data encryption (at rest and in transit)
   - API security (rate limiting, API keys, OAuth)
   - Security best practices

7. **INTEGRATION PATTERNS**
   - How to integrate with external systems
   - API gateway usage
   - Message queues/event bus
   - Data synchronization strategies

8. **MONITORING & OBSERVABILITY**
   - Logging strategy and tools
   - Metrics and monitoring
   - Distributed tracing
   - Alerting strategy

9. **CLOUD ARCHITECTURE** (if applicable)
   - Cloud provider recommendations
   - Specific cloud services to use
   - Multi-cloud vs single-cloud
   - Cost optimization strategies

10. **TRADE-OFFS & DECISIONS**
    - Key architectural decisions
    - Trade-offs considered
    - Why certain approaches were chosen over alternatives

Provide specific, actionable recommendations with clear reasoning."""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=6000,
            system=[
                {
                    "type": "text",
                    "text": system_prompt,
                    "cache_control": {"type": "ephemeral"}
                }
            ],
            messages=[{
                "role": "user",
                "content": user_prompt
            }]
        )

        arch_rec_content = response.content[0].text

        db.add_design_artifact(
            project_id=project.id,
            artifact_type='architecture_recommendations',
            content=arch_rec_content
        )

        return arch_rec_content
