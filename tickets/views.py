# tickets/views.py
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import os
import google.auth
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
import requests
import base64




def bot_response(request):
    # Aquí puedes personalizar la lógica de tu bot
    response_data = {
        'message': '¡Hola! Soy el bot de soporte. ¿En qué puedo ayudarte hoy?'
    }
    return JsonResponse(response_data)

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from utils.email_service import GmailService

from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
@require_http_methods(["GET"])
def get_emails(request):
    try:
        max_results = int(request.GET.get('max_results', 10))
        gmail_service = GmailService()
        gmail_service.authenticate()
        emails = gmail_service.get_emails(max_results=max_results)
        
        return JsonResponse({
            'status': 'success',
            'data': emails
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def get_email_detail(request, email_id):
    try:
        gmail_service = GmailService()
        gmail_service.authenticate()
        
        # Obtener los detalles del correo usando el método get_email_details
        email_detail = gmail_service.get_email_details(email_id)
        
        if email_detail is None:
            return JsonResponse({
                'status': 'error',
                'message': 'No se pudo obtener los detalles del correo'
            }, status=404)
        
        return JsonResponse({
            'status': 'success',
            'data': email_detail
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)
    

@csrf_exempt
@require_http_methods(["GET"])
def get_emails_with_attachments(request):
    try:
        gmail_service = GmailService()
        gmail_service.authenticate()
        
        max_results = request.GET.get('max_results', 10)
        emails_with_attachments = gmail_service.get_emails_with_attachments(max_results=int(max_results))
        
        return JsonResponse({
            'status': 'success',
            'data': emails_with_attachments
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)
    

@csrf_exempt
def gmail_notification(request):
    if request.method == 'GET':
        try:
            print("try antes del post")

            # Inicializar el servicio de Gmail
            gmail_service = GmailService()
            gmail_service.authenticate()

            # Obtener correos con adjuntos
            max_results = 10  # Puedes ajustar la cantidad de correos
            emails_with_attachments = gmail_service.get_emails_with_attachments(max_results=max_results)

            # Configurar la API de Mistral
            api_key = os.environ["MISTRAL_API_KEY"]
            model = "pixtral-12b-2409"
            mistral_responses = []

            email_data = emails_with_attachments
            if not isinstance(email_data, list):
                return JsonResponse({
                    'status': 'error',
                    'message': 'Formato de datos inesperado en emails_with_attachments["data"]'
                }, status=500)

            for email in email_data:
                email_id = email.get('id')
                subject = email.get('subject', 'Sin asunto')
                snippet = email.get('snippet', 'Sin contenido')
                base64_image = gmail_service.download_attachment_nvidia(email_id)
                promt_it = """
                    Actúa como un agente de soporte técnico especializado en productos electrónicos, con años de experiencia en la resolución de problemas de hardware y software de dispositivos de computación y consumo. Te llamas Enrique, y tu tarea es atender consultas por correo electrónico de clientes que experimentan problemas técnicos con nuestros productos. Proporciona una respuesta clara, detallada y estructurada. Responde de manera profesional, formal y técnica, iniciando con una breve presentación para transmitir confianza y adaptando el lenguaje a cada tipo de usuario (técnico o general) según la consulta.

                    Objetivo del correo de respuesta: Identificar la causa del problema, proporcionar una solución paso a paso y ofrecer recomendaciones adicionales para evitar futuros inconvenientes con el dispositivo.

                    Instrucciones detalladas:
                    Presentación Formal y Cortesía Inicial:

                    Inicia con un saludo cordial. Si el cliente proporciona su nombre, utiliza "Estimado/a [nombre del cliente]". Si no se menciona nombre, usa un saludo directo como "Estimado/a Cliente".
                    Preséntate de manera formal como Enrique (ej., "Mi nombre es Enrique, y seré el encargado de asistirlo/a con su consulta sobre [problema específico del dispositivo]").
                    Identificación del Problema: Resume el problema específico que el cliente experimenta, usando un lenguaje claro y similar al del cliente para demostrar comprensión.

                    Posibles Causas: Describe las causas más probables del problema, incluyendo detalles técnicos específicos al dispositivo.

                    Pasos de Solución:

                    Proporciona instrucciones específicas y numeradas para resolver el problema. Asegúrate de incluir cada paso necesario, con detalles claros. Ejemplos:
                    Si el paso implica abrir el dispositivo, explica cómo hacerlo con seguridad.
                    Si requiere configuraciones de software, menciona cada opción específica que debe seleccionar el cliente.
                    Pruebas Posteriores: Indica al cliente cómo verificar si el problema ha sido solucionado después de seguir cada paso.

                    Recomendaciones Finales: Sugiere medidas preventivas y buenas prácticas para evitar que el problema ocurra nuevamente en el futuro.

                    Cierre Formal: Finaliza el correo agradeciendo la confianza del cliente y ofreciendo soporte adicional si es necesario (ej., "No dude en contactarnos si tiene alguna otra consulta. Estaremos encantados de asistirle.").

                    Ejemplo de Respuesta:

                    Asunto: Resolución de Sobrecalentamiento en su Laptop

                    Estimado/a Cliente, (o "Estimado/a [Nombre del Cliente]" si se proporciona)

                    Mi nombre es Enrique y seré el encargado de asistirlo/a con su consulta sobre el sobrecalentamiento de su laptop. Entiendo lo importante que es para usted mantener el buen funcionamiento de su dispositivo, y estoy aquí para ayudarle a resolver este inconveniente.

                    Identificación del Problema: Su laptop se sobrecalienta rápidamente durante el uso prolongado.

                    Posibles Causas:

                    Acumulación de polvo en los ventiladores y disipadores.
                    Uso de programas de alto consumo de recursos sin una adecuada ventilación.
                    Posible mal funcionamiento del sistema de refrigeración interna.
                    Pasos de Solución:

                    Verifique la Ventilación: Coloque la laptop sobre una superficie plana y dura que no bloquee las ventilaciones.
                    Limpieza de Ventiladores:
                    Apague la laptop y desconéctela.
                    Si está familiarizado con la apertura del dispositivo, retire cuidadosamente la tapa trasera y utilice aire comprimido para limpiar los ventiladores.
                    Nota: Si no tiene experiencia, recomendamos contactar a un técnico.
                    Optimización de Programas:
                    Abra el Administrador de tareas y verifique qué programas consumen más CPU.
                    Cierre programas innecesarios y considere reducir el uso de aplicaciones de alta demanda.
                    Actualización de Controladores: Asegúrese de que los controladores de hardware estén actualizados visitando el sitio oficial del fabricante.
                    Recomendaciones Finales:

                    Utilice un soporte con ventilación adecuada.
                    Evite el uso de la laptop en superficies blandas que obstruyan la ventilación.
                    Realice una limpieza interna cada seis meses para mantener el sistema de enfriamiento en buen estado.
                    Agradezco su confianza y quedo a su disposición para cualquier otra consulta que pueda tener.

                    Atentamente,
                    Enrique
                    Soporte Técnico, Solutions IA"""
                # Preparar el mensaje para Mistral, ya sea con adjunto o sin él
                messages = [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": f"{promt_it}  Asunto: {subject} - {snippet}"},
                            {"type": "image_url", "image_url": f"data:image/jpeg;base64,{base64_image}" if base64_image else ""}
                        ]
                    }
                ]

                # Llamada a la API de Mistral usando requests
                mistral_url = "https://api.mistral.ai/v1/chat/completions"
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {api_key}"
                }
                data = {
                    "model": model,
                    "messages": messages,
                    "max_tokens": 2000
                }



                response = requests.post(mistral_url, headers=headers, json=data)

                if response.status_code == 200:
                    chat_response = response.json()
                    mistral_text = chat_response['choices'][0]['message']['content']
                else:
                    mistral_text = "Error en la respuesta de Mistral"
            


                # Guardar en la base de datos, incluyendo la URL si existe
                print("response",response)


                mistral_responses.append({
                    "subject": subject,
                    "snippet": snippet,
                    "mistral_response": mistral_text,
                    "id":email_id
                })

            return JsonResponse({
                'status': 'success',
                'data': mistral_responses
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)
    return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)
