from fastapi import FastAPI
from routing import authorization


app = FastAPI(openapi_url="/api/v1/openapi.json",
              redoc_url="/api/v1/redoc",
              docs_url="/api/v1/docs",
              version='1.0',
              title='VTB',
              description='Chia Mining Pool TokenVTB hackaton project',
              debug=False)

app.include_router(authorization.router)
