import os
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import UploadFile

from mediator.upload.model import Upload, UploadSource, UploadStatus
from mediator.message.model import Message
from mediator.upload.parsers.whatsapp import WhatsAppParser

UPLOAD_DIR = os.path.join(os.getcwd(), "data", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

class UploadService:
    @staticmethod
    async def process_upload(
        db: AsyncSession, file: UploadFile, source: UploadSource, user_id: uuid.UUID | None = None
    ) -> Upload:
        # Create Upload DB record
        upload = Upload(
            user_id=user_id,
            source=source,
            status=UploadStatus.PARSING,
            file_path="",  # will update after save
        )
        db.add(upload)
        await db.commit()
        await db.refresh(upload)

        # Save file to disk
        file_ext = os.path.splitext(file.filename or "")[1]
        local_filename = f"{upload.id}{file_ext}"
        local_filepath = os.path.join(UPLOAD_DIR, local_filename)

        with open(local_filepath, "wb") as f:
            content = await file.read()
            f.write(content)

        upload.file_path = local_filepath
        await db.commit()

        # Parse messages
        parser = WhatsAppParser()
        batch_size = 1000
        messages_to_insert = []
        total_messages = 0

        try:
            for parsed_msg in parser.parse(local_filepath):
                msg = Message(
                    upload_id=upload.id,
                    timestamp=parsed_msg.timestamp,
                    sender=parsed_msg.sender,
                    content=parsed_msg.content,
                    is_media=parsed_msg.is_media
                )
                messages_to_insert.append(msg)
                total_messages += 1

                if len(messages_to_insert) >= batch_size:
                    db.add_all(messages_to_insert)
                    await db.commit()
                    messages_to_insert.clear()

            if messages_to_insert:
                db.add_all(messages_to_insert)
                await db.commit()

            upload.status = UploadStatus.COMPLETED
            upload.message_count = total_messages
            await db.commit()
            await db.refresh(upload)

        except Exception as e:
            upload.status = UploadStatus.FAILED
            await db.commit()
            raise e

        return upload
        
    @staticmethod
    async def get_upload_messages(db: AsyncSession, upload_id: uuid.UUID) -> list[Message]:
        stmt = select(Message).where(Message.upload_id == upload_id).order_by(Message.timestamp)
        result = await db.execute(stmt)
        return list(result.scalars().all())
