from fastapi import FastAPI
from routing import authorization, datasets, shop
from fastapi.middleware.cors import CORSMiddleware


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

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(authorization.router)
app.include_router(datasets.router)
app.include_router(shop.router)
