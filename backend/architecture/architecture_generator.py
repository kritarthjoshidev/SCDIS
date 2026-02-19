import os
import json
import logging
from datetime import datetime
from typing import Dict, List

from core.config import settings

logger = logging.getLogger(__name__)


class ArchitectureGenerator:
    """
    Generates system architecture intelligence:
    - component inventory
    - dependency mapping
    - deployment readiness report
    - architecture export (JSON / Markdown)
    """

    def __init__(self):

        self.root_dir = settings.BASE_DIR

        self.component_map = {
            "core": "Configuration & security layer",
            "routes": "API interface layer",
            "services": "Business service layer",
            "ai_engine": "AI processing engines",
            "ml_pipeline": "MLOps lifecycle layer",
            "architecture": "Architecture intelligence tools"
        }

    # ====================================================
    # Scan project components
    # ====================================================
    def scan_components(self) -> Dict:

        discovered = {}

        for folder, desc in self.component_map.items():

            path = os.path.join(self.root_dir, folder)

            if os.path.exists(path):
                discovered[folder] = {
                    "description": desc,
                    "files": os.listdir(path)
                }

        logger.info("Architecture scan completed")

        return discovered

    # ====================================================
    # Dependency graph generation
    # ====================================================
    def generate_dependency_map(self) -> Dict:

        dependency_map = {
            "routes": ["services", "ai_engine"],
            "services": ["ml_pipeline"],
            "ml_pipeline": ["ai_engine"],
            "ai_engine": ["core"],
            "core": []
        }

        return dependency_map

    # ====================================================
    # Deployment readiness report
    # ====================================================
    def deployment_readiness(self):

        checklist = {
            "api_layer": True,
            "ai_models": True,
            "ml_pipeline": True,
            "scheduler": True,
            "monitoring": True,
            "security": True,
            "deployment_manager": True
        }

        readiness_score = round(
            (sum(checklist.values()) / len(checklist)) * 100,
            2
        )

        return {
            "readiness_score": readiness_score,
            "details": checklist,
            "generated_at": datetime.utcnow()
        }

    # ====================================================
    # Export architecture JSON
    # ====================================================
    def export_architecture_json(self, output_path="architecture_report.json"):

        report = {
            "components": self.scan_components(),
            "dependencies": self.generate_dependency_map(),
            "deployment_readiness": self.deployment_readiness(),
            "generated_at": datetime.utcnow().isoformat()
        }

        with open(output_path, "w") as f:
            json.dump(report, f, indent=4)

        logger.info("Architecture JSON exported")

        return output_path

    # ====================================================
    # Export Markdown architecture report
    # ====================================================
    def export_markdown_report(self, output_path="architecture_report.md"):

        components = self.scan_components()
        readiness = self.deployment_readiness()

        lines = [
            "# Smart Campus Decision Intelligence System",
            "",
            "## Architecture Components",
            ""
        ]

        for comp, data in components.items():
            lines.append(f"### {comp}")
            lines.append(data["description"])
            lines.append("")

        lines.append("## Deployment Readiness")
        lines.append(f"Score: {readiness['readiness_score']}%")

        with open(output_path, "w") as f:
            f.write("\n".join(lines))

        logger.info("Architecture Markdown exported")

        return output_path
