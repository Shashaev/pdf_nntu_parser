import logging
import time

import database.connection
import registration
import events
import logs


# database.connection.drop_db()
database.connection.create_db_and_tables()

while True:
    new_registered_functions = []
    min_delay = float('inf')
    for fun in registration.registered_functions:
        if not fun.endless_execution and fun.max_count == 0:
            continue

        if (time.time() - fun.last_execution_time) < fun.delay_time:
            min_delay = min(
                min_delay,
                fun.delay_time - (time.time() - fun.last_execution_time),
            )
            continue

        is_correct = True
        try:
            logging.debug(f'Function processing: {fun}')
            fun.fun()
            fun.last_execution_time = time.time()
            min_delay = min(min_delay, fun.delay_time)
            if not fun.endless_execution:
                fun.max_count -= 1
        except BaseException as e:
            logging.error(e, exc_info=True)
            min_delay = 0

        if fun.endless_execution or fun.max_count:
            new_registered_functions.append(fun)

    registration.registered_functions = new_registered_functions
    if not len(registration.registered_functions):
        break

    logging.info(f'Sleep for {min_delay} seconds')
    time.sleep(min_delay)

logging.info('The application is shutting down...')
