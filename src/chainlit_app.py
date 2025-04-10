import chainlit as cl
import os
import asyncio
from falc_crew.main import run

@cl.on_chat_start
async def on_chat_start():
    # Prompt the user to upload a Word (.docx) file using AskFileMessage.
    files = await cl.AskFileMessage(
        content="Veuillez charger un document Word (.docx) pour commencer !",
        accept={"application/vnd.openxmlformats-officedocument.wordprocessingml.document": [".docx"]},
        max_files=1,
        timeout=60,
        raise_on_timeout=False
    ).send()

    if not files or len(files) == 0:
        await cl.Message(
            content="Temps écoulé sans chargement de fichier. Veuillez réessayer."
        ).send()
        return

    # Take the first uploaded file.
    uploaded_file = files[0]
    file_name = uploaded_file.name

    # Ensure the temporary uploads directory exists.
    os.makedirs("temp_uploads", exist_ok=True)
    new_file_path = os.path.join("temp_uploads", file_name)

    # Copy the uploaded file from its temporary location to our designated folder.
    with open(uploaded_file.path, "rb") as src, open(new_file_path, "wb") as dst:
        dst.write(src.read())

    # Inform the user that processing has started.
    await cl.Message(
        content="Traitement en cours, veuillez patienter..."
    ).send()

    # Offload the CrewAI pipeline execution to a background thread.
    try:
        await asyncio.to_thread(run, file_path=new_file_path)
    except Exception as e:
        await cl.Message(
            content=f"❌ Erreur lors de l'exécution du pipeline : {e}"
        ).send()
        return

    # After running the pipeline, check for the output file.
    output_docx = "output/falc_translated_output.docx"
    if os.path.exists(output_docx):
        with open(output_docx, "rb") as doc:
            doc_bytes = doc.read()

        # Create a File element to let the user download the document.
        file_element = cl.File(
            name="falc_translated_output.docx",
            content=doc_bytes,
            display="inline"
        )
        await cl.Message(
            content="✅ Voici le document FALC généré. Vous pouvez le télécharger ci-dessous.",
            elements=[file_element]
        ).send()
    else:
        await cl.Message(
            content="❌ Le document final n'a pas été trouvé."
        ).send()
