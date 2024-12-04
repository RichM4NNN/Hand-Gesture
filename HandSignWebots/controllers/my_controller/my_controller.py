from controller import Robot, Keyboard, GPS, Compass, Motor
import math

# Constants
TIME_STEP = 16
TARGET_POINTS_SIZE = 13
DISTANCE_TOLERANCE = 1.5
MAX_SPEED = 7.0
TURN_COEFFICIENT = 4.0

# Define Vector class to hold 2D coordinates
class Vector:
    def __init__(self, u, v):
        self.u = u
        self.v = v

# Define target positions
targets = [
    Vector(-4.209318, 9.147717), Vector(0.946812, 9.404304), Vector(0.175989, -1.784311),
    Vector(-2.805353, -8.829694), Vector(-3.846730, -15.602851), Vector(-4.394915, -24.550777),
    Vector(-1.701877, -33.617226), Vector(-4.394915, -24.550777), Vector(-3.846730, -15.602851),
    Vector(-2.805353, -8.829694), Vector(0.175989, -1.784311), Vector(0.946812, 9.404304),
    Vector(-7.930821, 6.421292)
]

# Initialize robot and its components
robot = Robot()
motors = [robot.getDevice(f"left motor {i + 1}") for i in range(4)] + \
         [robot.getDevice(f"right motor {i + 1}") for i in range(4)]

# Initialize GPS and Compass
gps = robot.getDevice("gps")
gps.enable(TIME_STEP)
compass = robot.getDevice("compass")
compass.enable(TIME_STEP)

# Enable keyboard input
keyboard = Keyboard()
keyboard.enable(TIME_STEP)

# Robot state variables
current_target_index = 0
autopilot = True
old_autopilot = True
old_key = -1

# Set motor speed function
def robot_set_speed(left, right):
    for i in range(4):
        motors[i].setVelocity(left)
        motors[i + 4].setVelocity(right)

# Check keyboard input function
def check_keyboard():
    global autopilot, old_autopilot, old_key
    speeds = [0.0, 0.0]

    key = keyboard.getKey()
    if key >= 0:
        if key == Keyboard.UP:
            speeds[0] = MAX_SPEED
            speeds[1] = MAX_SPEED
            autopilot = False
        elif key == Keyboard.DOWN:
            speeds[0] = -MAX_SPEED
            speeds[1] = -MAX_SPEED
            autopilot = False
        elif key == Keyboard.RIGHT:
            speeds[0] = MAX_SPEED
            speeds[1] = -MAX_SPEED
            autopilot = False
        elif key == Keyboard.LEFT:
            speeds[0] = -MAX_SPEED
            speeds[1] = MAX_SPEED
            autopilot = False
        elif key == ord('P'):
            if key != old_key:  # Perform this action just once
                position_3d = gps.getValues()
                print(f"Position: {{{position_3d[0]}, {position_3d[1]}}}")
        elif key == ord('A'):
            if key != old_key:  # Perform this action just once
                autopilot = not autopilot

    if autopilot != old_autopilot:
        old_autopilot = autopilot
        print("Autopilot" if autopilot else "Manual control")

    robot_set_speed(speeds[0], speeds[1])
    old_key = key

# Main loop
while robot.step(TIME_STEP) != -1:
    check_keyboard()
    if autopilot:
        # Autopilot logic
        position_3d = gps.getValues()
        north_3d = compass.getValues()

        position = Vector(position_3d[0], position_3d[1])
        target = targets[current_target_index]

        direction = Vector(target.u - position.u, target.v - position.v)
        distance = math.sqrt(direction.u ** 2 + direction.v ** 2)

        if distance < DISTANCE_TOLERANCE:
            print(f"{current_target_index + 1} target reached")
            current_target_index = (current_target_index + 1) % TARGET_POINTS_SIZE
        else:
            robot_angle = math.atan2(north_3d[0], north_3d[1])
            target_angle = math.atan2(direction.v, direction.u)
            beta = (target_angle - robot_angle) % (2 * math.pi) - math.pi

            # Move the robot to the next target
            speeds = [MAX_SPEED - math.pi + TURN_COEFFICIENT * beta,
                      MAX_SPEED - math.pi - TURN_COEFFICIENT * beta]
            robot_set_speed(speeds[0], speeds[1])

# Cleanup (not usually reached due to the infinite loop)
robot_cleanup()
