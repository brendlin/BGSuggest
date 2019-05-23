#include <string>
#include <vector>
#include "TBranch.h"

struct bgrootstruct{
  Int_t Index                        ;
  std::string Date                   ;
  std::string Time                   ;
  std::string Timestamp              ;
  std::string NewDeviceTime          ;
  Int_t       BGReading              ;
  Long64_t    LinkedBGMeterID        ;
  Float_t     TempBasalAmount        ;
  std::string TempBasalType          ;
  Float_t     TempBasalDuration      ; // in hours
  std::string BolusType              ;
  Float_t     BolusVolumeSelected    ;
  Float_t     BolusVolumeDelivered   ;
  Float_t     ProgrammedBolusDuration; // in hours
  std::string PrimeType              ;
  Float_t     PrimeVolumeDelivered   ;
  Bool_t      SuspendStart           ;
  Bool_t      Rewind                 ;
  Float_t     BWZEstimate            ;
  Int_t       BWZTargetHighBG        ;
  Int_t       BWZTargetLowBG         ;
  Float_t     BWZCarbRatio           ;
  Int_t       BWZInsulinSensitivity  ;
  Int_t       BWZCarbInput           ;
  Int_t       BWZBGInput             ;
  Float_t     BWZCorrectionEstimate  ;
  Float_t     BWZFoodEstimate        ;
  Float_t     BWZActiveInsulin       ;
/*   std::string Alarm                  ; */
  Int_t       SensorCalibrationBG    ;
  Int_t       SensorGlucose          ;   
  Float_t     ISIGValue              ;
  Float_t     DailyInsulinTotal      ;
/*   std::string RawType                ; */
/*   std::string RawValues              ; */
/*   Long64_t    RawID                  ; */
/*   Long64_t    RawUploadID            ; */
/*   Long64_t    RawSeqNum              ; */
/*   std::string RawDeviceType          ; */
  //
  // Derived variables
  //
  ULong64_t   UniversalTime          ;
  Int_t       WeekOfYear             ;
  Int_t       DayOfWeekFromMonday    ;
  Float_t     TimeOfDayFromFourAM    ;
  Int_t       HourOfDayFromFourAM    ;
  Float_t     RecentSensorISIG       ;
  Int_t       RecentSensorGlucose    ;
  Float_t     MARD                   ;
  Float_t     SensorAgeDays          ;
  Bool_t      SuspendEnd             ;
  Bool_t      TempBasalEnd           ;
};

