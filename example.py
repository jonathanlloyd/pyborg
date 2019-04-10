import pyborg

if __name__ == '__main__':
    def on_prompt(prompt_text):
        if "this ok" in prompt_text:
            return "yes"
        elif "version" in prompt_text:
            return "1.0.0"
        elif "license" in prompt_text:
            return "MIT"
        else:
            return "foobar"

    result, return_code = pyborg.execute("npm", ['init'], on_prompt)

    if return_code != 0:
        print('Command failed')
    else:
        print(result)
