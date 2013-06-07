from constants import *
import os.path
import json
import itertools
from ..ProjectRunner import ProjectRunner
from ..WebSocketHandler import messageHandler

@messageHandler("run_test_request", ["test"])
def handle_run_test_request(socket_connection, message):
    test_name = TESTS_DIR + "/" + message['test']
    executable = socket_connection.project_dir("a.out")
    reference_file = [out for out in os.listdir(test_name) if out[-3:] == 'ref'][0]
    infile = [f for f in os.listdir(test_name) if f[-2:] == 'in'][0]
    with open(test_name + '/' + reference_file,'r') as f:
        expected_output = f.read().splitlines()
    with open(test_name + '/' + infile, 'r') as f:
        given_input = f.read()
    socket_connection.actual_output = []

    print "run_test_request:", executable, " with test:", test_name
    
    if socket_connection.project_runner is not None:
        socket_connection.notify("This project is already running! Check the run console.", "error")
        return
    
    if not os.path.exists(executable):
        socket_connection.notify("The project must be built before running!", "error")
        return
    
    def stdout_cb(data):
        socket_connection.actual_output.append(data)
    
    def stderr_cb(data):
        socket_connection.notify("test produced output on stderr, which is not supported for testing")
    
    def exited_cb(return_value):
        socket_connection.notify("{} exited with return value of {}".format(executable, return_value), "info")
        return_message = {
            'type': 'test_results',
            'lines': []
        }
        actual_output = ''.join(socket_connection.actual_output).splitlines()
        del socket_connection.actual_output
        for expected, actual in itertools.izip_longest(expected_output, actual_output):
            line ={
                'content':actual if actual is not None else '',
                'judgement':'good'
            }
            if actual != expected:
                line['content'] += '(expected "{}")'.format(expected if expected is not None else '')
                line['judgement'] = 'bad'
            line['content'] += '\n'
            return_message['lines'].append(line)
        socket_connection.write_message(json.dumps(return_message))
        socket_connection.project_runner = None
        
    def timeout_cb():
        socket_connection.notify("Your program was taking too long to run. Check your loops.", "error")
    
    args = [] #this is a bit of a cop-out-- we should allow args.
    socket_connection.project_runner = ProjectRunner(executable, args, stdout_cb, stderr_cb, exited_cb, timeout_cb)
    socket_connection.project_runner.start()
    socket_connection.project_runner.queue_input(given_input)
    socket_connection.log("debug","has run test project \"{}\"".format(socket_connection.project))
