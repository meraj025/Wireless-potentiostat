//C:\Users\Meraj\Documents\Arduino\libraries\LMP91000\LMP91000.h
//C:\Users\(username)\AppData\Local\Arduino15\packages by default.
// C:\Users\Meraj\AppData\Local\Arduino15\packages\RedBear\hardware\nRF52832\0.0.2\variants\BLE_Nano2\pin_arduino.h for pin mapping with arduino
//http://discuss.redbear.cc/t/problem-with-ftdi-and-ble-nano-v2-i2c-setup/3594
//C:\Users\Meraj\AppData\Local\Arduino15\packages\RedBear\hardware\nRF52832\0.0.2\cores\RBL_nRF52832\pin_transform.cpp contain definition
//https://fccid.io/2AKGS-MBN2/User-Manual/User-manual-3231863



#include <LMP91000.h>
#include <Wire.h>
//#include <SPI.h>
#include <BLEPeripheral.h>
#define LED_PIN 13
#define BLE_REQ -1
#define BLE_RDY -1
#define BLE_RST -1
#define DATA_LEN 8 //12

const unsigned char* LMP_REG;
uint8_t TIACN;
uint8_t REFCN;
uint8_t MODECN;

int currentState;
int debounceState;
int switchState = 0;
int ledState = 0;
unsigned char flag = 0;
unsigned int sensorVal1;
unsigned int sensorVal2;
unsigned int sensorVal3;
unsigned int sensorVal4;
//unsigned int sensorVal5;
//unsigned int sensorVal6;

//For I2C: https://github.com/redbear/nRF5x/tree/master/nRF52832/arduino/arduino-1.8.0/hardware/RBL/RBL_nRF52832/libraries/Wire

BLEPeripheral blePeripheral = BLEPeripheral(BLE_REQ, BLE_RDY, BLE_RST);
//LMPCSI LMP91000 Chemical Sensor Interface//
BLEService LMPCSI = BLEService("F0001120-0451-4000-B000-000000000000");

BLECharacteristic configLMP = BLECharacteristic("F0001121-0451-4000-B000-000000000000", BLEWrite,3);  //[TIACN,REFCN,MODECN]
BLEDescriptor configLMPDescriptor = BLEDescriptor("0001", "LMP91000 Configuration");

BLECharCharacteristic startLMP = BLECharCharacteristic("F0001122-0451-4000-B000-000000000000", BLEWrite);
BLEDescriptor startLMPDescriptor = BLEDescriptor("0001", "LMP91000 Start");

BLECharacteristic sensorOutput = BLECharacteristic("F0001123-0451-4000-B000-000000000000", BLENotify,DATA_LEN);
BLEDescriptor sensorOutputDescriptor = BLEDescriptor("0002", "LMP91000 Output");


LMP91000 lmp91000;
unsigned int i_loop;
String thisString;
unsigned char dataSend[DATA_LEN];
uint8_t res;
void setup() {
    Serial.begin(9600);
    Serial.println("LMP91000 Test");
    Wire.begin();





    pinMode(13, OUTPUT);
    digitalWrite(13, LOW);
    blePeripheral.setLocalName("LMP91000");
    blePeripheral.setDeviceName("LMP91000_");
    blePeripheral.setAdvertisedServiceUuid(LMPCSI.uuid());
    blePeripheral.addAttribute(LMPCSI);
    blePeripheral.addAttribute(configLMP);
    blePeripheral.addAttribute(configLMPDescriptor);
    blePeripheral.addAttribute(startLMP);
    blePeripheral.addAttribute(startLMPDescriptor);
    blePeripheral.addAttribute(sensorOutput);
    blePeripheral.addAttribute(sensorOutputDescriptor);
    
    configLMP.setEventHandler(BLEWritten, configLMPWritten);
    startLMP.setEventHandler(BLEWritten, startLMPWritten);
    
    blePeripheral.begin();
    Serial.println(F("LMP91000"));
    i_loop = 0;
  analogReadResolution(12);
//  analogReference(INTERNAL);




}




void loop() {
blePeripheral.poll();
delay(100);
if(flag){
//  dataSend[0] = i_loop>>8;
//  dataSend[1] = i_loop;

  sensorVal1 = analogRead(A4);
  sensorVal2 = analogRead(A0);
  sensorVal3 = analogRead(A1);
  sensorVal4 = analogRead(A5);

  
//  sensorVal5 = analogRead(A4);
//  sensorVal6 = analogRead(A5);

  dataSend[0] = sensorVal1>>8;
  dataSend[1] = sensorVal1;
  dataSend[2] = sensorVal2>>8;
  dataSend[3] = sensorVal2;
  dataSend[4] = sensorVal3>>8;
  dataSend[5] = sensorVal3;
  dataSend[6] = sensorVal4>>8;
  dataSend[7] = sensorVal4;

  
//  dataSend[8] = sensorVal5>>8;
//  dataSend[9] = sensorVal5;
//  dataSend[10] = sensorVal6>>8;
//  dataSend[11] = sensorVal6;
//  
  sensorOutput.setValue(dataSend,DATA_LEN);
//  delay(1);
  i_loop++;
}
}

void startLMPWritten(BLECentral& central, BLECharacteristic& characteristic)
{
  if(flag == 0 && startLMP.value() == 1)
  {

   // Start transmitting

  flag = 1;
  }
  else if(flag == 1 && startLMP.value() == 0) 
  {
  //  Put LMP in deep sleep mode and stop transmitting
  flag = 0;
  i_loop = 0;
  }

}

void configLMPWritten(BLECentral& central, BLECharacteristic& characteristic)
{

   // Configure the LMP
LMP_REG = configLMP.value();
TIACN = LMP_REG[0];
REFCN = LMP_REG[1];
MODECN = LMP_REG[2];


res = lmp91000.configure(TIACN,REFCN,MODECN);


    Serial.print("Config Result: ");
    Serial.println(res);
    
    Serial.print("STATUS: ");
    Serial.println(lmp91000.read(LMP91000_STATUS_REG),HEX);
    Serial.print("TIACN: ");
    Serial.println(lmp91000.read(LMP91000_TIACN_REG),HEX);
    Serial.print("REFCN: ");
    Serial.println(lmp91000.read(LMP91000_REFCN_REG),HEX);
    Serial.print("MODECN: ");
    Serial.println(lmp91000.read(LMP91000_MODECN_REG),HEX);  





Serial.println(TIACN);
Serial.println("\n");
Serial.println(REFCN);
Serial.println("\n");
Serial.println(MODECN);
Serial.println("\n");
    digitalWrite(13, HIGH);

}