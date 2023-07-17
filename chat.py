import openai
from pathlib import Path
import argparse    
from datetime import datetime
import os
import json

def read_file(filename) -> str:
    with open(filename, "r") as f:
        return f.read()

def write_file(filepath: Path, content: str):
    with open(filepath, "w+") as f:
        f.write(content)

def pretty_json_str(d: dict) -> str:
    return json.dumps(d, indent=2, separators=(',', ': '))

def save_as_json(d: dict, path: Path) -> Path:
    if path.is_dir():
        path /= f"{datetime.now()}.txt"
    path.parent.mkdir(parents=True, exist_ok=True)
    write_file(path, json.dumps(d, indent=2, separators=(',', ': ')))
    return path

def clear_terminal(): 
    os.system('cls' if os.name=='nt' else 'clear')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="GPT chat client", usage="", description="Terminal chat client")
    parser.add_argument("--continue", metavar="Path to previous conversations `out_file`", help="Continue a previous conversation. Command line arguments from the previous session will be overwritten by arguments passed with the new command. You cannot pass a new system_prompt when continuing a previous session.", required=False, type=str)
    parser.add_argument("--key_file", help="Path to file containing your API key", required=False, type=str)
    parser.add_argument("-o", "--out_file", help="Save the conversation to this file.", required=False, type=str, )
    parser.add_argument("--system_prompt", dest="system_prompt", required=False, type=str, help="System prompt to customize bot behavior", default="You are a chill coding buddy, eager to help with specific issues and to teach along the way")
    parser.add_argument("--model", dest="model", required=False, type=str, help="GPT model to use, gpt-4 is the best, but slowest and most expensive. gpt-3.5-turbo is faster and way cheaper", default="gpt-3.5-turbo", choices=["gpt-4", "gpt-4-0613", "gpt-4-32k", "gpt-4-32k-0613", "gpt-3.5-turbo", "gpt-3.5-turbo-0613", "gpt-3.5-turbo-16k", "gpt-3.5-turbo-16k-0613"])
    # Convert the Namespace object to dict for easy serialization
    args = { k:v for k,v in vars(parser.parse_args()).items() if v is not None }
    messages = [{"role": "system", "content": args["system_prompt"]}]

    if ('continue' in args):
        session = json.loads(read_file(args['continue']))
        args = session['args'] | args  # cli args overwrite session file
        messages = session['messages']

    openai.api_key = read_file(args["key_file"])

    clear_terminal()

    print(pretty_json_str(args))

    try:
        while True:
            print(f"\n{messages[-1]['role']}:\t{messages[-1]['content']}\n")
            messages.append({"role": "user", "content": input("user:\t")})
            messages.append(openai.ChatCompletion.create(
                model=args["model"],
                messages=messages
            ).choices[0].message)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"{type(e)}:\n{e}")

    if (args["out_file"] is not None):
        print(f"""Saved session to {save_as_json(
            {
                'args': args, 
                'messages': messages
            }, 
            Path(args['out_file'])).absolute()
        }""")
    exit(0)
