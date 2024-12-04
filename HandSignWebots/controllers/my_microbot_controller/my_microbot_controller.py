from controller import Robot
from controller import Keyboard
import socket

robot = Robot()
timestep = int(robot.getBasicTimeStep())

left_motor = robot.getMotor("left wheel motor")
right_motor = robot.getMotor("right wheel motor")
left_motor.setPosition(float("inf"))
right_motor.setPosition(float("inf"))
left_motor.setVelocity(0.0)
right_motor.setVelocity(0.0)

udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_socket.bind(('localhost', 5005))

max_speed = 10
min_speed = 3

while robot.step(timestep) != -1:
    try:
        udp_socket.settimeout(0.1)
        data, _ = udp_socket.recvfrom(1024)
        command = data.decode()
        print(f"Received command: {command}")

        if command == "FORWARD":
            left_motor.setVelocity(-max_speed)
            right_motor.setVelocity(-max_speed)
        elif command == "REVERSE":
            left_motor.setVelocity(max_speed)
            right_motor.setVelocity(max_speed)
        elif command == "LEFT":
            left_motor.setVelocity(min_speed)
            right_motor.setVelocity(-min_speed)
        elif command == "RIGHT":
            left_motor.setVelocity(-min_speed)
            right_motor.setVelocity(min_speed)
        elif command == "STOP":
            left_motor.setVelocity(0.0)
            right_motor.setVelocity(0.0)
    except socket.timeout:
        pass
    except Exception as e:
        print(f"Error receiving data: {e}")

udp_socket.close()
