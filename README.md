# magic-shell

GPT-powered command line assistant for Mac Z shell. For more information, see

https://adamloving.com/2023/02/28/magic-shell/

## Help command
Invokes the ChatGPT (GPT-4) API to help you with a command.

### Example
```
    $ help upload the file to s3
```

## Please command 
Invokes the GPT-3.5 davinci API to generate a command for you.

### Example
```
    $ please install pytorch
```

# Installation

Add these commands to your `~/.zshrc` or `~/.zprofile` file.

```

```
### shortcuts for magicshell please and help command line commands
export OPENAI_API_KEY="sk-123"
alias please="python ~/Projects/magic-shell/please.py" 
alias help="python ~/Projects/magic-shell/help.py"
```


# TODOs

todo: check prequisites. for example, if you need psql, "type p to check prerequisites"

todo: save variables locally and don't send them in the prompt

todo: Add an explain command (to get a longer explanation)

todo: Add a search (the web command)

todo: bootstrap artificial general intelligence behind this script

todo: add “forget” to wipe memory (or atleast the last command)

todo: an API ecosystem and AGI

Any other ideas, please leave a comment below!
