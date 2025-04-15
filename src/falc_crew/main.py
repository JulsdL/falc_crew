#!/usr/bin/env python
import sys
import os
import warnings
import json
from datetime import datetime
from docx import Document

from falc_crew.crew import FalcCrew
from falc_crew.tools.custom_tool import WordExtractorTool, FalcIconLookupTool, FalcDocxStructureTaggerTool

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information

import chainlit as cl

@cl.step(name="📄 Lecture du document Word")
async def extract_text(file_path):
    extractor = WordExtractorTool()
    return extractor._run(file_path)

@cl.step(name="🔍 Analyse de la structure du document")
async def tag_structure(doc_path):
    doc = Document(doc_path)
    paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
    tagger = FalcDocxStructureTaggerTool()
    return tagger._run(paragraphs)

@cl.step(name="🔎 Chargement des icônes disponibles")
async def load_icon_list():
    return FalcIconLookupTool()._run()

async def run(file_path: str, output_dir: str):
    print(f"📄 Lecture du fichier source : {file_path}")

    text = await extract_text(file_path)
    tag_response = await tag_structure(file_path)

    try:
        tag_data = json.loads(tag_response)
        subject_index = tag_data.get("subject", [])[0]
        body_indexes = tag_data.get("body", [])
    except Exception as e:
        raise Exception(f"❌ Failed to parse structure tagging response: {tag_response}") from e

    icon_list = await load_icon_list()

    inputs = {
        "original_text": text,
        "source_filename": os.path.basename(file_path),
        "original_doc_path": file_path,
        "subject_index": subject_index,
        "body_indexes": body_indexes,
        "icon_list": icon_list,
        "output_dir": output_dir,
    }

    @cl.step(name="📄 Traduction FALC en cours...")
    async def kickoff_crew(inputs):
        async with cl.Step(name="📄 Lancement", type="system") as step:
            step.input = "Texte prêt pour la traduction"
            step.output = "Analyse en cours..."

        return await FalcCrew().crew().kickoff_async(inputs=inputs)

    try:
        # await FalcCrew().crew().kickoff_async(inputs=inputs)
        await kickoff_crew(inputs)
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")




def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {
        "topic": "AI LLMs",
        "current_year": str(datetime.now().year)
    }
    try:
        FalcCrew().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        FalcCrew().crew().replay(task_id=sys.argv[1])

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")

def test():
    """
    Test the crew execution and returns the results.
    """
    inputs = {
        "topic": "AI LLMs",
        "current_year": str(datetime.now().year)
    }
    try:
        FalcCrew().crew().test(n_iterations=int(sys.argv[1]), openai_model_name=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")


if __name__ == "__main__":
    run()

    # Inspect entity memory
    from falc_crew.crew import FalcCrew
    crew_instance = FalcCrew()
    agent = crew_instance.falc_translator()

    if agent.entity_memory:
        print("🧠 ENTITÉS MÉMORISÉES")
        for key, value in agent.entity_memory.store.items():
            print(f"{key}: {value}")
