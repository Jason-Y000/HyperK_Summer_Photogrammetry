#include "HX711.h"

//#define calibration_factor -490047
//#define calibration_factor -502268

// HX711 circuit wiring
//#define LOADCELL_DOUT_PIN  2
//#define LOADCELL_SCK_PIN  3

#define DOUT  3
#define CLK  2

HX711 scale;

void setup() {
  Serial.begin(9600);
  scale.begin(DOUT, CLK);
//  scale.set_scale(0.1); // divider
//  scale.set_offset(-1001013);  // offset
// scale.set_scale(calibration_factor);
 //scale.tare(5);

  Serial.println("HX711 Calibration");
  Serial.println("Remove all weight from scale");
  Serial.println("After readings begin, place known weight on scale");
  Serial.println("Press a,s,d,f to increase calibration factor by 10,100,1000,10000 respectively");
  Serial.println("Press z,x,c,v to decrease calibration factor by 10,100,1000,10000 respectively");
  Serial.println("Press t for tare");
 // scale.set_scale();
  //scale.tare(); //Reset the scale to 0
  scale.set_gain(64);
  long zero_factor = scale.read_average(100); //Get a baseline reading
  Serial.print("Zero factor: "); //This can be used to remove the need to tare the scale. Useful in permanent scale projects.
  Serial.println(zero_factor);

}

void loop() {
/*
  if (scale.is_ready()) {
    long reading = scale.read();
    //scale.set_gain(128);
    Serial.print("HX711 reading: ");
    Serial.println(reading);
//    Serial.println(scale.get_units(), 1);
  //  Serial.println(scale.read_average(100));
  } else {
    Serial.println("HX711 not found.");
  }
*/
 // scale.set_scale(calibration_factor); //Adjust to this calibration factor
  Serial.print("Reading: ");
  //Serial.print(scale.get_units(), 3);
  Serial.print(scale.read());
 // scale.set_gain(64);
  Serial.print(" "); //Change this to kg and re-adjust the calibration factor if you follow SI units like a sane person
  //Serial.print(" calibration_factor: ");
  //Serial.print(calibration_factor);
  Serial.println();

  
  delay(1000);

}


/*
#include "HX711.h"

//#define calibration_factor -205526.0 //This value is obtained using the SparkFun_HX711_Calibration sketch

#define DOUT  3
#define CLK  2

HX711 scale;

void setup() {
  Serial.begin(9600);
  Serial.println("HX711 scale demo");

  scale.begin(DOUT, CLK);
  //scale.set_scale(calibration_factor); //This value is obtained by using the SparkFun_HX711_Calibration sketch   scale.tare(); //Assuming there is no weight on the scale at start up, reset the scale to 0
  //scale.tare();
  //Serial.println(scale.get_units(), 1);
//  Serial.println("Readings: ");
Serial.println(scale.read());
}

void loop() {
 // float volt;
  Serial.print("\n");
//  Serial.println(scale.get_value());
//  Serial.println(scale.get_units(), 1); //scale.get_units() returns a float
//  Serial.print(" lbs"); //You can change this to kg but you'll need to refactor the calibration_factor
//  Serial.println();
//  volt = ((scale.read())*5.0)/167777216;
  //Serial.print("\t\n");
  //Serial.print(volt);
Serial.println(scale.read());

delay(1000);
}
*/
