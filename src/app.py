import gradio as gr
import uvicorn
from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from src.ui import build_ui


# region Application Setup
def create_app() -> FastAPI:
    demo = build_ui()
    server = FastAPI(title="AegisOR")

    @server.get("/")
    def redirect_to_aegisor():
        return RedirectResponse(url="/aegisor")

    server = gr.mount_gradio_app(server, demo, path="/aegisor")
    return server


app = create_app()

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=7860)
# endregion
