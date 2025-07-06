
import torch
from transformers import DonutProcessor, VisionEncoderDecoderModel
from PIL import Image
from io import BytesIO
import requests

from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

BOT_TOKEN = 'YOUR_BOT_TOKEN_HERE'

# Load Donut model and processor
processor = DonutProcessor.from_pretrained("naver-clova-ix/donut-base-finetuned-docvqa")
model = VisionEncoderDecoderModel.from_pretrained("naver-clova-ix/donut-base-finetuned-docvqa")

device = "cuda" if torch.cuda.is_available() else "cpu"
model.to(device)

# Predefined prompt for CoC-like structure
prompt = "<s_docvqa><s_question>Describe this Clash of Clans account profile</s_question><s_answer>"

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = await update.message.photo[-1].get_file()
    image_data = requests.get(file.file_path).content
    image = Image.open(BytesIO(image_data)).convert("RGB")

    pixel_values = processor(images=image, return_tensors="pt").pixel_values.to(device)

    decoder_input_ids = processor.tokenizer(prompt, add_special_tokens=False, return_tensors="pt")["input_ids"]
    decoder_input_ids = decoder_input_ids.to(device)

    outputs = model.generate(
        pixel_values,
        decoder_input_ids=decoder_input_ids,
        max_length=512,
        early_stopping=True,
        pad_token_id=processor.tokenizer.pad_token_id,
        eos_token_id=processor.tokenizer.eos_token_id,
        use_cache=True,
        num_beams=4,
        bad_words_ids=[[processor.tokenizer.unk_token_id]]
    )

    result = processor.batch_decode(outputs, skip_special_tokens=True)[0]
    await update.message.reply_text(f"📸 *Detected Title:*\n{result}", parse_mode="Markdown")

if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.run_polling()
