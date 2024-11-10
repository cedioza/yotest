from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import os.path
import base64
import pickle
from nvidia_service import  send_image_request 
import base64
import cloudinary
import cloudinary.uploader
from cloudinary.utils import cloudinary_url


# Configuración de Cloudinary       
cloudinary.config( 
    cloud_name="dezprf2aq", 
    api_key="111224942286412", 
    api_secret="BDYRhKXaxsE4twYxZI87D0FaSAg",  # Asegúrate de reemplazar por tu API secret real
    secure=True
)

class GmailService:
    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
    
    def __init__(self):
        self.creds = None
        self.service = None

    def authenticate(self):
        # El archivo token.pickle almacena los tokens de acceso y actualización del usuario
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                self.creds = pickle.load(token)

        # Si no hay credenciales válidas disponibles, permite que el usuario inicie sesión
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', self.SCOPES)
                self.creds = flow.run_local_server()
                flow.redirect_uri = "http://localhost"
            
            # Guarda las credenciales para la próxima ejecución
            with open('token.pickle', 'wb') as token:
                pickle.dump(self.creds, token)

        self.service = build('gmail', 'v1', credentials=self.creds)
        return self.service

    def get_emails(self, max_results=10):
        """Obtiene los últimos correos electrónicos."""
        try:
            # Obtiene la lista de mensajes
            results = self.service.users().messages().list(
                userId='me', maxResults=max_results).execute()
            messages = results.get('messages', [])

            emails = []
            for message in messages:
                msg = self.service.users().messages().get(
                    userId='me', id=message['id']).execute()
                
                # Extrae los headers relevantes
                headers = msg['payload']['headers']
                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'Sin asunto')
                from_email = next((h['value'] for h in headers if h['name'] == 'From'), 'Desconocido')
                date = next((h['value'] for h in headers if h['name'] == 'Date'), 'Sin fecha')

                email_data = {
                    'id': msg['id'],
                    'subject': subject,
                    'from': from_email,
                    'date': date,
                    'snippet': msg['snippet']
                }
                emails.append(email_data)

            return emails

        except Exception as e:
            print(f"Error al obtener correos: {str(e)}")
            return []
        
        
    def get_email_details(self, email_id):
        """Obtiene los detalles de un correo electrónico específico por su ID."""
        try:
            # Obtiene el mensaje específico utilizando el ID
            msg = self.service.users().messages().get(
                userId='me', id=email_id).execute()
            
            # Extrae los headers relevantes
            headers = msg['payload']['headers']
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'Sin asunto')
            from_email = next((h['value'] for h in headers if h['name'] == 'From'), 'Desconocido')
            date = next((h['value'] for h in headers if h['name'] == 'Date'), 'Sin fecha')

            email_data = {
                'id': msg['id'],
                'subject': subject,
                'from': from_email,
                'date': date,
                'snippet': msg['snippet'],
                'body': msg['payload'].get('body', {}).get('data', 'Sin contenido')  # Obtiene el cuerpo si existe
            }

            return email_data

        except Exception as e:
            print(f"Error al obtener detalles del correo: {str(e)}")
            return None


    def get_emails_with_attachments(self, max_results=10):
        """Obtiene los correos electrónicos que contienen adjuntos."""
        try:
            results = self.service.users().messages().list(
                userId='me', maxResults=max_results).execute()
        
            messages = results.get('messages', [])

            emails_with_attachments = []
            for message in messages:
                msg = self.service.users().messages().get(
                    userId='me', id=message['id']).execute()
                
                headers = msg['payload']['headers']
                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'Sin asunto')
                from_email = next((h['value'] for h in headers if h['name'] == 'From'), 'Desconocido')
                date = next((h['value'] for h in headers if h['name'] == 'Date'), 'Sin fecha')

                # Verificar si el mensaje tiene partes adjuntas
                attachments = []
                for part in msg['payload'].get('parts', []):
                    if part['filename']:
                        # Si hay un nombre de archivo, es un adjunto
                        attachment_id = part['body'].get('attachmentId')
                        mime_type = part['mimeType']
                        
                        attachments.append({
                            'filename': part['filename'],
                            'mime_type': mime_type,
                            'attachment_id': attachment_id
                        })

                if attachments:
                    emails_with_attachments.append({
                        'id': msg['id'],
                        'subject': subject,
                        'from': from_email,
                        'date': date,
                        'snippet': msg['snippet'],
                        'attachments': attachments
                    })

            return emails_with_attachments

        except Exception as e:
            print(f"Error al obtener correos con adjuntos: {str(e)}")
            return []

    def download_attachment(self, user_id):
        message = self.service.users().messages().get(userId='me', id=user_id).execute()
        import uuid
        random_id = uuid.uuid4().hex[:8]
        for part in message['payload']['parts']:
            if 'filename' in part and part['filename']:  # Si tiene nombre de archivo, es un adjunto
                attachment_id = part['body']['attachmentId']
                attachment = self.service.users().messages().attachments().get(userId='me', messageId=user_id, id=attachment_id).execute()
                
                binary_file = attachment['data']

                # base64_data = base64.urlsafe_b64decode(binary_file)
                # base64_encoded_data = base64.b64encode(base64_data).decode('utf-8')
                # cloudinary_data_uri = f"data:image/jpeg;base64,{base64_encoded_data}"
               
                # upload_result = cloudinary.uploader.upload(cloudinary_data_uri, public_id=f"{part['filename']}", overwrite=True)
                
                # Imprimir la URL segura de Cloudinary
                # print("URL segura de Cloudinary:", upload_result["secure_url"])
                return binary_file


    def download_attachment_nvidia(self, user_id):
        message = self.service.users().messages().get(userId='me', id=user_id).execute()
        import uuid
        random_id = uuid.uuid4().hex[:8]
        for part in message['payload']['parts']:
            if 'filename' in part and part['filename']:  # Si tiene nombre de archivo, es un adjunto
                attachment_id = part['body']['attachmentId']
                attachment = self.service.users().messages().attachments().get(userId='me', messageId=user_id, id=attachment_id).execute()
                
                binary_file = attachment['data']
                send_image_request(binary_file)

                print("send_image_request",send_image_request.get("choices"))
                return binary_file
