import random
import time
import logging
import uuid
import requests
import qrcode
import os
import io
from decimal import Decimal
from django.conf import settings
from django.db.models import Q
from django.core.files.base import ContentFile
from ..models import Pedido, Pago, QRPredefinido

logger = logging.getLogger(__name__)

class PaymentProcessor:
    """Clase base para procesar pagos"""
    def process_payment(self, pedido_id, metodo_pago, token=None, datos=None):
        """Método abstracto para procesar pagos"""
        raise NotImplementedError("Las subclases deben implementar este método")
    
    def verify_payment(self, payment_id):
        """Método abstracto para verificar el estado de un pago"""
        raise NotImplementedError("Las subclases deben implementar este método")

class SimuladorPago(PaymentProcessor):
    """Simulador de pasarela de pagos para pruebas"""
    
    # Probabilidad de éxito del pago (90%)
    SUCCESS_RATE = 0.9
    
    # Tiempo máximo de simulación en segundos
    MAX_PROCESSING_TIME = 2
    
    def process_payment(self, pedido_id, metodo_pago, token=None, datos=None):
        """
        Simula el procesamiento de un pago y devuelve una respuesta
        similar a la que daría una pasarela de pagos real
        """
        try:
            # Obtener el pedido
            pedido = Pedido.objects.get(id=pedido_id)
            
            # Comprobar si ya existe un pago para este pedido
            if hasattr(pedido, 'pago'):
                logger.warning(f"Ya existe un pago para el pedido #{pedido_id}")
                return {
                    'success': False,
                    'error': 'Ya existe un pago para este pedido',
                    'payment_id': pedido.pago.id
                }
            
            # Crear un registro de pago
            pago = Pago.objects.create(
                pedido=pedido,
                monto=pedido.total,
                metodo_pago=metodo_pago,
                referencia=datos.get('referencia', '') if datos else ''
            )
            
            # Iniciar el procesamiento del pago
            token = pago.iniciar_pago()
            
            # Simular tiempo de procesamiento
            time.sleep(random.uniform(0.5, self.MAX_PROCESSING_TIME))
            
            # Simular resultado (éxito o fracaso según tasa de éxito)
            success = random.random() < self.SUCCESS_RATE
            
            if success:
                # Generar ID de transacción simulado
                transaction_id = f"SIM-{uuid.uuid4().hex[:10].upper()}"
                
                # Datos adicionales simulados
                additional_data = {
                    'processor': 'Simulador de Pagos',
                    'timestamp': time.time(),
                    'auth_code': f"AUTH-{random.randint(100000, 999999)}",
                    'message': 'Pago aprobado'
                }
                
                # Completar el pago
                pago.completar_pago(transaction_id, additional_data)
                
                return {
                    'success': True,
                    'payment_id': pago.id,
                    'transaction_id': transaction_id,
                    'status': 'completed',
                    'message': 'Pago procesado correctamente'
                }
            else:
                # Simular error
                error_codes = [
                    'insufficient_funds', 
                    'card_declined', 
                    'expired_card',
                    'processing_error',
                    'bank_error'
                ]
                error_code = random.choice(error_codes)
                
                # Datos del error
                error_data = {
                    'error_code': error_code,
                    'timestamp': time.time(),
                    'message': f'Error en el pago: {error_code}'
                }
                
                # Marcar como fallido
                pago.marcar_como_fallido(error_data)
                
                return {
                    'success': False,
                    'payment_id': pago.id,
                    'error': error_code,
                    'status': 'failed',
                    'message': f'Error en el procesamiento del pago: {error_code}'
                }
                
        except Pedido.DoesNotExist:
            return {
                'success': False,
                'error': 'Pedido no encontrado',
                'message': f'No se encontró el pedido con ID {pedido_id}'
            }
        except Exception as e:
            logger.error(f"Error al procesar el pago: {str(e)}")
            return {
                'success': False,
                'error': 'internal_error',
                'message': 'Error interno al procesar el pago'
            }
    
    def verify_payment(self, payment_id):
        """
        Simula la verificación del estado de un pago
        """
        try:
            pago = Pago.objects.get(id=payment_id)
            
            return {
                'success': True,
                'payment_id': pago.id,
                'status': pago.estado,
                'amount': str(pago.monto),
                'payment_method': pago.metodo_pago,
                'transaction_id': pago.id_transaccion,
                'created_at': pago.fecha_creacion.isoformat(),
                'updated_at': pago.fecha_actualizacion.isoformat()
            }
            
        except Pago.DoesNotExist:
            return {
                'success': False,
                'error': 'payment_not_found',
                'message': f'No se encontró el pago con ID {payment_id}'
            }
        except Exception as e:
            logger.error(f"Error al verificar el pago: {str(e)}")
            return {
                'success': False,
                'error': 'internal_error',
                'message': 'Error interno al verificar el pago'
            }

class QRPagoProcessor(PaymentProcessor):
    """
    Procesador para pagos mediante QR.
    Utiliza QRs predefinidos del administrador o genera dinámicamente.
    """
    def process_payment(self, pedido_id, metodo_pago, token=None, datos=None):
        try:
            # Obtener el pedido
            pedido = Pedido.objects.get(id=pedido_id)
            
            # Comprobar si ya existe un pago para este pedido
            if hasattr(pedido, 'pago'):
                logger.warning(f"Ya existe un pago para el pedido #{pedido_id}")
                return {
                    'success': False,
                    'error': 'Ya existe un pago para este pedido',
                    'payment_id': pedido.pago.id
                }
            
            # Inicializar variables para QR
            qr_instrucciones = "Escanea el código QR con tu aplicación bancaria o billetera móvil."
            qr_imagen = None
            
            # Crear un registro de pago
            pago = Pago.objects.create(
                pedido=pedido,
                monto=pedido.total,
                metodo_pago=metodo_pago,
                estado='pendiente',
                referencia=datos.get('referencia', '') if datos else '',
            )
            
            # 1. BUSCAR QR PREDEFINIDO: Intentar usar primero un QR predefinido activo
            qr_predefinido = QRPredefinido.objects.filter(activo=True).first()
            
            if qr_predefinido:
                # Usar el QR predefinido
                pago.qr_imagen.save(
                    f'qr_predefinido_{qr_predefinido.id}_{pedido.id}.png',
                    qr_predefinido.imagen,
                    save=False
                )
                
                # Generar instrucciones personalizadas con el monto
                qr_instrucciones = (
                    f"{qr_predefinido.instrucciones}\n\n"
                    f"Banco: {qr_predefinido.banco}\n"
                    f"Titular: {qr_predefinido.titular}\n"
                    f"Monto: {pedido.total} Bs\n"
                    f"Referencia: Pedido #{pedido.id}"
                )
                
                if qr_predefinido.cuenta:
                    qr_instrucciones += f"\nCuenta: {qr_predefinido.cuenta}"
                    
                pago.qr_instrucciones = qr_instrucciones
                
            # 2. REUTILIZAR QR: Si no hay predefinido, buscar uno existente reutilizable
            elif not qr_imagen:
                qr_disponible = Pago.objects.filter(
                    Q(metodo_pago=metodo_pago) & 
                    Q(qr_imagen__isnull=False) & 
                    Q(estado='completado') & 
                    ~Q(pedido__estado='pendiente') & 
                    ~Q(pedido__estado='pagado')
                ).first()
                
                if qr_disponible and qr_disponible.qr_imagen:
                    pago.qr_imagen.save(
                        f'qr_reuso_{qr_disponible.id}_{pedido.id}.png',
                        qr_disponible.qr_imagen,
                        save=False
                    )
                    
                    if qr_disponible.qr_instrucciones:
                        qr_instrucciones = qr_disponible.qr_instrucciones
                        qr_instrucciones += f"\n\nMonto a pagar: {pedido.total} Bs\nReferencia: Pedido #{pedido.id}"
                        pago.qr_instrucciones = qr_instrucciones
            
            # 3. GENERAR QR DINÁMICO: Si no hay QR predefinido ni reutilizable, generar uno dinámicamente
            if not pago.qr_imagen:
                qr_data = self._generar_datos_qr(pedido, pago)
                qr_image = self._generar_qr_imagen(qr_data)
                
                # Guardar imagen generada
                if qr_image:
                    # Convertir la imagen PIL a bytes
                    image_io = io.BytesIO()
                    qr_image.save(image_io, format='PNG')
                    image_io.seek(0)
                    
                    # Guardar en el campo qr_imagen del pago
                    file_name = f'qr_pago_{pedido_id}_{int(time.time())}.png'
                    pago.qr_imagen.save(
                        file_name,
                        ContentFile(image_io.read()),
                        save=False
                    )
                    
                    # Instrucciones específicas para el QR generado
                    qr_instrucciones = (
                        f"Escanea este código con tu aplicación bancaria o billetera móvil.\n\n"
                        f"Monto a pagar: {pedido.total} Bs\n"
                        f"Referencia: Pedido #{pedido.id}"
                    )
                    pago.qr_instrucciones = qr_instrucciones
            
            # Guardar el pago con el QR asignado
            pago.save()
            
            # Para pagos QR, dejamos el estado como pendiente hasta confirmación
            return {
                'success': True,
                'payment_id': pago.id,
                'status': 'pending',
                'qr_url': pago.qr_imagen.url if pago.qr_imagen else None,
                'instructions': qr_instrucciones,
                'message': 'Por favor, escanea el código QR para realizar el pago.'
            }
                
        except Pedido.DoesNotExist:
            return {
                'success': False,
                'error': 'Pedido no encontrado',
                'message': f'No se encontró el pedido con ID {pedido_id}'
            }
        except Exception as e:
            logger.error(f"Error al registrar el pago: {str(e)}")
            return {
                'success': False,
                'error': 'internal_error',
                'message': f'Error interno al registrar el pago: {str(e)}'
            }
    
    def _generar_datos_qr(self, pedido, pago):
        """
        Genera los datos que se codificarán en el QR.
        Por lo general, sería una URL o un código de pago específico del banco.
        """
        # En un escenario real, esto podría ser una llamada a una API bancaria
        # que devuelve un enlace de pago o un código QR
        
        # Para este ejemplo, generamos un texto con la información del pago
        qr_data = (
            f"SAGITARIO STORE - PAGO\n"
            f"ID: {pago.id}\n"
            f"PEDIDO: {pedido.id}\n"
            f"MONTO: {pedido.total} Bs\n"
            f"REF: P{pedido.id}-{int(time.time())}\n"
            f"FECHA: {time.strftime('%d/%m/%Y %H:%M')}"
        )
        
        return qr_data
    
    def _generar_qr_imagen(self, data):
        """
        Genera una imagen QR a partir de los datos proporcionados
        """
        try:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_M,
                box_size=10,
                border=4,
            )
            qr.add_data(data)
            qr.make(fit=True)
            
            # Crear la imagen del QR con un fondo blanco y código negro
            qr_image = qr.make_image(fill_color="black", back_color="white")
            
            return qr_image
        except Exception as e:
            logger.error(f"Error al generar imagen QR: {str(e)}")
            return None
    
    def verify_payment(self, payment_id):
        """
        Verifica el estado de un pago por QR
        """
        try:
            pago = Pago.objects.get(id=payment_id)
            
            # Consultar API externa si hay callback URL configurada
            if pago.api_callback_url:
                try:
                    response = requests.get(
                        pago.api_callback_url,
                        params={'payment_id': payment_id, 'amount': str(pago.monto)},
                        timeout=5
                    )
                    if response.status_code == 200:
                        data = response.json()
                        if data.get('is_paid', False):
                            pago.completar_pago(
                                id_transaccion=data.get('transaction_id', f'API-{uuid.uuid4().hex[:8]}'),
                                datos=data
                            )
                except Exception as e:
                    logger.error(f"Error al consultar API para pago {payment_id}: {str(e)}")
            
            return {
                'success': True,
                'payment_id': pago.id,
                'status': pago.estado,
                'amount': str(pago.monto),
                'payment_method': pago.metodo_pago,
                'reference': pago.referencia,
                'created_at': pago.fecha_creacion.isoformat(),
                'updated_at': pago.fecha_actualizacion.isoformat(),
                'has_qr': bool(pago.qr_imagen)
            }
            
        except Pago.DoesNotExist:
            return {
                'success': False,
                'error': 'payment_not_found',
                'message': f'No se encontró el pago con ID {payment_id}'
            }
        except Exception as e:
            logger.error(f"Error al verificar el pago: {str(e)}")
            return {
                'success': False,
                'error': 'internal_error',
                'message': 'Error interno al verificar el pago'
            }

class TransferenciaBancariaPago(PaymentProcessor):
    """
    Procesador para pagos mediante transferencia bancaria.
    En este caso, el pago es manual y debe ser verificado por un administrador.
    """
    def process_payment(self, pedido_id, metodo_pago, token=None, datos=None):
        try:
            # Obtener el pedido
            pedido = Pedido.objects.get(id=pedido_id)
            
            # Comprobar si ya existe un pago para este pedido
            if hasattr(pedido, 'pago'):
                logger.warning(f"Ya existe un pago para el pedido #{pedido_id}")
                return {
                    'success': False,
                    'error': 'Ya existe un pago para este pedido',
                    'payment_id': pedido.pago.id
                }
            
            # Crear un registro de pago
            pago = Pago.objects.create(
                pedido=pedido,
                monto=pedido.total,
                metodo_pago=metodo_pago,
                estado='pendiente',
                referencia=datos.get('referencia', '') if datos else ''
            )
            
            # Para transferencias bancarias el pago queda en estado pendiente
            # hasta que un administrador lo verifique
            
            return {
                'success': True,
                'payment_id': pago.id,
                'status': 'pending',
                'message': 'Pago registrado. Esperando confirmación del pago.'
            }
                
        except Pedido.DoesNotExist:
            return {
                'success': False,
                'error': 'Pedido no encontrado',
                'message': f'No se encontró el pedido con ID {pedido_id}'
            }
        except Exception as e:
            logger.error(f"Error al registrar el pago: {str(e)}")
            return {
                'success': False,
                'error': 'internal_error',
                'message': 'Error interno al registrar el pago'
            }
    
    def verify_payment(self, payment_id):
        """
        Verificar el estado de un pago por transferencia
        """
        try:
            pago = Pago.objects.get(id=payment_id)
            
            return {
                'success': True,
                'payment_id': pago.id,
                'status': pago.estado,
                'amount': str(pago.monto),
                'payment_method': pago.metodo_pago,
                'reference': pago.referencia,
                'created_at': pago.fecha_creacion.isoformat(),
                'updated_at': pago.fecha_actualizacion.isoformat()
            }
            
        except Pago.DoesNotExist:
            return {
                'success': False,
                'error': 'payment_not_found',
                'message': f'No se encontró el pago con ID {payment_id}'
            }
        except Exception as e:
            logger.error(f"Error al verificar el pago: {str(e)}")
            return {
                'success': False,
                'error': 'internal_error',
                'message': 'Error interno al verificar el pago'
            }

class EfectivoPago(PaymentProcessor):
    """
    Procesador para pagos en efectivo (contra entrega).
    """
    def process_payment(self, pedido_id, metodo_pago, token=None, datos=None):
        try:
            # Obtener el pedido
            pedido = Pedido.objects.get(id=pedido_id)
            
            # Comprobar si ya existe un pago para este pedido
            if hasattr(pedido, 'pago'):
                logger.warning(f"Ya existe un pago para el pedido #{pedido_id}")
                return {
                    'success': False,
                    'error': 'Ya existe un pago para este pedido',
                    'payment_id': pedido.pago.id
                }
            
            # Crear un registro de pago
            pago = Pago.objects.create(
                pedido=pedido,
                monto=pedido.total,
                metodo_pago=metodo_pago,
                estado='pendiente',  # El pago se realizará contra entrega
            )
            
            # Al ser contra entrega, el pedido sigue su curso normal
            # pero el pago queda pendiente hasta la entrega
            
            return {
                'success': True,
                'payment_id': pago.id,
                'status': 'pending',
                'message': 'Pago registrado. Se cobrará al momento de la entrega.'
            }
                
        except Pedido.DoesNotExist:
            return {
                'success': False,
                'error': 'Pedido no encontrado',
                'message': f'No se encontró el pedido con ID {pedido_id}'
            }
        except Exception as e:
            logger.error(f"Error al registrar el pago: {str(e)}")
            return {
                'success': False,
                'error': 'internal_error',
                'message': 'Error interno al registrar el pago'
            }
    
    def verify_payment(self, payment_id):
        """
        Verificar el estado de un pago en efectivo
        """
        try:
            pago = Pago.objects.get(id=payment_id)
            
            return {
                'success': True,
                'payment_id': pago.id,
                'status': pago.estado,
                'amount': str(pago.monto),
                'payment_method': pago.metodo_pago,
                'created_at': pago.fecha_creacion.isoformat(),
                'updated_at': pago.fecha_actualizacion.isoformat()
            }
            
        except Pago.DoesNotExist:
            return {
                'success': False,
                'error': 'payment_not_found', 
                'message': f'No se encontró el pago con ID {payment_id}'
            }
        except Exception as e:
            logger.error(f"Error al verificar el pago: {str(e)}")
            return {
                'success': False,
                'error': 'internal_error',
                'message': 'Error interno al verificar el pago'
            }

def get_payment_processor(metodo_pago):
    """
    Factory para obtener el procesador de pagos adecuado según el método seleccionado
    """
    processors = {
        'transferencia': TransferenciaBancariaPago(),
        'qr': QRPagoProcessor(),  # Ahora usamos el procesador específico para QR
        'efectivo': EfectivoPago(),
        'tigo_money': SimuladorPago(),  # Por ahora usamos el simulador para Tigo Money
    }
    
    return processors.get(metodo_pago, SimuladorPago())