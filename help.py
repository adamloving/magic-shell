import os, json, sys, time
import openai

# for covenience, alias "help" to "python3 help.py"
# by adding the following to your .bashrc or .zshrc
# alias help="python3 /path/to/help.py"
#
# usage: help create an s3 bucked called my-bucket

LONGTERM_MEMORY = ""
CURRENT_CONVO_JSON = ""

openai.api_key = os.getenv("OPENAI_API_KEY")

prompt_path = os.path.join(os.path.dirname(__file__), "help_prompt.txt")

# path to a text file with English statements
longterm_memory_path = os.path.join(os.path.dirname(__file__), "longterm_memory.txt")

# path to a JSON file with the current conversation (the chat completion messages array)
current_convo_path = os.path.join(os.path.dirname(__file__), "convos/current.json")


def initialize_memory():
    global LONGTERM_MEMORY, CURRENT_CONVO_JSON

    if os.path.exists(longterm_memory_path):
        # open "longterm_memory.txt" and read into LONGTERM_MEMORY
        with open(longterm_memory_path, "r") as f:
            LONGTERM_MEMORY = f.read()

    if os.path.exists(current_convo_path):
        # if file exists and is > 12 hours old, rename it using the file's last modified time
        last_modified = os.path.getmtime(current_convo_path)
        if last_modified < time.time() - 12 * 60 * 60:
            os.rename(current_convo_path, f"convos/{last_modified}.json")

    # now open the current conversation (if any)
    if os.path.exists(current_convo_path):
        with open(current_convo_path, "r") as f:
            CURRENT_CONVO_JSON = f.read()


def build_messages(query):
    global LONGTERM_MEMORY, SHORTTERM_MEMORY

    if CURRENT_CONVO_JSON:
        # continue the current conversation
        messages = json.loads(CURRENT_CONVO_JSON)
    else:
        with open(prompt_path, "r") as f:
            prompt = f.read()

        messages = []

        messages.append(
            {
                "role": "system",
                "content": prompt,
            }
        )

        if LONGTERM_MEMORY:
            messages.append(
                {
                    "role": "system",
                    "content": f"Here is some context you can use to infer information to be used in commands {LONGTERM_MEMORY}",
                }
            )

    # now add the users' latest query
    messages.append(({"role": "user", "content": query}))

    return messages


def complete(messages):
    print("Messages:")
    print(json.dumps(messages, indent=4))

    completion_message = (
        openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages,
            temperature=0.2,
        )
        .to_dict()
        .get("choices", [{}])[0]
        .get("message", {})
    )
    print("Completion message:")
    print(json.dumps(completion_message, indent=4))

    return completion_message


def save_longterm_memory(text):
    with open(longterm_memory_path, "w") as f:
        f.write(LONGTERM_MEMORY + text + "\n")


# Bugbug: rotate the current conversation every 2 hours
def save_conversation(messages):
    # overwrite the current conversation
    with open(current_convo_path, "w") as f:
        f.write(json.dumps(messages, indent=4))


if __name__ == "__main__":
    initialize_memory()

    # combine all arguments into one string
    query = " ".join(sys.argv[1:])

    if not query:
        print("Please provide more info. Example: help create an s3 bucket")
        sys.exit(1)

    if query.startswith("remember "):
        # add one line to longterm_memory.txt
        save_longterm_memory(query.replace("remember ", ""))
        sys.exit(0)

    # either continue previous convo, or start a new one
    # append the query to the current conversation
    input_messages = build_messages(query)
    completion_message = complete(input_messages)
    content = completion_message.get("content", "")

    # check if the completion message is a question
    while "Please enter " in content:
        clarification = content
        print("")
        answer = input(content)  # get input from user via terminal
        input_messages.append(completion_message)
        input_messages.append({"role": "user", "content": answer})
        completion_message = complete(input_messages)
        content = completion_message.get("content", "")

    explanation = content.split(":$: ")[0]
    command = content.split(":$: ")[-1]
    print(explanation)

    if command:
        print("Suggestion: \033[33m" + command + "\033[0m\n")

        # prompt user to accept or reject
        accept = input("Run it? [y/n] ")
        if accept.lower() == "y":
            input_messages.append(completion_message)

            # run the command and capture standard output
            result = os.popen(command).read()

            if len(result) > 1003:
                # take the first 500 and the last 500 characters
                # with a "..." in the middle
                result = result[:500] + "..." + result[-500:]

            print("RESULT: " + str(result))
            input_messages.append(
                {"role": "system", "content": "Result: " + str(result)}
            )
            save_conversation(input_messages)
