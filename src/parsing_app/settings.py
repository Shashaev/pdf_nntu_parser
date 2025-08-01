import pathlib


PATH_ROOT = pathlib.Path(__file__).parent

PATH_DATA = PATH_ROOT / pathlib.Path('data/')
PATH_DATA.mkdir(exist_ok=True)

# PATH_HTML = PATH_DATA / 'html'
# PATH_HTML.mkdir(exist_ok=True)

PATH_PDF = PATH_DATA / 'pdf'
PATH_PDF.mkdir(exist_ok=True)
PATH_PDF_EDUCATIONAL_PROGRAM = PATH_PDF / 'educational_program'
PATH_PDF_EDUCATIONAL_PROGRAM.mkdir(exist_ok=True)
PATH_PDF_RPD = PATH_PDF / 'rpd'
PATH_PDF_RPD.mkdir(exist_ok=True)

USE_POSTGRESQL = False
DB_USER = None
DB_PASSWORD = None
DB_HOST = None
DB_PORT = None
DB_NAME = None

if not USE_POSTGRESQL:
    PATH_DB = PATH_DATA / "database.db"
    CONNECTION_STRING = f'sqlite:///{str(PATH_DB)}'
else:
    CONNECTION_STRING = (
        f'postgresql+asyncpg://{DB_USER}:'
        f'{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
    )
