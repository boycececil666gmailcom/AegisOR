import gradio as gr

from src.assembly_service import SPECIALTY_PRESETS
from src.samples import SAMPLE_INTRAOP_TEXT, SAMPLE_POSTOP_TEXT, SAMPLE_TIMEOUT_TEXT
from src.ui.handlers import (
    assembly_service,
    handle_apply_preset,
    handle_intraop,
    handle_postop,
    handle_reset_vocabulary,
    handle_save_vocabulary,
    handle_timeout,
)


# region Gradio UI Builder
def build_ui() -> gr.Blocks:
    with gr.Blocks(title="AegisOR") as demo:
        gr.Markdown(
            """
            # AegisOR
            Enforces The Joint Commission Universal Protocol, monitors Closed-Loop Communication, and compiles audit records using AssemblyAI.
            """
        )

        with gr.Tabs():
            # Tab 0: Pre-Case Setup & Lexicon Tuning
            with gr.TabItem("0. Pre-Case Setup & Lexicon Tuning"):
                gr.Markdown(
                    """
                    **Pre-Case Clinical Setup & Acoustic Vocabulary Priming**:
                    Configure procedural guidelines, expected clinical terminology, pharmaceutical names, and surgical presets before case initiation.
                    This primes the speech recognition engine with custom acoustic probability boosting to maximize transcription accuracy.
                    """
                )
                default_preset = next(iter(SPECIALTY_PRESETS.keys()))
                with gr.Row():
                    with gr.Column(scale=1):
                        vocab_preset = gr.Dropdown(
                            choices=list(SPECIALTY_PRESETS.keys()),
                            value=default_preset,
                            label="Clinical Specialty Preset",
                        )
                        btn_apply_preset = gr.Button(
                            "Load Specialty Preset", variant="secondary"
                        )

                        vocab_input = gr.Textbox(
                            value=", ".join(SPECIALTY_PRESETS[default_preset]),
                            lines=5,
                            label="Custom Vocabulary & Keywords (Comma or Line Separated)",
                            placeholder="e.g. Marcaine, Calot's triangle, heparin, da Vinci...",
                        )

                        guidelines_input = gr.Textbox(
                            value="Patient undergoing laparoscopic cholecystectomy for symptomatic cholelithiasis. Key landmarks: Calot's triangle, cystic duct, cystic artery. Attending: Dr. Davis, Anesthesia: Dr. Evans, RN: Sarah.",
                            lines=4,
                            label="Procedural Guidelines & Clinical Context Briefing",
                            placeholder="Provide operational scenario or background...",
                        )

                        with gr.Row():
                            btn_save_vocab = gr.Button(
                                "Save & Update AI Lexicon", variant="primary"
                            )
                            btn_reset_vocab = gr.Button(
                                "Reset to Baseline", variant="stop"
                            )

                    with gr.Column(scale=2):
                        vocab_status = gr.Markdown(
                            "### STATUS: BASELINE SURGICAL LEXICON ACTIVE"
                        )
                        init_active = assembly_service.get_active_vocabulary()
                        init_preview = (
                            f"**Total Active Boosted Terms ({len(init_active)}):**\n\n"
                            + ", ".join([f"`{w}`" for w in init_active])
                        )
                        vocab_preview = gr.Markdown(value=init_preview)

                btn_apply_preset.click(
                    fn=handle_apply_preset,
                    inputs=[vocab_preset],
                    outputs=[vocab_input],
                )

                btn_save_vocab.click(
                    fn=handle_save_vocabulary,
                    inputs=[vocab_input, guidelines_input],
                    outputs=[vocab_status, vocab_preview],
                )

                btn_reset_vocab.click(
                    fn=handle_reset_vocabulary,
                    inputs=[],
                    outputs=[
                        vocab_input,
                        guidelines_input,
                        vocab_status,
                        vocab_preview,
                    ],
                )

            # Tab 1: Pre-Op Time-Out
            with gr.TabItem("1. Pre-Op Time-Out Verification"):
                gr.Markdown(
                    """
                    **The Universal Protocol**: Before surgical incision, all team members (Surgeon, Anesthesia, Nursing)
                    must verbally confirm patient identity, correct procedure, operative site/side, consent, allergies, and antibiotics.
                    """
                )
                with gr.Row():
                    with gr.Column(scale=1):
                        to_audio = gr.Audio(
                            sources=["upload", "microphone"],
                            type="filepath",
                            label="Operating Room Audio Stream",
                        )
                        to_text = gr.Textbox(
                            value=SAMPLE_TIMEOUT_TEXT,
                            lines=6,
                            label="Acoustic Transcript / Surgical Scenario Input",
                        )
                        to_btn = gr.Button(
                            "Execute Pre-Op Verification", variant="primary"
                        )

                    with gr.Column(scale=2):
                        to_status = gr.Markdown("### STATUS: AWAITING TIME-OUT AUDIO")
                        to_checklist = gr.Markdown(
                            "Checklist will appear here upon evaluation."
                        )
                        with gr.Accordion("Diarized Acoustic Log", open=False):
                            to_diar = gr.Markdown()

                to_btn.click(
                    fn=handle_timeout,
                    inputs=[to_audio, to_text],
                    outputs=[to_status, to_checklist, to_diar],
                )

            # Tab 2: Intra-Op Closed Loop
            with gr.TabItem("2. Intra-Op Closed-Loop Tracking"):
                gr.Markdown(
                    """
                    **Closed-Loop Communication**: In high-acuity environments, verbal medication orders and critical actions
                    must be answered by an explicit read-back to guarantee the instruction was heard and executed accurately.
                    """
                )
                with gr.Row():
                    with gr.Column(scale=1):
                        cl_audio = gr.Audio(
                            sources=["upload", "microphone"],
                            type="filepath",
                            label="Intra-Op Audio Stream",
                        )
                        cl_text = gr.Textbox(
                            value=SAMPLE_INTRAOP_TEXT,
                            lines=6,
                            label="Intra-Op Dialogue Input",
                        )
                        cl_btn = gr.Button(
                            "Track Closed-Loop Orders", variant="primary"
                        )

                    with gr.Column(scale=2):
                        cl_summary = gr.Markdown("### Closed-Loop Ledger Status")
                        cl_table = gr.Dataframe(
                            headers=[
                                "Order ID",
                                "Timestamp",
                                "Type",
                                "Directive",
                                "Directed By",
                                "Read-Back",
                                "Read-Back By",
                                "Status",
                            ],
                            datatype=[
                                "str",
                                "str",
                                "str",
                                "str",
                                "str",
                                "str",
                                "str",
                                "str",
                            ],
                            label="Active Communication Ledger",
                        )
                        with gr.Accordion(
                            "Recognized Surgical & Pharmaceutical Entities", open=True
                        ):
                            cl_entities = gr.Markdown()

                cl_btn.click(
                    fn=handle_intraop,
                    inputs=[cl_audio, cl_text],
                    outputs=[cl_table, cl_summary, cl_entities],
                )

            # Tab 3: Post-Op Sign-Out
            with gr.TabItem("3. Post-Op Sign-Out & Operative Report"):
                gr.Markdown(
                    """
                    **Sign-Out & Operative Documentation**: Automatically compiles surgical milestones, count verifications,
                    and executive operative summaries for immediate electronic health record archiving.
                    """
                )
                with gr.Row():
                    with gr.Column(scale=1):
                        po_audio = gr.Audio(
                            sources=["upload", "microphone"],
                            type="filepath",
                            label="Sign-Out Audio Stream",
                        )
                        po_text = gr.Textbox(
                            value=SAMPLE_POSTOP_TEXT,
                            lines=6,
                            label="Sign-Out Transcript Input",
                        )
                        po_btn = gr.Button(
                            "Generate Operative Audit Report", variant="primary"
                        )

                    with gr.Column(scale=2):
                        gr.Markdown("### Complete Operative Audit Ledger")
                        po_report = gr.Markdown(
                            "Operative Audit Ledger will appear here upon report generation."
                        )

                po_btn.click(
                    fn=handle_postop,
                    inputs=[po_audio, po_text],
                    outputs=[po_report],
                )

    return demo


# endregion
