# AL-KO Device Capabilities Reference

This document lists available data points and features that can be implemented from the AL-KO API, categorized by Home Assistant entity types.

## Currently Implemented
- ⚡ Switch: Eco Mode (`thingState.state.reported.ecoMode`)
- ⚡ Switch: Rain Sensor (`thingState.state.reported.rainSensor`)
- 🔽 Select: Operation Mode (`thingState.state.reported.operationState`)
- 📊 Sensor: Battery Level (`thingState.state.reported.batteryLevel`)
- 📊 Sensor: Operation State (`thingState.state.reported.operationState`)
- 📊 Sensor: Operation Error (`thingState.state.reported.operationError`)
- 📊 Sensor: Blade Life (`thingState.state.reported.remainingBladeLifetime`)

## Available Features by Entity Type

### Binary Sensors
- Connection Status (`thingState.state.reported.isConnected`)
- Rain Detected (`situationFlags.rainDetected`)
- Rain Allows Mowing (`situationFlags.rainAllowsMowing`)
- Frost Detected (`situationFlags.frostDetected`)
- Frost Allows Mowing (`situationFlags.frostAllowsMowing`)
- Charging Active (`situationFlags.chargerActive`)
- Charger Contact (`situationFlags.chargerContact`)
- Robot Is Active (`situationFlags.robotIsActive`)
- Bumper Triggered (`thingState.state.reported.hall.bumperTriggered`)

### Sensors
#### Number Type
- Signal Strength (`thingState.state.reported.rssi`): dB
- Battery Voltage (`thingState.state.reported.battery.voltage`): mV
- Charging Current (`thingState.state.reported.battery.chargingCurrent`): mA
- Battery Temperature (`thingState.state.reported.temperature.battery`): °C
- Motor Temperature (`thingState.state.reported.temperature.motor`): °C
- Environment Temperature (`thingState.state.reported.temperature.environment`): °C
- Rain Sensitivity (`thingState.state.reported.rainSensitivity`): 1-10
- Frost Threshold (`thingState.state.reported.frostThreshold`): °C
- Tilt Slope (`thingState.state.reported.tiltSlope`): degrees
- Remaining Duration (`thingState.state.reported.remainingDuration`): minutes
- Remaining Duration Percentage (`thingState.state.reported.remainingDurationPercentage`): %

#### Diagnostic Sensors
- Total Operation Time (`thingState.state.reported.operationTimeTotal`)
- Mowing Time (`thingState.state.reported.operationTimeMowing`)
- Wheel Motor Left Time (`thingState.state.reported.operationTimeWheelMotorLeft`)
- Wheel Motor Right Time (`thingState.state.reported.operationTimeWheelMotorRight`)
- Blade Operation Time (`thingState.state.reported.operationTimeBlade`)
- Mowing Cycles (`thingState.state.reported.mowingCycles`)
- Charging Cycles (`thingState.state.reported.chargingCycles`)

### Switches
- Frost Sensor (`thingState.state.reported.frostSensor`)
- Demo Mode (`thingState.state.reported.demoMode`)
- Margin Mowing (`thingState.state.reported.marginMowing`)
- Manual Margin Mowing (`thingState.state.reported.manualMarginMowing`)
- Mowing Strategy (`thingState.state.reported.mowingStrategy`)

### Select
- Language (`thingState.state.reported.languageSettings.selected`)
- Entry Point Selection (`thingState.state.reported.entryPoints`)
- Blade Speed (`thingState.state.reported.bladeSpeed`)

### Number
- Rain Sensitivity Setting (`thingState.state.reported.rainSensitivity`)
- Frost Threshold Setting (`thingState.state.reported.frostThreshold`)
- Boundary Overlap Setting (`thingState.state.reported.boundaryOverlap`)
- Rain Delay Setting (`thingState.state.reported.rainDelay`)
- Frost Delay Setting (`thingState.state.reported.frostDelay`)

### Calendar
- Mowing Schedule
  ```python
  thingState.state.reported.mowingWindows
  {
    'monday': {
      'window_1': {
        'activityMode': True,
        'marginMode': True,
        'startHour': 9,
        'startMinute': 0,
        'duration': 420,
        'entryPoint': 33,
        'narrowPassageMode': False
      },
      'window_2': {...}
    },
    'tuesday': {...}
  }
  ```

### Button
- Reset Blade Service (`thingState.state.reported.resetBladesService`)