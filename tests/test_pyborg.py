import pyborg


def test_basic_input():
    def on_prompt(prompt_text):
        if "1" in prompt_text:
            return "a"
        elif "2" in prompt_text:
            return "b"
        elif "3" in prompt_text:
            return "c"
        else:
            return "Unexpected prompt text"

    result, return_code = pyborg.execute("./tests/cli", [], on_prompt)

    assert (
        result
        == """Input 1: a
Input 2: b
Input 3: c
a, b, c
"""
    )

    assert return_code == 0
