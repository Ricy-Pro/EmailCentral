# your_app/management/commands/fetch_emails.py
from django.core.management.base import BaseCommand
from myapp.models import Email  # Import your Email model
import imaplib
import email
import csv
import yaml

class Command(BaseCommand):
    help = 'Fetch emails from Gmail and save information to the database'

    def handle(self, *args, **options):
        # Your script to fetch emails goes here
        # Importing libraries
        with open(r"C:\Users\ricir\OneDrive\Documents\GitHub\EmailCentral\EmailCentral\myapp\management\commands\credentials.yml") as f:
            content = f.read()

        my_credentials = yaml.load(content, Loader=yaml.FullLoader)
        user, password = my_credentials["user"], my_credentials["password"]
        imap_url = 'imap.gmail.com'
        my_mail = imaplib.IMAP4_SSL(imap_url)

        try:
            # Log in using your credentials
            my_mail.login(user, password)
            # Select the Inbox to fetch messages
            my_mail.select('Inbox')

            key = 'FROM'
            value = 'welcome@overleaf.com'
            _, data = my_mail.search(None, key, value)

            mail_id_list = data[0].split()
            msgs = []

            # Iterate through messages and extract data into the msgs list
            for num in mail_id_list:
                typ, data = my_mail.fetch(num, '(RFC822)')
                msgs.append(data)

            # Iterate through messages and save information to the database
            for msg in msgs[::-1]:
                for response_part in msg:
                    if type(response_part) is tuple:
                        my_msg = email.message_from_bytes(response_part[1])
                        subject = my_msg['subject']
                        sender = my_msg['from']
                        body = ''
                        for part in my_msg.walk():
                            if part.get_content_type() == 'text/plain':
                                body = part.get_payload()

                        # Create and save Email object to the database
                        email_obj = Email(
                            sender=sender,
                            subject=subject,
                            content=body,
                            source='gmail'  # Set the source to 'gmail'
                            # attachments will be None since emails don't have attachments
                        )
                        email_obj.save()

            self.stdout.write(self.style.SUCCESS('Email information saved to the database.'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {e}'))

        finally:
            # Always close the connection
            my_mail.logout()
