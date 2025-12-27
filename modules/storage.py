from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime, timezone
import os

Base = declarative_base()


class Project(Base):
    __tablename__ = 'projects'

    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    requirements = relationship('Requirement', back_populates='project', cascade='all, delete-orphan')
    design_artifacts = relationship('DesignArtifact', back_populates='project', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Project(id={self.id}, name='{self.name}')>"


class Requirement(Base):
    __tablename__ = 'requirements'

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    category = Column(String(50), nullable=False)  # 'functional', 'non_functional', 'constraint'
    description = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    project = relationship('Project', back_populates='requirements')

    def __repr__(self):
        return f"<Requirement(id={self.id}, category='{self.category}')>"


class DesignArtifact(Base):
    __tablename__ = 'design_artifacts'

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    artifact_type = Column(String(50), nullable=False)  # 'architecture', 'component', 'data_model', etc.
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    project = relationship('Project', back_populates='design_artifacts')

    def __repr__(self):
        return f"<DesignArtifact(id={self.id}, type='{self.artifact_type}')>"


class Database:
    """Database manager for the project planner"""

    def __init__(self, db_path='data/projects.db'):
        # Create data directory if it doesn't exist
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

        # Create engine and session
        self.engine = create_engine(f'sqlite:///{db_path}')
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def create_project(self, name, description):
        """Create a new project"""
        project = Project(name=name, description=description)
        self.session.add(project)
        self.session.commit()
        return project

    def get_project(self, project_id):
        """Get a project by ID"""
        return self.session.query(Project).filter_by(id=project_id).first()

    def get_all_projects(self):
        """Get all projects"""
        return self.session.query(Project).all()

    def add_requirement(self, project_id, category, description):
        """Add a requirement to a project"""
        requirement = Requirement(
            project_id=project_id,
            category=category,
            description=description
        )
        self.session.add(requirement)
        self.session.commit()
        return requirement

    def add_design_artifact(self, project_id, artifact_type, content):
        """Add a design artifact to a project"""
        artifact = DesignArtifact(
            project_id=project_id,
            artifact_type=artifact_type,
            content=content
        )
        self.session.add(artifact)
        self.session.commit()
        return artifact

    def delete_project(self, project_id):
        """Delete a project and all its related data"""
        project = self.get_project(project_id)
        if project:
            self.session.delete(project)
            self.session.commit()
            return True
        return False

    def close(self):
        """Close the database session"""
        self.session.close()
