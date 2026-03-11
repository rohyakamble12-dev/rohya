import webbrowser
import urllib.parse
import imaplib
import email

class CommsPlugin:
    def __init__(self, assistant):
        self.assistant = assistant

    def register_intents(self):
        return {
            "send_email": self.compose_email,
            "read_emails": self.check_inbox
        }

    def compose_email(self, params):
        to = params.get("to", "")
        subject = params.get("subject", "Tactical Update")
        body = params.get("body", "")

        subject_enc = urllib.parse.quote(subject)
        body_enc = urllib.parse.quote(body)
        mailto_url = f"mailto:{to}?subject={subject_enc}&body={body_enc}"

        webbrowser.open(mailto_url)
        return f"Drafting email to {to}."

    def check_inbox(self, params):
        # We encourage the user to provide credentials via memory/env
        user = self.assistant.memory.get("email_user")
        pwd = self.assistant.memory.get("email_pass")
        host = self.assistant.memory.get("email_host", "imap.gmail.com")

        if not user or not pwd:
            return "Email credentials missing from my secure memory. Please configure them to enable inbox intelligence."

        try:
            mail = imaplib.IMAP4_SSL(host)
            mail.login(user, pwd)
            mail.select("inbox")
            _, data = mail.search(None, 'UNSEEN')

            mail_ids = data[0].split()
            count = len(mail_ids)
            if count == 0: return "The inbox is clear, Operator."

            # Fetch latest
            _, msg_data = mail.fetch(mail_ids[-1], '(RFC822)')
            msg = email.message_from_bytes(msg_data[0][1])
            subject = msg['subject']
            sender = msg['from']

            return f"You have {count} unread messages. The latest is from {sender} regarding '{subject}'."
        except Exception as e:
            return f"Insecure link: {e}"
