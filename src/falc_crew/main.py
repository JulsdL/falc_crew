#!/usr/bin/env python
import sys
import os
import warnings

from datetime import datetime

from falc_crew.crew import FalcCrew
from falc_crew.tools.custom_tool import WordExtractorTool

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information

def run(file_path: str):
    """
    Run the crew.
    """
    print(f"📄 Lecture du fichier source : {file_path}")
    extractor = WordExtractorTool()
    text = extractor._run(file_path)

    print("🚀 Lancement du crew avec le contenu extrait...")
    inputs = {
        "original_text": text,
        "source_filename": os.path.basename(file_path)
    }

    try:
        FalcCrew().crew().kickoff(inputs=inputs)
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
