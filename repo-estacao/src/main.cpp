#include <Arduino.h>
#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BME280.h>

constexpr uint8_t SDA_PIN = 21;
constexpr uint8_t SCL_PIN = 22;
constexpr uint8_t LDR_PIN = 34;
constexpr uint8_t MQ135_PIN = 35;
constexpr uint8_t RAIN_PIN = 32;
constexpr int LIMITE_CHUVA = 3000;  // abaixo disso = molhado (ajustar depois)
constexpr unsigned long INTERVALO_LEITURA_MS = 5000;

Adafruit_BME280 bme;
bool bmeDisponivel = false;

void imprimirMedida(const char* rotulo, float valor, const char* unidade,
                    float minimo, float maximo) {
  Serial.print(rotulo);
  if (isnan(valor) || valor < minimo || valor > maximo) {
    Serial.println("LEITURA INVÁLIDA");
    return;
  }

  Serial.print(valor, 2);
  Serial.print(" ");
  Serial.println(unidade);
}

void setup() {
  Serial.begin(115200);
  delay(3000);
  Serial.println("Iniciando Estação Meteorológica...");

  Wire.begin(SDA_PIN, SCL_PIN);

  // O BME280 costuma usar o endereço 0x76 ou 0x77
  bmeDisponivel = bme.begin(0x76, &Wire);
  if (!bmeDisponivel) {
    bmeDisponivel = bme.begin(0x77, &Wire);
  }
  if (!bmeDisponivel) {
    Serial.println("Aviso: BME280 não encontrado (testei 0x76 e 0x77). Confira SDA/SCL/VIN/GND.");
  } else {
    Serial.println("BME280 encontrado!");
  }

  pinMode(LDR_PIN, INPUT);
  pinMode(MQ135_PIN, INPUT);
  pinMode(RAIN_PIN, INPUT);

  Serial.println("Sensores prontos!");
}

void loop() {
  float temperatura = bmeDisponivel ? bme.readTemperature() : NAN;
  float umidade = bmeDisponivel ? bme.readHumidity() : NAN;
  float pressao = bmeDisponivel ? bme.readPressure() / 100.0F : NAN;

  int luminosidade = analogRead(LDR_PIN);
  int qualidadeAr = analogRead(MQ135_PIN);
  int chuvaBruta = analogRead(RAIN_PIN);
  bool chuvaDetectada = chuvaBruta < LIMITE_CHUVA;

  Serial.println("---- Leitura da Estação ----");
  imprimirMedida("Temperatura: ", temperatura, "°C", -40.0F, 80.0F);
  imprimirMedida("Umidade: ", umidade, "%", 0.0F, 100.0F);
  imprimirMedida("Pressão: ", pressao, "hPa", 300.0F, 1100.0F);
  Serial.print("Luminosidade (LDR, leitura bruta): ");
  Serial.println(luminosidade);
  Serial.print("Qualidade do ar (MQ-135, leitura bruta): ");
  Serial.println(qualidadeAr);
  Serial.print("Chuva (leitura bruta): ");
  Serial.println(chuvaBruta);
  Serial.print("Chuva detectada: ");
  Serial.println(chuvaDetectada ? "SIM" : "NÃO");
  Serial.println("-----------------------------");

  delay(INTERVALO_LEITURA_MS);
}