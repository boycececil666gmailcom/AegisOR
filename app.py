# region AegisOR Entrypoint
import os

from src.ui import build_ui

demo = build_ui()

if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=int(os.getenv("PORT", 7860)),
    )
# endregion
