import os
import io
import discord
from dotenv import load_dotenv
from PIL import Image
import pytesseract
import re

intents = discord.Intents(messages=True, message_content=True)


load_dotenv()
TOKEN = os.getenv('TOKEN')

intents = discord.Intents(messages=True, message_content=True) 
client = discord.Client(intents=intents)

# Define a function to evaluate expressions
def evaluate_expression(expression):
    try:
        # Remove any characters that are not numbers or the specified operators
        cleaned_expression = re.sub(r'[^0-9+\-*/]', '', expression)

        # Check if the cleaned expression is not empty
        if cleaned_expression:
            result = eval(cleaned_expression)
            return result
        else:
            return None
    except Exception as e:
        return str(e)

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('/upload'):
        attachments = message.attachments
        if len(attachments) > 0:
            attachment = attachments[0]
            img_data = await attachment.read()
            image = Image.open(io.BytesIO(img_data))
            text = pytesseract.image_to_string(image)

            # Check if the remaining text is a valid mathematical expression
            result = evaluate_expression(text)
            if result is not None:
                await message.channel.send(result)
            else:
                await message.channel.send("No valid mathematical expressions found in the image.")

    else:
        await message.channel.send("Please use /upload")

client.run(TOKEN)