import os
import json
import ulid
from datetime import datetime
import pytz
import gradio as gr
import uuid


class UserContext:
    _context = {}

    @classmethod
    def set_user_id(cls, session_id, user_id):
        cls._context[session_id] = user_id

    @classmethod
    def get_user_id(cls, session_id):
        return cls._context.get(session_id)

    @classmethod
    def clear_user_id(cls, session_id):
        if session_id in cls._context:
            del cls._context[session_id]


class Logs:
    def __init__(self):
        self.log_dir_path = "events_logs"

    def log_event(self, event_name, session_id):
        """Log user activity to the terminal and save to a JSON file."""
        user_id = UserContext.get_user_id(session_id)
        japan_timezone = pytz.timezone('Japan')
        japan_datetime = datetime.fromtimestamp(int(datetime.now().timestamp()), japan_timezone)
        japan_timestamp = int(japan_datetime.timestamp())
        log_entry = {
            "user_id": user_id,
            "event": event_name,
            "datetime": japan_timestamp
        }
        print("Log entry:", log_entry)

        # Create date-based subdirectory
        date_str = datetime.now().strftime('%Y%m%d')
        date_dir_path = os.path.join(self.log_dir_path, date_str)
        if not os.path.exists(date_dir_path):
            os.makedirs(date_dir_path, exist_ok=True)

        # Generate ULID for the log file name
        ulid_str = ulid.from_timestamp(int(datetime.now().timestamp()))
        log_file_path = os.path.join(date_dir_path, f"{ulid_str}.json")

        # Write log entry to the file
        try:
            with open(log_file_path, 'w') as file:
                json.dump(log_entry, file)
        except Exception as e:
            print(f"An error occurred while logging event: {e}")


def store_cookie(context: gr.State, request: gr.Request):
    session_id = context.get("session_id")
    if not session_id:
        session_id = str(uuid.uuid4())
        context["session_id"] = session_id

    context["cookie"] = request.headers.get("cookie", "")
    context["username"] = request.username
    context["last_updated"] = int(datetime.timestamp(datetime.now()))

    # Set the user ID in UserContext
    UserContext.set_user_id(session_id, context["username"])

    # Log the event
    logs = Logs()
    logs.log_event("Logged in", session_id)

    return context


class UI:
    def __init__(self, main_dict_to_ui):
        self.main_dict_to_ui = main_dict_to_ui

    def ui(self):
        self.summary_status = "ON"
        css = """
        #logout-button {
            position: absolute;
            top: 10px;
            right: 10px;
            min-width: 50px;
        }
        """
        with gr.Blocks(css=css) as demo:
            context = gr.State({"user_messages": [], "username": "", "session_expired": False}, time_to_live=40)

            demo.load(store_cookie, inputs=context, outputs=context)

            main_ui = gr.Column(visible=True)
            with main_ui:
                expired_message = gr.Textbox(label="Session Status", value="", visible=False)

        demo.launch(auth=[("user", "password"), ("user2", "password") , ("user3" , "password")],share=True)


# Test the logging functionality
if __name__ == "__main__":
    ui = UI(main_dict_to_ui={})
    ui.ui()
