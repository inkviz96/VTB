from fastapi import FastAPI
from routing import authorization, datasets


app = FastAPI(openapi_url="/api/v1/openapi.json",
              redoc_url="/api/v1/redoc",
              docs_url="/api/v1/docs",
              version='1.0',
              title='VTB',
              description='VTB hackaton project',
              debug=False,
              openapi_tags=[{"name": "authorization",
                             "description": "Routing for authoruzation users"},
                            {"name": "datasets",
                             "description": "Routing for create, get datasets"}])

app.include_router(authorization.router)
app.include_router(datasets.router)
