#!/usr/bin/env python3
import rospy
import cv2
import math
import subprocess
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
model = YOLO('/home/clover/diplovma/best.pt')  # Укажи путь к своей модели .pt

# Подключение к сервисам Clover
get_telemetry = rospy.ServiceProxy('get_telemetry', srv.GetTelemetry)
navigate = rospy.ServiceProxy('navigate', srv.Navigate)
set_velocity = rospy.ServiceProxy('set_velocity', srv.SetVelocity)
land = rospy.ServiceProxy('land', Trigger)

# Публикация скорости
vel_pub = rospy.Publisher('cmd_vel', TwistStamped, queue_size=1)

# Параметры
TARGET_CLASS = 'delamination'  # Класс, который отслеживается для управления
TARGET_HEIGHT = 4.0  # Высота полёта (м), выше дома
MAX_SPEED = 0.5  # Максимальная линейная скорость (м/с)
MAX_YAW_RATE = 1.0  # Максимальная угловая скорость (рад/с)
FRAME_WIDTH = 640  # Размер из /image_raw
FRAME_HEIGHT = 480  # Размер из /image_raw

# Параметры облёта
HOUSE_CENTER_X = 2.0  # Координаты центра дома (x)
HOUSE_CENTER_Y = 2.0  # Координаты центра дома (y)
RADIUS = 5.0  # Радиус облёта (м)
NUM_POINTS = 36  # Количество точек на траектории (одна точка каждые 10 градусов)

# Инициализация для записи видео
fourcc = cv2.VideoWriter_fourcc(*'DIVX')  # Кодек DIVX
video_writer = None  # Объект для записи видео
recording = False  # Флаг записи
video_filename = None  # Имя файла видео

def navigate_to(x, y, z, yaw=float('nan'), speed=0.5, frame_id='map'):
    navigate(x=x, y=y, z=z, yaw=yaw, speed=speed, frame_id=frame_id, auto_arm=True)
    rospy.sleep(0.5)
    while not rospy.is_shutdown():
        telem = get_telemetry()
        if math.sqrt((telem.x - x) ** 2 + (telem.y - y) ** 2 + (telem.z - z) ** 2) < 0.2:
            break
        rospy.sleep(0.1)

@long_callback
def image_callback(msg):
    global video_writer, recording, video_filename
    rospy.loginfo("Received image from /image_raw")
    
    # Конвертация ROS-изображения в OpenCV
    img = bridge.imgmsg_to_cv2(msg, 'bgr8')
    rospy.loginfo("Image converted to OpenCV format")
    
    # Проверка размера изображения
    h, w, _ = img.shape
    if w != FRAME_WIDTH or h != FRAME_HEIGHT:
        rospy.logwarn(f"Image size mismatch: expected {FRAME_WIDTH}x{FRAME_HEIGHT}, got {w}x{h}")
        return
    
    # Обработка изображения YOLO
    results = model.predict(img, conf=0.1)
    rospy.loginfo(f"YOLO results: {len(results[0].boxes)} objects detected")
    
    # Поиск и отрисовка всех объектов
    target_detected = False
    center_x, center_y = None, None
    for result in results:
        for box in result.boxes:
            detected_class = result.names[int(box.cls)]
            confidence = box.conf[0].item()
            rospy.loginfo(f"Detected class: {detected_class}, confidence: {confidence:.2f}")
            
            # Отрисовка рамки и подписи для каждого объекта
            x1, y1, x2, y2 = box.xyxy[0]
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            label = f"Damage: {detected_class} ({confidence:.2f})"
            cv2.putText(img, label, (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
            # Если это целевой класс для отслеживания, сохраняем координаты для управления
            if detected_class == TARGET_CLASS and not target_detected:
                center_x = (x1 + x2) / 2
                center_y = (y1 + y2) / 2
                target_detected = True
        
        # Глобальная подпись в верхней части кадра
        if target_detected:
            global_label = f"Detected Damage: {TARGET_CLASS} (Confidence: {confidence:.2f})"
            cv2.putText(img, global_label, (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
    
    # Записать кадр в видео, если запись активна
    if recording:
        video_writer.write(img)
        rospy.loginfo("Frame written to video")
    
    # Управление дроном
    vel_msg = TwistStamped()
    vel_msg.header.stamp = rospy.Time.now()
    
    if target_detected:
        error_x = (center_x - FRAME_WIDTH / 2) / (FRAME_WIDTH / 2)
        error_y = (center_y - FRAME_HEIGHT / 2) / (FRAME_HEIGHT / 2)
        vel_msg.twist.angular.z = -MAX_YAW_RATE * error_x
        box_area = (x2 - x1) * (y2 - y1) if x2 > x1 and y2 > y1 else 0
        if box_area < 10000:
            vel_msg.twist.linear.x = MAX_SPEED * 0.5
        else:
            vel_msg.twist.linear.x = 0.0
        rospy.loginfo(f"Tracking {TARGET_CLASS}: center=({center_x:.1f}, {center_y:.1f}), yaw_rate={vel_msg.twist.angular.z:.2f}")
    else:
        vel_msg.twist.linear.x = 0.0
        vel_msg.twist.angular.z = 0.0
        rospy.loginfo(f"{TARGET_CLASS} not detected")
    
    vel_pub.publish(vel_msg)

def main():
    global video_writer, recording, video_filename
    
    # Ожидание сервиса /navigate
    rospy.loginfo("Waiting for service /navigate...")
    try:
        rospy.wait_for_service('/navigate', timeout=30)
        rospy.loginfo("Service /navigate is available")
    except rospy.ROSException as e:
        rospy.logerr(f"Failed to find service /navigate: {e}")
        return
    
    # Ожидание сервиса /get_telemetry
    rospy.loginfo("Waiting for service /get_telemetry...")
    try:
        rospy.wait_for_service('/get_telemetry', timeout=30)
        rospy.loginfo("Service /get_telemetry is available")
    except rospy.ROSException as e:
        rospy.logerr(f"Failed to find service /get_telemetry: {e}")
        return
    
    # Взлёт
    rospy.loginfo("Taking off to 1m")
    navigate_to(x=0, y=0, z=TARGET_HEIGHT, frame_id='body')
    rospy.loginfo("Waiting for simulation to stabilize...")
    rospy.sleep(10)
    
    # Начало записи видео
    video_filename = f"/home/clover/diplovma/defect_{rospy.get_time()}.avi"
    video_writer = cv2.VideoWriter(video_filename, fourcc, 10.0, (FRAME_WIDTH, FRAME_HEIGHT))
    if not video_writer.isOpened():
        rospy.logerr("Failed to open video writer")
        return
    recording = True
    rospy.loginfo(f"Started recording video: {video_filename}")
    
    # Подписка на видеопоток
    sub = rospy.Subscriber('/image_raw', Image, image_callback, queue_size=1)
    
    # Облёт вокруг дома
    rospy.loginfo("Starting circular flight around the house")
    for i in range(NUM_POINTS):
        theta = (2 * math.pi * i) / NUM_POINTS  # Угол в радианах
        x = HOUSE_CENTER_X + RADIUS * math.cos(theta)
        y = HOUSE_CENTER_Y + RADIUS * math.sin(theta)
        z = TARGET_HEIGHT
        
        # Вычисление угла поворота (yaw), чтобы камера смотрела на центр дома
        yaw = math.atan2(HOUSE_CENTER_Y - y, HOUSE_CENTER_X - x)
        
        rospy.loginfo(f"Moving to position: x={x:.2f}, y={y:.2f}, z={z:.2f}, yaw={yaw:.2f}")
        navigate_to(x=x, y=y, z=z, yaw=yaw, speed=MAX_SPEED, frame_id='map')
    
    # Остановка записи
    if recording:
        video_writer.release()
        recording = False
        rospy.loginfo("Final video recording stopped")
    
    # Посадка
    rospy.loginfo("Landing")
    land()
    
    # Воспроизведение видео
    rospy.loginfo(f"Playing video: {video_filename}")
    try:
        subprocess.run(['mpv', video_filename], check=True)
        rospy.loginfo("Video playback completed")
    except subprocess.CalledProcessError as e:
        rospy.logerr(f"Failed to play video with mpv: {e}")
        # Попробуем VLC, если mpv не сработал
        try:
            subprocess.run(['vlc', video_filename], check=True)
            rospy.loginfo("Video playback completed with VLC")
        except subprocess.CalledProcessError as e2:
            rospy.logerr(f"Failed to play video with VLC: {e2}")
    except FileNotFoundError as e:
        rospy.logerr(f"Playback failed: {e} (ensure mpv or vlc is installed)")
    
    # Завершение
    rospy.signal_shutdown("Flight completed")
if __name__ == '__main__':
    try:
        main()
    except rospy.ROSInterruptException:
        pass