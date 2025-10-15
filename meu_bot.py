import asyncio
import random
import re
import os
from dotenv import load_dotenv
from telethon import TelegramClient, events 
from asyncio.exceptions import TimeoutError
from telethon.tl.types import Message

API_ID = os.environ.get('API_ID') 
API_HASH = os.environ.get('API_HASH')

TARGET_CHAT = '@tricklandbot'

SESSION_FILE = 'data/userbot_session'

COMMAND_TO_SEND = "🎯 Mirar"  
STOP_PHRASES = ["Oh, não! Você não possui mais dardos."]

LOOP_DELAY_SECONDS = 0.5       
RESPONSE_TIMEOUT_SECONDS = 2 
PAUSE_AFTER_CLICK_SECONDS = 0.8

PRIMARY_PREFERENCES = [
    "triples", "artms", "red velvet", "exo", "enhypen",
    "p1harmony", "babymonster", "seventeen", "txt", "riize", "bts", "nct",
    "aespa", "cortis", "the boyz", "stray kids"
]

SECONDARY_PREFERENCES = [
    "ive", "idid", "alpha drive one", "tws", "monsta x", "boynextdoor", "le sserafim",
    "solistas de k-pop/k-hiphop", "ampers&one", "&team", "zerobaseone", "kickflip",
    "grupos de k-pop/j-pop", "katseye", "one pact", "blackpink", "njz"
]

TRIGGER_PHRASES = ["Escolha uma subcategoria:"]

REFRESH_BUTTON_TEXT = "🔄"
MAX_REFRESH_ATTEMPTS = 2

client = TelegramClient(SESSION_FILE, API_ID, API_HASH)

def parse_message_and_map_buttons(message):

    if not isinstance(message, Message) or not message.text or not message.buttons: return []

    all_buttons = [btn for row in message.buttons for btn in row]
    button_map_by_text = {btn.text: btn for btn in all_buttons}
    mapped_options = []
    lines = message.text.splitlines()

    for line in lines:
        match = re.match(r"^\s*(\S+)\s*[—\-–]\s*(.+)$", line.strip())

        if match:
            emoji = match.group(1).strip()
            name = match.group(2).strip().lower().strip('*_`')
           
            if emoji in button_map_by_text:
                button_obj = button_map_by_text[emoji]
                mapped_options.append({'name': name, 'button_obj': button_obj})

                #print(f"    Texto: '{name}' -> Botão: '{emoji}'")

    if not mapped_options: print("    Não foi possível mapear nenhum nome aos botões.")
    return mapped_options

async def main():

    if not TARGET_CHAT:
        return

    await client.start()

    round_counter = 1

    while True:
        #print(f"\nRodada: {round_counter}")
        choice_made = False

        try:
            current_message = None

            async with client.conversation(TARGET_CHAT, timeout=RESPONSE_TIMEOUT_SECONDS) as conv:
                await conv.send_message(COMMAND_TO_SEND)
                current_message = await conv.get_response()

            if any(phrase.lower() in current_message.text.lower() for phrase in STOP_PHRASES):
                print("Ending loop")
                break

            for attempt in range(MAX_REFRESH_ATTEMPTS + 1):
                #print(f"\nAttempt: {attempt + 1}/{MAX_REFRESH_ATTEMPTS + 1}")

                mapped_options = parse_message_and_map_buttons(current_message)

                for pref_list in [PRIMARY_PREFERENCES, SECONDARY_PREFERENCES]:
                    for preference in pref_list:
                        for option in mapped_options:
                            if preference == option['name']:
                                print(f"Preference: '{preference}'")
                                await option['button_obj'].click()
                                choice_made = True
                                break

                        if choice_made: break
                    if choice_made: break

                if choice_made:
                    #print("Success")
                    break

                if attempt < MAX_REFRESH_ATTEMPTS:
                    #print(f"No preferences found.")
                    all_buttons = [btn for row in current_message.buttons for btn in row]
                    refresh_button_obj = next((btn for btn in all_buttons if btn.text == REFRESH_BUTTON_TEXT), None)

                    if refresh_button_obj:
                        await refresh_button_obj.click()
                        await asyncio.sleep(PAUSE_AFTER_CLICK_SECONDS)
                        messages = await client.get_messages(TARGET_CHAT, limit=1)
                        current_message = messages[0]

                    else:
                        break

                else:
                    print("Max refresh limit")


            if not choice_made:
                #print("Random choice")

                mapped_options = parse_message_and_map_buttons(current_message)

                if mapped_options:
                    random_choice_button = random.choice([opt['button_obj'] for opt in mapped_options])
                    #print(f"   -> Choice'{random_choice_button.text}'")
                    await random_choice_button.click()

                else:
                    print("Nenhuma opção válida para escolha aleatória encontrada.")


        except TimeoutError:
            print(f"Timeout.")

        except Exception as e:
            print(f"Error: {e}")
            #print("  Aguardando para a próxima rodada.")
           

        #print(f"Fim da Rodada {round_counter}")
        #print(f"Aguardando {LOOP_DELAY_SECONDS} segundos para a próxima rodada")
        await asyncio.sleep(LOOP_DELAY_SECONDS)

        round_counter += 1

    #print("\nBot parado")

if __name__ == '__main__':
    asyncio.run(main()) 