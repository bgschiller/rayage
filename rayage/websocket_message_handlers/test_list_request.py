from constants import *

import os
import json
import os.path

from ..WebSocketHandler import messageHandler

@messageHandler("test_list_request")
def handle_project_list_request(socket_connection, message):
    """
    Writes a JSON structure representing the available projects to work on to our socket.
    Currently a flat list of folders in the STUDENTS_DIR
    """
    tests = [{'label': p, 'id': p} for p in os.listdir(TESTS_DIR)]
                                      
    result_message = {'type': 'test_list',
                      'tests': tests}

    socket_connection.write_message(json.dumps(result_message))
