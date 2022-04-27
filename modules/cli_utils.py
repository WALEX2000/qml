from subprocess import Popen, PIPE, STDOUT
import io
import os

def CLIexec(cmd: str, execDir: str = os.getcwd()):
    p = Popen(cmd, stdout = PIPE, stderr = STDOUT, shell = True, cwd=execDir)
    reader = io.TextIOWrapper(p.stdout, encoding=None, newline='')
    while not p.stdout.closed:
        char = reader.read(1)
        if(char == ''):
            break
        print(char, end='')
    
    reader.close()

def CLIcomm(cmd: str, execDir: str, inputs: list[str]):
    p = Popen(cmd, stdout = PIPE, stderr = STDOUT, stdin=PIPE, shell = True, cwd=execDir)
    reader = io.TextIOWrapper(p.stdout, encoding=None, newline='')
    writer = io.TextIOWrapper(p.stdin, line_buffering=True, newline=None)
    iterator = 0
    while not p.stdout.closed and not p.stdin.closed:
        if(iterator < len(inputs)):
            res = writer.write(inputs[iterator] + '\n')
            if(res == len(inputs[iterator]) + 1):
                iterator += 1
        char = reader.read(1)
        if(char == ''):
            break
        else:
            print(char, end='')
    
    reader.close()
    writer.close()