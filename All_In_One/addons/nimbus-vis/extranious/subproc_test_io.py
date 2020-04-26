from subprocess import Popen, PIPE
proc = Popen('py',
    stdin = PIPE,
    stdout = PIPE,
    stderr = PIPE,
    )
stdout, stderr = proc.communicate()

#output = proc.stdout.readline()
#print(output.strip())
#print(output)