import chainlit as cl
import os
import uuid
import asyncio
from falc_crew.main import run

@cl.on_chat_start
async def on_chat_start():

    # 🔐 Generate a session-unique UUID
    if not cl.user_session.get("session_id"):
        cl.user_session.set("session_id", str(uuid.uuid4()))

    session_id = cl.user_session.get("session_id")

    # Session-based isolation
    upload_dir = os.path.join("temp_uploads", session_id)
    output_dir = os.path.join("output", session_id)
    os.makedirs(upload_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)

    # Prompt the user to upload a Word (.docx) file using AskFileMessage.
    files = await cl.AskFileMessage(
        content="Veuillez charger un document Word (.docx) contenant le texte à traduire pour commencer !",
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
    new_file_path = os.path.join(upload_dir, file_name)

    # Copy the uploaded file from its temporary location to our designated folder.
    with open(uploaded_file.path, "rb") as src, open(new_file_path, "wb") as dst:
        dst.write(src.read())

    # Inform the user that processing has started.
    await cl.Message(
        content="Traitement en cours, veuillez patienter (~30secondes)..."
    ).send()

    # Offload the CrewAI pipeline execution to a background thread.
    try:
        await asyncio.to_thread(run, file_path=new_file_path, output_dir=output_dir)
    except Exception as e:
        await cl.Message(
            content=f"❌ Erreur lors de l'exécution du pipeline : {e}"
        ).send()
        return

    # Look for most recent output file for the current session id
    if not os.path.exists(output_dir):
        await cl.Message(content="❌ Aucun document généré trouvé pour votre session.").send()
        return

    all_docx_files = [
        f for f in os.listdir(output_dir)
        if f.lower().endswith(".docx")
    ]

    if not all_docx_files:
        await cl.Message(content="❌ Aucun document Word de sortie trouvé.").send()
        return

    latest_file = sorted(
        all_docx_files,
        key=lambda x: os.path.getmtime(os.path.join(output_dir, x)),
        reverse=True
    )[0]

    output_path = os.path.join(output_dir, latest_file)
    with open(output_path, "rb") as doc:
        doc_bytes = doc.read()

    file_element = cl.File(
        name=latest_file,
        content=doc_bytes,
        display="inline"
    )
    await cl.Message(
        content=f"✅ Voici votre document FALC généré : **{latest_file}**.",
        elements=[file_element]
    ).send()
