import os
import io
import discord
from dotenv import load_dotenv
from PIL import Image
import pytesseract
import re

load_dotenv()
TOKEN = os.getenv('TOKEN')

intents = discord.Intents(messages=True, message_content=True) 
client = discord.Client(intents=intents)

# Define a function to evaluate expressions following BEDMAS
def evaluate_expression(expression):
    operators = {'+': (1, lambda x, y: x + y), '-': (1, lambda x, y: x - y),
                 '*': (2, lambda x, y: x * y), '/': (2, lambda x, y: x / y)}

    def apply_operator(operators, values, operator):
        while values[-1] in operators and operators[values[-1]][0] >= operators[operator][0]:
            operator_fn = operators[values.pop()]
            right = values.pop()
            left = values.pop()
            values.append(operator_fn[1](left, right))
        values.append(operator)

    values = []
    operators_stack = []
    for token in re.findall(r'[+\-*/()]|\d+', expression):
        if token.isnumeric() or (token[0] == '-' and token[1:].isnumeric()):
            values.append(float(token))
        elif token in operators:
            apply_operator(operators, values, token)
        elif token == '(':
            operators_stack.append(token)
        elif token == ')':
            while operators_stack[-1] != '(':
                apply_operator(operators, values, operators_stack[-1])
                operators_stack.pop()
            operators_stack.pop()

    while operators_stack:
        apply_operator(operators, values, operators_stack[-1])
        operators_stack.pop()

    return values[0]

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

            # Remove the equal sign and any leading/trailing whitespace
            text = text.replace("=", "").strip()

            # Check if the remaining text is a valid mathematical expression
            try:
                result = evaluate_expression(text)
                await message.channel.send(result)
            except Exception as e:
                await message.channel.send(f"Invalid expression: {e}")

    else:
        await message.channel.send("Please use /upload")

client.run(TOKEN)
