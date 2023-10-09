import dotenv
import uvicorn

HOT_RELOAD = dotenv.dotenv_values().get("ENVIRONMENT", "prod") == "dev"

if __name__ == "__main__":
    uvicorn.run("src.api:app", reload=HOT_RELOAD)
