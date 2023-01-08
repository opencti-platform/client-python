import time
from typing import Dict


def wait_for_test_to_finish(
    connector_test_instance, old_state: Dict, timeout: int = 60
) -> str:
    connector_test_instance.initiate()
    sleep_delay = 0.5
    time_spent = 0

    finished = False
    error = ""
    while not finished and time_spent < timeout:
        new_state = connector_test_instance.connector_instance.get_state()
        error = new_state.get("error", "")
        if error:
            finished = True

        if new_state.get("last_run", None) != old_state.get("last_run", None):
            finished = True

        time.sleep(sleep_delay)
        time_spent += sleep_delay

    if time_spent >= timeout and error == "":
        error = f"Timeout after {time_spent} seconds. Please step through your code to find the issue if no error is visible."

    return error


def wait_for_n_jobs(
    connector_test_instance, old_state: Dict, n_jobs: int, timeout: int = 60
) -> str:
    connector_test_instance.initiate()
    sleep_delay = 0.1
    time_spent = 0

    change_cnt = 0
    last_start_from_run = old_state.get("start_from", None)

    finished = False
    error = ""
    while not finished and change_cnt < n_jobs and time_spent < timeout:
        new_state = connector_test_instance.connector_instance.get_state()

        error = new_state.get("error", "")
        if error:
            finished = True

        if new_state.get("start_from", None) != last_start_from_run:
            change_cnt += 1

        time.sleep(sleep_delay)
        time_spent += sleep_delay

    if time_spent >= timeout and error == "":
        error = f"Timeout after {time_spent} seconds. Please step through your code to find the issue if no error is visible."

    return error