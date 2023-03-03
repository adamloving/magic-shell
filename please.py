import os, json, sys
import openai

# for covenience, alias "please" to "python3 please.py"
# by adding the following to your .bashrc or .zshrc
# alias please="python3 /path/to/please.py"
#
# usage: please create an s3 bucked called my-bucket

LONGTERM_MEMORY = ""
SHORTTERM_MEMORY = ""

openai.api_key = os.getenv("OPENAI_API_KEY")

prompt_path = os.path.join(os.path.dirname(__file__), "prompt.txt")
longterm_memory_path = os.path.join(os.path.dirname(__file__), "longterm_memory.txt")
shortterm_memory_path = os.path.join(os.path.dirname(__file__), "shortterm_memory.txt")


# if file "longterm_memory.txt" open it and read into LONGTERM_MEMORY
# else create file and write empty string
def initialize_memory():
    global LONGTERM_MEMORY, SHORTTERM_MEMORY

    if os.path.exists(longterm_memory_path):
        with open(longterm_memory_path, "r") as f:
            LONGTERM_MEMORY = f.read()
    else:
        with open(longterm_memory_path, "w") as f:
            f.write("")

    # same for shortterm_memory.txt
    if os.path.exists(shortterm_memory_path):
        with open(shortterm_memory_path, "r") as f:
            SHORTTERM_MEMORY = f.read()
    else:
        with open(shortterm_memory_path, "w") as f:
            f.write("")
            SHORTTERM_MEMORY = ""


def build_prompt(query):
    global LONGTERM_MEMORY, SHORTTERM_MEMORY
    # open prompt.txt
    with open(prompt_path, "r") as f:
        prompt = f.read()

    if LONGTERM_MEMORY:
        prompt = prompt.replace(
            "%LONGTERM_MEMORY%",
            f"Here are some things we know:\n{LONGTERM_MEMORY}",
        )
    else:
        prompt = prompt.replace("\n%LONGTERM_MEMORY%\n", "")

    if SHORTTERM_MEMORY:
        prompt = prompt.replace(
            "%SHORTTERM_MEMORY%",
            f"Recent commands:\n{SHORTTERM_MEMORY}",
        )
    else:
        prompt = prompt.replace("\n%SHORTTERM_MEMORY%\n", "")

    prompt = prompt.replace("%QUERY%", query)

    return prompt


def complete(prompt):
    text = (
        openai.Completion.create(
            model="text-davinci-003",
            prompt=prompt,
            max_tokens=100,
            temperature=0,
        )
        .to_dict()
        .get("choices", [{}])[0]
        .get("text", "")
    )

    return text


def save_longterm_memory(text):
    global LONGTERM_MEMORY

    with open(longterm_memory_path, "w") as f:
        f.write(LONGTERM_MEMORY + text + "\n")


def save_shortterm_memory(text):
    global SHORTTERM_MEMORY

    # if shortterm_memory is longer than 10 lines, remove the first 2 lines
    lines = SHORTTERM_MEMORY.splitlines()
    if len(lines) > 30:
        SHORTTERM_MEMORY = "\n".join(lines[3:])

    with open(shortterm_memory_path, "w") as f:
        f.write(SHORTTERM_MEMORY + "\n" + text + "\n")


if __name__ == "__main__":
    initialize_memory()

    # combine all arguemnts into one string
    query = " ".join(sys.argv[1:])

    if not query:
        print("Please provide a query")
        sys.exit(1)

    if query.startswith("remember "):
        save_longterm_memory(query.replace("remember ", ""))
        sys.exit(0)

    prompt = build_prompt(query)
    suggested_command = complete(prompt)

    print("Suggested command: \033[33m" + suggested_command + "\033[0m\n")

    # prompt user to accept or reject
    accept = input("Run it? [y/n] ")

    if accept.lower() == "y":
        os.system(suggested_command)
        save_shortterm_memory(f"# {query}\n" + f"{suggested_command}\n")
