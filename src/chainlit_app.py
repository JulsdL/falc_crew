import chainlit as cl
import os
import uuid
import shutil
import asyncio
from falc_crew.main import run


# 🔄 Shared logic for uploading, processing, and delivering output
async def process_upload():
    session_id = cl.user_session.get("session_id")
    upload_dir = cl.user_session.get("upload_dir")
    output_dir = cl.user_session.get("output_dir")

    # Prompt upload
    files = await cl.AskFileMessage(
        content="📄 Veuillez charger un nouveau document Word (.docx) à traduire.",
        accept={"application/vnd.openxmlformats-officedocument.wordprocessingml.document": [".docx"]},
        max_files=1,
        timeout=300,
        raise_on_timeout=False
    ).send()

    if not files:
        await cl.Message(content="⏳ Aucun fichier reçu. Réessayez.").send()
        return

    uploaded_file = files[0]
    file_name = uploaded_file.name
    new_file_path = os.path.join(upload_dir, file_name)

    with open(uploaded_file.path, "rb") as src, open(new_file_path, "wb") as dst:
        dst.write(src.read())

    await cl.Message(content=f"📝 Fichier reçu : **{file_name}**\n⏳ Traitement en cours (~1 minute)...").send()

    try:
        # await asyncio.to_thread(run, file_path=new_file_path, output_dir=output_dir)
        await run(file_path=new_file_path, output_dir=output_dir)
    except Exception as e:
        await cl.Message(content=f"❌ Erreur durant le traitement : {e}").send()
        return

    docx_files = [f for f in os.listdir(output_dir) if f.endswith(".docx")]
    if not docx_files:
        await cl.Message(content="❌ Aucun document généré trouvé.").send()
        return

    latest_file = sorted(
        docx_files,
        key=lambda x: os.path.getmtime(os.path.join(output_dir, x)),
        reverse=True
    )[0]

    output_path = os.path.join(output_dir, latest_file)
    with open(output_path, "rb") as doc:
        doc_bytes = doc.read()

    file_element = cl.File(name=latest_file, content=doc_bytes, display="inline")
    await cl.Message(
        content=f"✅ Document FALC généré, cliquez pour télécharger : **{latest_file}**.",
        elements=[file_element]
    ).send()

    # ✨ Immediately re-prompt for next upload
    await process_upload()


# 👋 First-time user session start
@cl.on_chat_start
async def on_chat_start():
    # Generate per-session UUID
    if not cl.user_session.get("session_id"):
        cl.user_session.set("session_id", str(uuid.uuid4()))

    session_id = cl.user_session.get("session_id")
    upload_dir = os.path.join("temp_uploads", session_id)
    output_dir = os.path.join("output", session_id)
    os.makedirs(upload_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)

    cl.user_session.set("upload_dir", upload_dir)
    cl.user_session.set("output_dir", output_dir)

    await cl.Message(content="👋 Bienvenue ! Ce service traduit vos documents Word (.docx) en FALC.").send()
    await process_upload()


# 🔁 User types anything → re-prompt for upload
@cl.on_message
async def on_message(message: cl.Message):
    await process_upload()


# 🧹 Cleanup after disconnect
@cl.on_chat_end
def end():
    try:
        for dir_path in [
            cl.user_session.get("upload_dir"),
            cl.user_session.get("output_dir")
        ]:
            if dir_path and os.path.exists(dir_path):
                shutil.rmtree(dir_path)
                print(f"🧹 Cleaned: {dir_path}")
    except Exception as e:
        print(f"⚠️ Cleanup error: {e}")
