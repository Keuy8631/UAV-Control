from dronekit import connect, VehicleMode

print('Connecting...')
vehicle = connect("127.0.0.1:14551")

import time
from dronekit import LocationGlobalRelative
from pymavlink import mavutil
import tkinter as tk

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
    # Copter should arm in GUIDED mode
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
            0,
            0, 0,
            mavutil.mavlink.MAV_FRAME_BODY_NED,
            0b0000111111000111, #Bitmask -> 只考慮速度
            0, 0, 0,        #位置
            vx, vy, vz,     #速度
            0, 0, 0,        #加速
            0, 0)
    vehicle.send_mavlink(msg)
    vehicle.flush()

#Key event function
"""def key(event):
    if event.char == event.keysym: #-- standard keys
        if event.keysym == 'r':
            print("r pressed >> Set the vehicle to RTL")
            vehicle.mode = VehicleMode("RTL")
            
    else: #-- non standard keys
        if event.keysym == 'Up':
            set_velocity_body(vehicle, gnd_speed, 0, 0)
        elif event.keysym == 'Down':
            set_velocity_body(vehicle,-gnd_speed, 0, 0)
        elif event.keysym == 'Left':
            set_velocity_body(vehicle, 0, -gnd_speed, 0)
        elif event.keysym == 'Right':
            set_velocity_body(vehicle, 0, gnd_speed, 0)"""

#Web commond function
def web(cmd):
    if cmd == 'go' or cmd =='g':
        set_velocity_body(vehicle, gnd_speed, 0, 0)
    elif cmd == 'RTL' or cmd =='s':
        vehicle.mode = VehicleMode("RTL")
    elif cmd == 'back' or cmd =='b':
        set_velocity_body(vehicle,-gnd_speed, 0, 0)
    elif cmd == 'right' or cmd =='r':
        set_velocity_body(vehicle, 0, gnd_speed, 0)
    elif cmd == 'left' or cmd =='l':
        set_velocity_body(vehicle, 0, -gnd_speed, 0)
    


#起飛高度
arm_and_takeoff(5)

#利用tkinter讀取鍵盤
"""root = tk.Tk()
root.title('無人機控制介面')
root.geometry('275x250')
root.configure(background='white')
header_label = tk.Label(root,text='方向鍵')
header_label.pack()

button1 = tk.Button(root,text='⬆')
button2 = tk.Button(root,text='⬇')
button3 = tk.Button(root,text='⬅')
button4 = tk.Button(root,text='➡')
button1.pack(side='top')
button2.pack(side='bottom')
button3.pack(side='left')
button4.pack(side='right')

print(">> Control the drone with the arrow keys. Press r for RTL mode")
root.bind_all('<Key>', key)
root.mainloop()"""