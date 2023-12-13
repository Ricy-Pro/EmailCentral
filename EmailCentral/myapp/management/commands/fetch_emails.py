from email import policy
from email.parser import BytesParser
from django.core.management.base import BaseCommand
from django.utils import timezone
from myapp.models import Email, Attachment

import imaplib
import email
import yaml
import pytz
from email import policy
from email.parser import BytesParser

class Command(BaseCommand):
    help = 'Fetch emails from Gmail and update the database'

    def handle(self, *args, **options):
        try:
            # Clear the existing emails and attachments in the database
            Email.objects.all().delete()
            Attachment.objects.all().delete()

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
                        msg_data = response_part[1]
                        msg_text = msg_data.decode('utf-8', errors='replace')
                        msg_bytes = msg_text.encode('utf-8')
                        
                        my_msg = BytesParser(policy=policy.default).parsebytes(msg_bytes)

                        sender = my_msg['from']
                        subject = my_msg['subject']
                        content = ""

                        # Variables to store attachments
                        attachments = []

                        # Extract content if available
                        for part in my_msg.walk():
                            if part.get_content_type() == 'text/plain':
                                content = part.get_payload()
                            elif part.get('Content-Disposition') and 'attachment' in part.get('Content-Disposition'):
                                # This part is an attachment
                                filename = part.get_filename()
                                attachment_content = part.get_payload(decode=True)

                                # Save the attachment to the Attachment model
                                attachment = Attachment(name=filename, content=attachment_content)
                                attachment.save()
                                attachments.append(attachment)

                        # Check if the email already exists
                        if not Email.objects.filter(sender=sender, subject=subject, content=content).exists():
                            # Email does not exist, create a new entry
                            date_header = my_msg['Date']

                            try:
                                # Try parsing with (UTC) suffix
                                received_at_utc = timezone.datetime.strptime(date_header, '%a, %d %b %Y %H:%M:%S %z (UTC)')
                            except ValueError:
                                try:
                                    # Try parsing without (UTC) suffix
                                    received_at_utc = timezone.datetime.strptime(date_header, '%a, %d %b %Y %H:%M:%S %z')
                                except ValueError as e:
                                    # Handle parsing errors
                                    self.stdout.write(self.style.ERROR(f'Error parsing date: {e}'))
                                    continue  # Skip this email if date parsing fails
                            # Try parsing with (UTC) suffix
                            try:
                                received_at_utc = timezone.datetime.strptime(date_header, '%a, %d %b %Y %H:%M:%S %z')
                            except ValueError:
                                # Handle parsing errors
                                self.stdout.write(self.style.ERROR(f'Error parsing date: {e}'))
                                continue  # Skip this email if date parsing fails

                            # Check if the timezone is present in the date header
                            if received_at_utc.tzinfo is None:
                                # If not, assume GMT
                                received_at_utc = received_at_utc.replace(tzinfo=pytz.timezone('GMT'))

                            # Add 2 hours to the received time
                            received_at_utc += timezone.timedelta(hours=2)

                            # Convert to Romanian timezone
                            romanian_timezone = pytz.timezone('Europe/Bucharest')
                            received_at_romanian = received_at_utc.astimezone(romanian_timezone)




                            email_obj = Email(sender=sender, subject=subject, content=content, source='Gmail', received_at=received_at_romanian)
                            email_obj.save()

                            # Associate attachments with the email
                            email_obj.attachments.set(attachments)

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {e}'))

        finally:
            # Close the connection if it was opened successfully
            if 'my_mail' in locals():
                my_mail.logout()

        self.stdout.write(self.style.SUCCESS('Emails fetched and stored in the database successfully.'))
