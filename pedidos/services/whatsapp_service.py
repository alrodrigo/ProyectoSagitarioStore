import requests
import json
import logging
from django.conf import settings
from urllib.parse import quote
import os

logger = logging.getLogger(__name__)

class WhatsAppNotificationService:
    """
    Servicio para enviar notificaciones por WhatsApp a los clientes
    Utiliza la API de WhatsApp Business para enviar mensajes
    """
    
    # Configuración de la API de WhatsApp
    WHATSAPP_API_URL = "https://graph.facebook.com/v17.0/"
    
    @staticmethod
    def format_phone_number(phone):
        """
        Formatea el número de teléfono para que sea compatible con la API de WhatsApp
        Elimina caracteres especiales y asegura que tenga el formato correcto
        """
        # Eliminamos cualquier caracter que no sea un número
        clean_number = ''.join(filter(str.isdigit, phone))
        
        # Si el número no empieza con el código de país (591 para Bolivia), lo añadimos
        if not clean_number.startswith('591'):
            # Si comienza con un 6, 7 o similar (número celular boliviano), añadimos 591
            if clean_number.startswith(('6', '7', '8', '9')):
                clean_number = f"591{clean_number}"
        
        return clean_number
    
    @staticmethod
    def send_payment_confirmation(pedido):
        """
        Envía una notificación cuando el pago de un pedido ha sido confirmado
        """
        try:
            # Obtenemos el número de teléfono del usuario o de la dirección de envío
            phone = None
            if hasattr(pedido.usuario, 'perfil') and pedido.usuario.perfil.telefono:
                phone = pedido.usuario.perfil.telefono
            elif pedido.direccion_envio and pedido.direccion_envio.telefono:
                phone = pedido.direccion_envio.telefono
            
            if not phone:
                logger.warning(f"No se pudo enviar notificación WhatsApp para pedido {pedido.id}: No hay número telefónico")
                return False
            
            formatted_phone = WhatsAppNotificationService.format_phone_number(phone)
            
            # Construimos el mensaje
            mensaje = f"""*SAGITARIO STORE - Pago Confirmado*

¡Hola {pedido.usuario.first_name}!
Tu pago para el pedido *#{pedido.id}* ha sido confirmado.

*Detalles del pedido:*
- Total: Bs. {pedido.total}
- Estado: Pagado
- Fecha: {pedido.fecha_pedido.strftime('%d/%m/%Y')}

Estamos preparando tu pedido para envío. Te notificaremos cuando sea despachado.

Gracias por tu compra.
Sagitario Store
"""
            
            # Enviar el mensaje a través de la API oficial si está configurada y habilitada
            whatsapp_phone_id = settings.WHATSAPP_PHONE_NUMBER_ID
            whatsapp_token = settings.WHATSAPP_ACCESS_TOKEN
            auto_send = getattr(settings, 'WHATSAPP_AUTO_SEND', False)
            
            if auto_send and whatsapp_phone_id and whatsapp_token:
                return WhatsAppNotificationService._send_whatsapp_api(formatted_phone, mensaje, whatsapp_phone_id, whatsapp_token)
            else:
                # Modo de fallback: generar enlace para uso manual
                return WhatsAppNotificationService._generate_whatsapp_url(formatted_phone, mensaje)
            
        except Exception as e:
            logger.error(f"Error enviando notificación WhatsApp de pago: {str(e)}")
            return False
    
    @staticmethod
    def send_shipping_notification(pedido):
        """
        Envía una notificación cuando un pedido ha sido enviado
        """
        try:
            # Obtenemos el número de teléfono del usuario o de la dirección de envío
            phone = None
            if hasattr(pedido.usuario, 'perfil') and pedido.usuario.perfil.telefono:
                phone = pedido.usuario.perfil.telefono
            elif pedido.direccion_envio and pedido.direccion_envio.telefono:
                phone = pedido.direccion_envio.telefono
            
            if not phone:
                logger.warning(f"No se pudo enviar notificación WhatsApp para pedido {pedido.id}: No hay número telefónico")
                return False
            
            formatted_phone = WhatsAppNotificationService.format_phone_number(phone)
            
            # Construimos el mensaje
            mensaje = f"""*SAGITARIO STORE - Pedido Enviado*

¡Hola {pedido.usuario.first_name}!
Tu pedido *#{pedido.id}* ha sido enviado y está en camino.

*Detalles del pedido:*
- Total: Bs. {pedido.total}
- Método de envío: {pedido.metodo_envio.nombre if pedido.metodo_envio else 'No especificado'}
- Fecha de envío: {pedido.fecha_actualizacion.strftime('%d/%m/%Y')}

Puedes seguir el estado de tu pedido desde tu cuenta.

Gracias por tu preferencia.
Sagitario Store
"""
            
            # Enviar el mensaje a través de la API oficial si está configurada y habilitada
            whatsapp_phone_id = settings.WHATSAPP_PHONE_NUMBER_ID
            whatsapp_token = settings.WHATSAPP_ACCESS_TOKEN
            auto_send = getattr(settings, 'WHATSAPP_AUTO_SEND', False)
            
            if auto_send and whatsapp_phone_id and whatsapp_token:
                return WhatsAppNotificationService._send_whatsapp_api(formatted_phone, mensaje, whatsapp_phone_id, whatsapp_token)
            else:
                # Modo de fallback: generar enlace para uso manual
                return WhatsAppNotificationService._generate_whatsapp_url(formatted_phone, mensaje)
            
        except Exception as e:
            logger.error(f"Error enviando notificación WhatsApp de envío: {str(e)}")
            return False

    @staticmethod
    def send_delivery_confirmation(pedido):
        """
        Envía una notificación cuando un pedido ha sido entregado
        """
        try:
            # Obtenemos el número de teléfono
            phone = None
            if hasattr(pedido.usuario, 'perfil') and pedido.usuario.perfil.telefono:
                phone = pedido.usuario.perfil.telefono
            elif pedido.direccion_envio and pedido.direccion_envio.telefono:
                phone = pedido.direccion_envio.telefono
            
            if not phone:
                logger.warning(f"No se pudo enviar notificación WhatsApp para pedido {pedido.id}: No hay número telefónico")
                return False
            
            formatted_phone = WhatsAppNotificationService.format_phone_number(phone)
            
            # Construimos el mensaje de entrega
            mensaje = f"""*SAGITARIO STORE - Pedido Entregado*

¡Hola {pedido.usuario.first_name}!
Tu pedido *#{pedido.id}* ha sido entregado exitosamente.

¡Gracias por comprar con nosotros! Esperamos que disfrutes tus productos.
Si tienes alguna pregunta o necesitas asistencia, no dudes en contactarnos.

Sagitario Store
"""
            
            # Enviar el mensaje a través de la API oficial si está configurada y habilitada
            whatsapp_phone_id = settings.WHATSAPP_PHONE_NUMBER_ID
            whatsapp_token = settings.WHATSAPP_ACCESS_TOKEN
            auto_send = getattr(settings, 'WHATSAPP_AUTO_SEND', False)
            
            if auto_send and whatsapp_phone_id and whatsapp_token:
                return WhatsAppNotificationService._send_whatsapp_api(formatted_phone, mensaje, whatsapp_phone_id, whatsapp_token)
            else:
                # Modo de fallback: generar enlace para uso manual
                return WhatsAppNotificationService._generate_whatsapp_url(formatted_phone, mensaje)
            
        except Exception as e:
            logger.error(f"Error enviando notificación WhatsApp de entrega: {str(e)}")
            return False
    
    @staticmethod
    def send_preparation_notification(pedido):
        """
        Envía una notificación cuando un pedido está en preparación
        """
        try:
            # Obtenemos el número de teléfono del usuario o de la dirección de envío
            phone = None
            if hasattr(pedido.usuario, 'perfil') and pedido.usuario.perfil.telefono:
                phone = pedido.usuario.perfil.telefono
            elif pedido.direccion_envio and pedido.direccion_envio.telefono:
                phone = pedido.direccion_envio.telefono
            
            if not phone:
                logger.warning(f"No se pudo enviar notificación WhatsApp para pedido {pedido.id}: No hay número telefónico")
                return False
            
            formatted_phone = WhatsAppNotificationService.format_phone_number(phone)
            
            # Construimos el mensaje
            mensaje = f"""*SAGITARIO STORE - Pedido en Preparación*

¡Hola {pedido.usuario.first_name}!
Tu pedido *#{pedido.id}* está siendo preparado.

*Detalles del pedido:*
- Total: Bs. {pedido.total}
- Estado: En preparación
- Fecha de actualización: {pedido.fecha_actualizacion.strftime('%d/%m/%Y')}

Te notificaremos cuando tu pedido sea enviado.

Gracias por tu paciencia.
Sagitario Store
"""
            
            # Enviar el mensaje a través de la API oficial si está configurada y habilitada
            whatsapp_phone_id = settings.WHATSAPP_PHONE_NUMBER_ID
            whatsapp_token = settings.WHATSAPP_ACCESS_TOKEN
            auto_send = getattr(settings, 'WHATSAPP_AUTO_SEND', False)
            
            if auto_send and whatsapp_phone_id and whatsapp_token:
                return WhatsAppNotificationService._send_whatsapp_api(formatted_phone, mensaje, whatsapp_phone_id, whatsapp_token)
            else:
                # Modo de fallback: generar enlace para uso manual
                return WhatsAppNotificationService._generate_whatsapp_url(formatted_phone, mensaje)
            
        except Exception as e:
            logger.error(f"Error enviando notificación WhatsApp de preparación: {str(e)}")
            return False
    
    @staticmethod
    def _send_whatsapp_api(phone, message, phone_number_id, access_token):
        """
        Envía un mensaje a través de la API oficial de WhatsApp Business Cloud
        """
        try:
            url = f"{WhatsAppNotificationService.WHATSAPP_API_URL}{phone_number_id}/messages"
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {access_token}"
            }
            
            payload = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": phone,
                "type": "text",
                "text": {
                    "body": message
                }
            }
            
            response = requests.post(url, headers=headers, json=payload)
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Mensaje WhatsApp enviado correctamente: {result}")
                # Retornamos el ID del mensaje como confirmación
                return result.get('messages', [{}])[0].get('id', True)
            else:
                logger.error(f"Error al enviar mensaje WhatsApp: {response.status_code} - {response.text}")
                # Fallback: generar y retornar URL para envío manual
                return WhatsAppNotificationService._generate_whatsapp_url(phone, message)
                
        except Exception as e:
            logger.error(f"Error en API de WhatsApp: {str(e)}")
            # Fallback: generar y retornar URL para envío manual
            return WhatsAppNotificationService._generate_whatsapp_url(phone, message)
    
    @staticmethod
    def _generate_whatsapp_url(phone, message):
        """
        Genera una URL para abrir WhatsApp con un mensaje predefinido
        Este método se usa como fallback cuando la API oficial no está disponible
        """
        try:
            # URL base para envío de WhatsApp
            base_url = "https://api.whatsapp.com/send"
            
            # Codificamos el mensaje para que sea seguro en una URL
            encoded_message = quote(message)
            
            # Construimos la URL completa
            whatsapp_url = f"{base_url}?phone={phone}&text={encoded_message}"
            
            logger.info(f"URL de WhatsApp generada para el teléfono {phone}")
            
            return whatsapp_url
            
        except Exception as e:
            logger.error(f"Error generando URL de WhatsApp: {str(e)}")
            return None