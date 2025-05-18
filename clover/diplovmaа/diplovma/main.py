
#!/usr/bin/env python3
import rospy
import cv2
import math
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
from ultralytics import YOLO
from clover import srv
from std_srvs.srv import Trigger
from geometry_msgs.msg import TwistStamped
from clover import long_callback

# Инициализация ROS
rospy.init_node('yolo_flight')
bridge = CvBridge()

# Загрузка модели YOLO
model = YOLO('best.pt')  # Укажи путь к своей модели .pt

# Подключение к сервисам Clover
get_telemetry = rospy.ServiceProxy('get_telemetry', srv.GetTelemetry)
navigate = rospy.ServiceProxy('navigate', srv.Navigate)
set_velocity = rospy.ServiceProxy('set_velocity', srv.SetVelocity)
land = rospy.ServiceProxy('land', Trigger)

# Публикация скорости
vel_pub = rospy.Publisher('cmd_vel', TwistStamped, queue_size=1)

# Параметры
TARGET_CLASS = 'person'  # Класс объекта для отслеживания (замени на нужный, например, 'marker')
TARGET_HEIGHT = 1.0  # Высота полёта (м)
MAX_SPEED = 0.5  # Максимальная линейная скорость (м/с)
MAX_YAW_RATE = 1.0  # Максимальная угловая скорость (рад/с)
FRAME_WIDTH = 320  # Ширина кадра
FRAME_HEIGHT = 240  # Высота кадра

def navigate_to(x, y, z, speed=0.5, frame_id='map'):
    navigate(x=x, y=y, z=z, yaw=float('nan'), speed=speed, frame_id=frame_id, auto_arm=True)
    rospy.sleep(0.5)
    while not rospy.is_shutdown():
        telem = get_telemetry()
        if math.sqrt((telem.x - x) ** 2 + (telem.y - y) ** 2 + (telem.z - z) ** 2) < 0.2:
            break
        rospy.sleep(0.1)

@long_callback
def forward_camera_callback(msg):
    # Конвертация ROS-изображения в OpenCV
    img = bridge.imgmsg_to_cv2(msg, 'bgr8')
    
    # Обработка изображения YOLO
    results = model.predict(img, conf=0.3)  # Пониженный порог уверенности для улучшения обнаружения
    rospy.loginfo(f"YOLO results: {len(results[0].boxes)} objects detected")
    
    # Поиск целевого объекта
    target_detected = False
    center_x, center_y = None, None
    for result in results:
        for box in result.boxes:
            detected_class = result.names[int(box.cls)]
            confidence = box.conf[0].item()
            rospy.loginfo(f"Detected class: {detected_class}, confidence: {confidence:.2f}")
            if detected_class == TARGET_CLASS:
                # Координаты bounding box
                x1, y1, x2, y2 = box.xyxy[0]
                center_x = (x1 + x2) / 2
                center_y = (y1 + y2) / 2
                target_detected = True
                break
        if target_detected:
            break
    
    # Управление дроном
    vel_msg = TwistStamped()
    vel_msg.header.stamp = rospy.Time.now()
    
    if target_detected:
        # Ошибка по X/Y (центрирование объекта в кадре)
        error_x = (center_x - FRAME_WIDTH / 2) / (FRAME_WIDTH / 2)
        error_y = (center_y - FRAME_HEIGHT / 2) / (FRAME_HEIGHT / 2)
        
        # Угловая скорость (поворот к объекту)
        vel_msg.twist.angular.z = -MAX_YAW_RATE * error_x
        
        # Линейная скорость (движение вперёд/назад)
        box_area = (x2 - x1) * (y2 - y1)
        if box_area < 10000:  # Если объект маленький (далеко)
            vel_msg.twist.linear.x = MAX_SPEED * 0.5
        else:
            vel_msg.twist.linear.x = 0.0
        
        rospy.loginfo(f"Tracking {TARGET_CLASS}: center=({center_x:.1f}, {center_y:.1f}), yaw_rate={vel_msg.twist.angular.z:.2f}")
    else:
        # Если объект потерян, остановить движение
        vel_msg.twist.linear.x = 0.0
        vel_msg.twist.angular.z = 0.0
        rospy.loginfo(f"{TARGET_CLASS} not detected")
    
    vel_pub.publish(vel_msg)


def main():
    # Взлёт
    rospy.loginfo("Taking off to 1m")
    navigate_to(x=0, y=0, z=TARGET_HEIGHT, frame_id='body')
    
    # Подписка на видеопоток с камеры, направленной вперёд
    sub = rospy.Subscriber('/image_raw', Image, forward_camera_callback, queue_size=1)  # Для симуляции
    # Для реального дрона с USB-камерой раскомментируй:
    # sub = rospy.Subscriber('/usb_cam/image_raw', Image, forward_camera_callback, queue_size=1)
    
    # Полёт в течение 60 секунд
    rospy.sleep(60)
    
    # Посадка
    rospy.loginfo("Landing")
    land()
    
    # Завершение
    rospy.signal_shutdown("Flight completed")

if __name__ == '__main__':
    try:
        main()
    except rospy.ROSInterruptException:
        pass
