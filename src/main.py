import cv2
from image_processing import BallTracking
from modbus_client import ModbusClient

addresses = {
    'Ball X': 12288,
    'Ball Y': 12290
}

if __name__ == '__main__':
    cap = cv2.VideoCapture(0)
    cap.set(propId=3, value=640)
    cap.set(propId=4, value=480)

    # Create objects

    client = ModbusClient()
    ball_tracking = BallTracking(capture=cap, watch=True, color="neon_yellow")

    while client.is_connected():
        ball_coordinates = ball_tracking.get_coordinates()
        client.write_int(value=ball_coordinates[0], address=addresses['Ball X'])
        client.write_int(value=ball_coordinates[1], address=addresses['Ball Y'])

        key = cv2.waitKey(5) & 0xFF
        if key == 27:
            ball_tracking.stop()
            break

