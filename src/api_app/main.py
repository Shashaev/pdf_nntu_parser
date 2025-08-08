import pathlib
import sys

import fastapi
import uvicorn


script_dir = pathlib.Path(__file__).parent.parent
sys.path.append(str(script_dir))


import parsing_app.database.connection as connection
import api


connection.create_db_and_tables()

app = fastapi.FastAPI()
app.include_router(api.main_router)

if __name__ == '__main__':
    uvicorn.run('main:app', reload=True)
