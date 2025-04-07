import os
import json
from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
from docx import Document
from docx.shared import Pt


class MyCustomToolInput(BaseModel):
    """Input schema for MyCustomTool."""
    argument: str = Field(..., description="Description of the argument.")

class MyCustomTool(BaseTool):
    name: str = "Name of my tool"
    description: str = (
        "Clear description for what this tool is useful for, your agent will need this information to use it."
    )
    args_schema: Type[BaseModel] = MyCustomToolInput

    def _run(self, argument: str) -> str:
        # Implementation goes here
        return "this is an example of a tool output, ignore it and move along."

# ========== WordExtractorTool ==========
class WordExtractorInput(BaseModel):
    file_path: str = Field(..., description="Chemin vers le document Word source (.docx)")


class WordExtractorTool(BaseTool):
    name: str = "WordExtractorTool"
    description: str = "Lit le contenu texte d'un document Word (.docx) et retourne le texte brut."
    args_schema: Type[BaseModel] = WordExtractorInput

    def _run(self, file_path: str) -> str:
        if not os.path.exists(file_path):
            return "⚠️ Le fichier spécifié est introuvable."

        doc = Document(file_path)
        text = "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
        return text

# ========== FalcDocxWriterTool ==========
class FalcDocxWriterInput(BaseModel):
    """Input schema for FalcDocxWriterTool."""
    markdown_text: str = Field(..., description="FALC markdown text to convert into a formatted DOCX document.")


class FalcDocxWriterTool(BaseTool):
    name: str = "FalcDocxWriterTool"
    description: str = (
        "Converts a markdown FALC text into a properly formatted .docx Word document using Arial font, spacing rules, and one sentence per line."
    )
    args_schema: Type[BaseModel] = FalcDocxWriterInput

    def _run(self, markdown_text: str) -> str:
        document = Document()

        # Default style
        style = document.styles['Normal']
        font = style.font
        font.name = 'Arial'
        font.size = Pt(10)

        for line in markdown_text.split("\n"):
            if not line.strip():
                continue
            p = document.add_paragraph(line.strip())
            p.paragraph_format.space_after = Pt(10)
            p.paragraph_format.line_spacing = 1.5

        output_path = "output/falc_translated_output.docx"
        os.makedirs("output", exist_ok=True)
        document.save(output_path)

        return f"Document Word FALC generated at: {output_path}"


# ========== FalcIconInjectorTool ==========
class FalcIconInjectorInput(BaseModel):
    """Input schema for FalcIconInjectorTool."""
    markdown_text: str = Field(..., description="FALC markdown text to enhance by injecting icons based on keyword mapping.")


class FalcIconInjectorTool(BaseTool):
    name: str = "FalcIconInjectorTool"
    description: str = (
        "Scans a markdown text and inserts appropriate FALC icons (emojis or symbols) based on a keyword-to-icon map in knowledge/icons.json."
    )
    args_schema: Type[BaseModel] = FalcIconInjectorInput

    def _run(self, markdown_text: str) -> str:
        icons_path = os.path.join("knowledge", "icons.json")
        if not os.path.exists(icons_path):
            return "⚠️ Error: icons.json file not found in the 'knowledge/' directory."

        with open(icons_path, "r", encoding="utf-8") as f:
            icon_map = json.load(f)

        for keyword, icon in icon_map.items():
            markdown_text = markdown_text.replace(keyword, f"{icon} {keyword}")

        return markdown_text
