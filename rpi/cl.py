import socket, protocol # сокет и протокол(как передаем) 
import car #вычисления
import cv2
import base64
import os
import RPi.GPIO as GPIO 



if __name__ == '__main__':
    GPIO.setmode(GPIO.BOARD) 
    GPIO.setup(7, GPIO.OUT)
    GPIO.setup(11,GPIO.OUT)
    GPIO.setup(29,GPIO.OUT)
    GPIO.setup(31,GPIO.OUT)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(("10.0.48.228", 5001))
    cap = cv2.VideoCapture(0)
    cap.set(3, 1280)
    cap.set(4, 720)
    while True:      
        #обнуляем двигатели
        car.motors_clean(accel=0, breake=0, left=0, right=0)
        #получаем изображение
        image=car.camera(cap)
        #кодируем в байты
        send_data=car.encode_send(image)
        #отправляем
        protocol.send(sock, send_data)
        #получаем команды 
        data = protocol.recv(sock)
        #декодируем
        accel, breake, left, right = car.data_recv(data)
        #car.print_comm(accel, breake, left, right)# Debug
        #управляем моторами
        car.motor_control(accel, breake, left, right)

    car.motors_clean(accel=0, breake=0, left=0, right=0)
    sock.close()
    cap.release()

