from django.core.management.base import BaseCommand
from django.utils import timezone
from myapp.models import Email
import imaplib
import email
import yaml

class Command(BaseCommand):
    help = 'Fetch emails from Gmail and update the database'

    def handle(self, *args, **options):
        try:
            with open(r"C:\Users\ricir\OneDrive\Documents\GitHub\EmailCentral\EmailCentral\myapp\management\commands\credentials.yml") as f:
                content = f.read()

            my_credentials = yaml.load(content, Loader=yaml.FullLoader)
            user, password = my_credentials["user"], my_credentials["password"]
            imap_url = 'imap.gmail.com'
            my_mail = imaplib.IMAP4_SSL(imap_url)

            # Log in using your credentials
            my_mail.login(user, password)
            # Select the Inbox to fetch messages
            my_mail.select('Inbox')

            # Set the key and dynamically set the value to today's date
            key = 'SINCE'
            value = timezone.now().strftime("%d-%b-%Y")
            _, data = my_mail.search(None, key, value)

            mail_id_list = data[0].split()
            msgs = []

            # Iterate through messages and extract data into the msgs list
            for num in mail_id_list:
                typ, data = my_mail.fetch(num, '(RFC822)')
                msgs.append(data)

            # Iterate through messages and store in the database
            for msg in msgs[::-1]:
                for response_part in msg:
                    if type(response_part) is tuple:
                        my_msg = email.message_from_bytes(response_part[1])
                        sender = my_msg['from']
                        subject = my_msg['subject']
                        content = ""

                        # Extract content if available
                        for part in my_msg.walk():
                            if part.get_content_type() == 'text/plain':
                                content = part.get_payload()
                 
                        # Check if the email already exists
                        if not Email.objects.filter(sender=sender, subject=subject, content=content).exists():
                            # Email does not exist, create a new entry
                            # Extract the date header from the email
                            date_header = my_msg['Date']

                            try:
                                # Try parsing with (UTC) suffix
                                received_at = timezone.datetime.strptime(date_header, '%a, %d %b %Y %H:%M:%S %z (UTC)')
                            except ValueError:
                                try:
                                    # Try parsing without (UTC) suffix
                                    received_at = timezone.datetime.strptime(date_header, '%a, %d %b %Y %H:%M:%S %z')
                                except ValueError as e:
                                    # Handle parsing errors
                                    self.stdout.write(self.style.ERROR(f'Error parsing date: {e}'))
                                    continue  # Skip this email if date parsing fails

        

                            email_obj = Email(sender=sender, subject=subject, content=content, source='Gmail', received_at=received_at)
                            email_obj.save()

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {e}'))

        finally:
            # Close the connection if it was opened successfully
            if 'my_mail' in locals():
                my_mail.logout()

        self.stdout.write(self.style.SUCCESS('Emails fetched and stored in the database successfully.'))
