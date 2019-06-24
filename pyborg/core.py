"""Top-level pyborg implementation"""

from subprocess import Popen, PIPE
from time import sleep
from fcntl import fcntl, F_GETFL, F_SETFL
from os import O_NONBLOCK, read, write

SLEEP_SECS = 0.05


def execute(command, arguments, callback):
    """Executes a command in a subshell with prompt support.

    This is the main entrypoint to pyborg. Runs the given command in a subshell.
    If the command prompts for input, pyborg will call the provided callback passing
    in the prompt text. The return value of the callback will be entered into
    the prompt followed by the return key.

    The output of the command, after all prompts have been completed will be returned.

    :param command: The command to be executed
    :type command: str
    :param arguments: List of arguments to be passed to the executed command
    :type command: list
    :param arguments: Callback that will be fired when command prompts for input
    :type command: function

    :returns: Tuple - first element is terminal output for session, second is
              the process return code.
    :rtype: tuple(str, int)
    """

    proc = Popen(
        [command, *arguments], stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=False
    )
    flags = fcntl(proc.stdout, F_GETFL)
    fcntl(proc.stdout, F_SETFL, flags | O_NONBLOCK)

    session = ""
    return_code = None

    while True:
        prompt_text_bytes, return_code = _read_prompt(proc)
        has_errored = isinstance(return_code, int) and return_code > 0
        if has_errored:
            _, error_bytes = proc.communicate()
            error = error_bytes.decode()
            return error, return_code

        prompt_text = prompt_text_bytes.decode()

        ended = return_code is not None
        if ended:
            session += prompt_text
            break

        if prompt_text == "":
            continue

        response = callback(prompt_text)
        write(proc.stdin.fileno(), response.encode() + b"\n")

        session += prompt_text + response + "\n"

    return session, return_code


def _read_prompt(process):
    prompt_text_bytes = b""
    while True:
        return_code = process.poll()
        if return_code is not None:
            return prompt_text_bytes, return_code
        sleep(SLEEP_SECS)
        try:
            prompt_text_bytes += read(process.stdout.fileno(), 1024)
        except OSError:
            return prompt_text_bytes, None
