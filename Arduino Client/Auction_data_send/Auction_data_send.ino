void(* resetFunc) (void) = 0;

int inputState[7] = {0,0,0,0,0,0,0};
String m = ",";
String Bid_team_states[7] = {"Team 1", "Team 2", "Team 3", "Team 4", "Team 5", "Team 6", "End",};
int count = 0;
int one = 0;
int x;

void setup() {
  // put your setup code here, to run once:
Serial.begin(9600);
//Serial.setTimeout(1);

}

void loop() {
  // put your main code here, to run repeatedly:



int inputValues [7];


int pin1 = digitalRead(2);
int pin2 = digitalRead(3);
int pin3 = digitalRead(4);
int pin4 = digitalRead(5);
int pin5 = digitalRead(6);
int pin6 = digitalRead(7);
int pin7 = digitalRead(8);

inputValues[0] = pin1;
inputValues[1] = pin2;
inputValues[2] = pin3;
inputValues[3] = pin4;
inputValues[4] = pin5;
inputValues[5] = pin6;
inputValues[6] = pin7;


//For loop for team identification of bidder and state doen't suport reppetative
for(int i=0; i<6; i++){
  if (inputValues[i] != inputState[i] && inputValues[i] == 1){
      Serial.println(Bid_team_states[i]);
      inputState[i] = inputValues[i];
}
  else{
    inputState[i] = inputValues[i];
    }
    }


//IF loop for Ending the bidding supports repetative nature
if (inputValues[6] != inputState[6] && inputValues[6] == 1){
      Serial.println(Bid_team_states[6]);
      inputState[6] = inputValues[6];
}
else{
  inputState[6] = inputValues[6];

  }


Serial.println("n");
delay(100);
}




























  


//Serial.println(inputValues[0] + m + inputValues[1] + m + inputValues[2]);
//delay(100);
