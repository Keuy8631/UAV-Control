from flask import Flask,render_template
from dronekit import connect,VehicleMode,LocationGlobalRelative
from pymavlink import mavutil
import time

print('Connecting...')
vehicle = connect("127.0.0.1:14551")

#設定飛行速度
gnd_speed = 5 #(m/s)

#定義飛機狀態
def arm_and_takeoff(aTargetAltitude):
    """
    Arms vehicle and fly to aTargetAltitude.
    """
    print("Basic pre-arm checks")
    # Don't try to arm until autopilot is ready
    while not vehicle.is_armable:
        print(" Waiting for vehicle to initialise...")
        time.sleep(1)

    print("Arming motors")
    # Copter should arm in "GUIDED" mode
    vehicle.mode = VehicleMode("GUIDED")
    vehicle.armed = True

    # Confirm vehicle armed before attempting to take off
    while not vehicle.armed:
        print(" Waiting for arming...")
        time.sleep(1)

    print("Taking off!")
    vehicle.simple_takeoff(aTargetAltitude)  # Take off to target altitude

    # Wait until the vehicle reaches a safe height before processing the goto
    #  (otherwise the command after Vehicle.simple_takeoff will execute immediately).
    while True:
        print(" Altitude: ", vehicle.location.global_relative_frame.alt)
        # Break and return from function just below target altitude.
        if vehicle.location.global_relative_frame.alt >= aTargetAltitude * 0.95:
            print("Reached target altitude")
            break
        time.sleep(1)

#Define the function for sending mavlink velocity command in body frame
def set_velocity_body(vehicle, vx, vy, vz):
    msg = vehicle.message_factory.set_position_target_local_ned_encode(
            0,      #time_boot_ms
            0, 0,   #target system,target component
            mavutil.mavlink.MAV_FRAME_BODY_NED, #frame(此為forward/backward/left/right control)
            0b0000111111000111, #Bitmask(使能速度控制or位置控制) -> 只使能控制速度
            0, 0, 0,        #x,y,z位置(not use)
            vx, vy, vz,     #x,y,z速度(m/s)
            0, 0, 0,        #x,y,z加速(not use)
            0, 0)           #yaw軸角度,yaw軸加速度
    vehicle.send_mavlink(msg)
    vehicle.flush()

def web(cmd):
    if cmd == 'go' :
        set_velocity_body(vehicle, gnd_speed, 0, 0)
    elif cmd == 'RTL' :
        vehicle.mode = VehicleMode("RTL")
    elif cmd == 'back' :
        set_velocity_body(vehicle,-gnd_speed, 0, 0)
    elif cmd == 'right' :
        set_velocity_body(vehicle, 0, gnd_speed, 0)
    elif cmd == 'left' :
        set_velocity_body(vehicle, 0, -gnd_speed, 0)

arm_and_takeoff(3) #起飛高度

app = Flask(__name__)

@app.route('/')
@app.route('/<cmd>')
def key(cmd=None):
    if cmd == 'go':
        web('go')
        print('go')
    elif cmd == 'RTL':
        web('RTL')
        print('RTL')
    elif cmd == 'back':
        web('back')
        print('back')
    elif cmd == 'right':
        web('right')
        print('right')
    elif cmd == 'left':
        web('left')
        print('left')
    return render_template("control.html",cmd=cmd)

if __name__ == "__main__":
    app.run(host="0.0.0.0",port=3000,debug=True)
