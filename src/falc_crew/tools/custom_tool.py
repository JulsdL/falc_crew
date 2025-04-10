import os
import json
from crewai.tools import BaseTool
from crewai_tools import RagTool
from typing import List, Optional, Type
from pydantic import BaseModel, Field
from typing import Dict, Any
from docx import Document
from docx.shared import Pt


# class MyCustomToolInput(BaseModel):
#     """Input schema for MyCustomTool."""
#     argument: str = Field(..., description="Description of the argument.")

# class MyCustomTool(BaseTool):
#     name: str = "Name of my tool"
#     description: str = (
#         "Clear description for what this tool is useful for, your agent will need this information to use it."
#     )
#     args_schema: Type[BaseModel] = MyCustomToolInput

#     def _run(self, argument: str) -> str:
#         # Implementation goes here
#         return "this is an example of a tool output, ignore it and move along."

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
    header: Optional[str] = Field(None, description="Header block for the letter, typically sender info")
    recipient: Optional[str] = Field(None, description="Recipient block, usually address and name")
    subject: Optional[str] = Field(None, description="Subject line of the letter")
    body_sections: List[str] = Field(..., description="List of paragraphs or markdown strings to be rendered")
    footer: Optional[str] = Field(None, description="Final line or sign-off")
    markdown_text: Optional[str] = Field(None, description="Fallback full markdown text")


class FalcDocxWriterTool(BaseTool):
    name: str = "FalcDocxWriterTool"
    description: str = (
        "Generate a structured FALC Word letter layout with optional header, subject, recipient and footer"
    )
    args_schema: Type[BaseModel] = FalcDocxWriterInput

    def _run(self, header=None, recipient=None, subject=None, body_sections=None, footer=None, markdown_text=None) -> str:
        document = Document()

        # Style config
        style = document.styles['Normal']
        font = style.font
        font.name = 'Arial'
        font.size = Pt(10)

        # Add header and recipient as table
        if header or recipient:
            table = document.add_table(rows=1, cols=2)
            table.autofit = False
            hdr_cell, rcpt_cell = table.rows[0].cells
            if header:
                hdr_cell.text = header
            if recipient:
                rcpt_cell.text = recipient
            document.add_paragraph("")  # Spacer

        # Subject
        if subject:
            subject_paragraph = document.add_paragraph(subject)
            subject_paragraph.style = 'Heading 2'

        # Body content
        if body_sections:
            for section in body_sections:
                clean = section.strip()
                if not clean:
                    continue
                if clean.startswith("##"):
                    heading = clean.replace("##", "").strip()
                    document.add_paragraph(heading, style='Heading 3')
                else:
                    paragraph = document.add_paragraph(clean)
                    paragraph.paragraph_format.space_after = Pt(10)
                    paragraph.paragraph_format.line_spacing = 1.5

        if not body_sections and markdown_text:
            body_sections = markdown_text.splitlines()

        # Footer
        if footer:
            document.add_paragraph("\n" + footer)

        # Save output
        output_path = "output/falc_translated_output.docx"
        os.makedirs("output", exist_ok=True)
        document.save(output_path)
        return f"✅ FALC document generated: {output_path}"



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


# ========== ReferenceModelRetrieverTool ==========

class ReferenceModelRetrieverInput(BaseModel):
    query: str = Field(..., description="Query to search for a similar FALC translation model.")

class ReferenceModelRetrieverTool(RagTool):
    name: str = "ReferenceModelRetriever"
    description: str = (
        "Use this tool to search a bank of reference FALC translations "
        "and find similar documents based on your input."
    )
    args_schema: Type[BaseModel] = ReferenceModelRetrieverInput
