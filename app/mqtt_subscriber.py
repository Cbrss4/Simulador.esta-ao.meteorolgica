import logging
from dataclasses import dataclass
from typing import Literal

import paho.mqtt.client as mqtt
from pydantic import ValidationError

from app.models import ReadingPayloadV1
from app.repository import ReadingRepository
from app.settings import Settings

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ProcessingResult:
    accepted: bool
    reading_id: int | None = None
    reading_status: Literal["valid", "partial"] | None = None
    error: str | None = None


class MqttMessageProcessor:
    """Valida e persiste uma mensagem MQTT sem depender do cliente de rede."""

    def __init__(self, repository: ReadingRepository) -> None:
        self.repository = repository

    def process(self, payload: bytes) -> ProcessingResult:
        try:
            reading = ReadingPayloadV1.model_validate_json(payload)
        except ValidationError as exc:
            error = str(exc)
            logger.warning("Mensagem MQTT rejeitada: %s", error)
            return ProcessingResult(accepted=False, error=error)

        try:
            reading_id = self.repository.save(reading)
        except Exception as exc:
            logger.exception("Falha ao persistir mensagem MQTT")
            return ProcessingResult(accepted=False, error=str(exc))

        logger.info(
            "Mensagem MQTT armazenada: id=%s status=%s device_id=%s",
            reading_id,
            reading.reading_status,
            reading.device_id,
        )
        return ProcessingResult(
            accepted=True,
            reading_id=reading_id,
            reading_status=reading.reading_status,
        )


class MqttSubscriber:
    """Assina o tópico configurado e encaminha mensagens para o processador."""

    def __init__(
        self,
        settings: Settings,
        processor: MqttMessageProcessor,
        client: mqtt.Client | None = None,
    ) -> None:
        self.settings = settings
        self.processor = processor
        self.client = client or mqtt.Client(
            callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
            client_id="weather-backend",
            protocol=mqtt.MQTTv311,
        )
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_message = self._on_message

    def _on_connect(
        self,
        client: mqtt.Client,
        userdata: object,
        flags: mqtt.ConnectFlags,
        reason_code: mqtt.ReasonCode,
        properties: mqtt.Properties | None,
    ) -> None:
        del userdata, flags, properties
        if reason_code != 0:
            logger.error("Conexão MQTT recusada: %s", reason_code)
            return

        client.subscribe(self.settings.mqtt_topic, qos=self.settings.mqtt_qos)
        logger.info(
            "Conectado ao MQTT e inscrito em %s com QoS %s",
            self.settings.mqtt_topic,
            self.settings.mqtt_qos,
        )

    def _on_disconnect(
        self,
        client: mqtt.Client,
        userdata: object,
        disconnect_flags: mqtt.DisconnectFlags,
        reason_code: mqtt.ReasonCode,
        properties: mqtt.Properties | None,
    ) -> None:
        del client, userdata, disconnect_flags, properties
        if reason_code != 0:
            logger.warning("Conexão MQTT perdida: %s", reason_code)

    def _on_message(
        self,
        client: mqtt.Client,
        userdata: object,
        message: mqtt.MQTTMessage,
    ) -> None:
        del client, userdata
        self.processor.process(message.payload)

    def run_forever(self) -> None:
        logger.info(
            "Conectando ao MQTT em %s:%s",
            self.settings.mqtt_host,
            self.settings.mqtt_port,
        )
        self.client.connect(
            self.settings.mqtt_host,
            self.settings.mqtt_port,
            self.settings.mqtt_keepalive,
        )
        self.client.loop_forever(retry_first_connection=True)


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    settings = Settings()
    repository = ReadingRepository(settings.weather_database_path)
    processor = MqttMessageProcessor(repository)
    subscriber = MqttSubscriber(settings, processor)

    try:
        subscriber.run_forever()
    except KeyboardInterrupt:
        logger.info("Assinante MQTT encerrado pelo usuário")


if __name__ == "__main__":
    main()
