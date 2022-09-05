#include "HX711.h"
#include <SD.h>
#include <SPI.h>

// Add a timer or clock to print the current time to obtain timestamps

// Pin definitions for the HX711 sensor
const int DOUT_1 = 3;
const int CLK_1 = 2;

const int DOUT_2 = 9;
const int CLK_2 = 8;

// Pin definitions for MicroSD card reader module
// Uses SPI communication standards
const int CS = 10;

HX711 scale_1;
HX711 scale_2;
File datafile;

long reading_1;
long reading_2; 

String base = "data";
String filename = "data.txt";
int file_num = 1;

unsigned long startTime;
unsigned long readingTime;

// If we want LED light to signal failures and initializations of the SD card, we need a separate LED since
// the built-in LED is connected to pin 13 which is used for the SPI communication

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);

  startTime = millis();
  
  delay(1000);  // Wait one second
  
  while (!SD.begin(CS)) {
    Serial.println("Initialization Failure");
  }
  SD.begin(CS);
  Serial.println("SD Card ready to write");

  scale_1.begin(DOUT_1,CLK_1);
  scale_2.begin(DOUT_2,CLK_2);
  Serial.println("Load cells 1 and 2 have been initialized");

  // Choose the gain settings to use. Channel A has gain options of 64 and 128
  scale_1.set_gain(128);
  scale_2.set_gain(128);
//  scale_1.set_gain(64);
//  scale_2.set_gain(64);
  
  // Get baseline readings. Can use to get the nominal strain
  // This is not the most accurate way to get baseline. Best approach would be to leave the dome
  // and collect the nominal value
  readingTime = millis() - startTime;
  long zero_factor_1 = scale_1.read_average(100);
  long zero_factor_2 = scale_2.read_average(100);

  Serial.print("Reading time: ");
  Serial.println(readingTime);
  Serial.print("Zero reading of scale 1: ");
  Serial.println(zero_factor_1);
  Serial.print("Zero reading of scale 2: ");
  Serial.println(zero_factor_2);
  
  if (SD.exists(filename)) {
    Serial.println("File exists. Attempting to create a new file ...");
//    filename.remove(filename.length()-4,4); // Remove extension
    filename = base + String("_") + String(file_num) + String(".txt"); // Add number to see if a new file is made
    file_num = file_num + 1;
    
    while (SD.exists(filename)) {
//      Serial.println("Backup filename already exists. Rename files");
      filename = base + String("_") + String(file_num) + String(".txt"); // Add number to see if a new file is made
      file_num = file_num + 1;
      
      delay(500);
    }
    Serial.print("New file created: ");
    Serial.println(filename);
  }
  
  datafile = SD.open(filename, FILE_WRITE);
  datafile.println("Time,Load Cell 1,Load Cell 2");  // Structure .txt file like CSV with headers
  datafile.print(readingTime);  // Print time the reading was made
  datafile.print(",");
  datafile.print(zero_factor_1);  // Print cell 1 value to SD card
  datafile.print(",");
  datafile.println(zero_factor_2);  // Print cell 2 value to SD card 
  datafile.close();

}

void loop() {
  // put your main code here, to run repeatedly:

  readingTime = millis() - startTime;
  
  reading_1 = scale_1.read();
//  reading_1 = scale_1.read_average(15); // Get the average of 15 raw readings

  reading_2 = scale_2.read();
//  reading_2 = scale_2.read_average(15); // Get the average of 15 raw readings

  Serial.print("Reading time: ");
  Serial.println(readingTime);
  
  Serial.print("Reading cell 1: ");
  Serial.println(reading_1);

  Serial.print("Reading cell 2: ");
  Serial.println(reading_2);

  Serial.flush(); // Wait for all readings to be written to the serial port 
  
  datafile = SD.open(filename, FILE_WRITE);

  if (datafile) {
    datafile.print(readingTime);
    datafile.print(",");
    datafile.print(reading_1);  // Print cell 1 value to SD card
    datafile.print(",");
    datafile.println(reading_2);  // Print cell 2 value to SD card 
    datafile.close();
  }

// If we can wire a second button into the circuit, we likely won't be able to have something send a
// terminate signal
//
//  delay(100); // Delay for 100 ms to give opportunity to send close value
//  
//  if (Serial.available() > 0) {
//    char val = Serial.read();
//    if (val == 'c' || val == 'C') {
//      datafile.close();
//      Serial.println("File now closed, please exit serial monitor");
//      while (1);
//    }
//  }
  
  delay(1000); // Pause before next reading
}
