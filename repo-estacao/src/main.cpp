#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BME280.h>

#define LDR_PIN     34
#define MQ135_PIN   35
#define RAIN_PIN    32

Adafruit_BME280 bme;

void setup() {
  Serial.begin(115200);
  delay(1000);
  Serial.println("Iniciando Estação Meteorológica...");

  if (!bme.begin(0x76)) {
    Serial.println("Erro: BME280 não encontrado. Verifique a conexão I2C.");
    while (1) delay(10);
  }

  pinMode(LDR_PIN, INPUT);
  pinMode(MQ135_PIN, INPUT);
  pinMode(RAIN_PIN, INPUT);

  Serial.println("Sensores prontos!");
}

void loop() {
  float temperatura = bme.readTemperature();
  float umidade = bme.readHumidity();
  float pressao = bme.readPressure() / 100.0F; // Pa -> hPa

  int luminosidade = analogRead(LDR_PIN);
  int qualidadeAr = analogRead(MQ135_PIN);
  int chuva = digitalRead(RAIN_PIN);

  Serial.println("---- Leitura da Estação ----");
  Serial.print("Temperatura: "); Serial.print(temperatura); Serial.println(" °C");
  Serial.print("Umidade: "); Serial.print(umidade); Serial.println(" %");
  Serial.print("Pressão: "); Serial.print(pressao); Serial.println(" hPa");
  Serial.print("Luminosidade (LDR): "); Serial.println(luminosidade);
  Serial.print("Qualidade do ar (MQ-135): "); Serial.println(qualidadeAr);
  Serial.print("Chuva detectada: "); Serial.println(chuva == LOW ? "SIM" : "NÃO");
  Serial.println("-----------------------------");

  delay(2000);
}
