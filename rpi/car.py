import cv2
import base64
import os
import RPi.GPIO as GPIO 



#переводим полученное изображение cv2 в массив байт
def encode_send(image):   
    retval, buffer = cv2.imencode('.jpg', image)
    jpg_as_byte = base64.b64encode(buffer)
    return jpg_as_byte

#разделяем строку комманд на метки(accel,brake...) и значения(1,0)
def data_recv(data):
    datasplit = data.split('*')
    data = 0
    for i in datasplit:
        str1 = datasplit[datasplit.index(i)].replace('(','')
        str2 = str1.replace(')','')
        str3 = str2.split(' ')
        if str3[0] == 'accel':
            accel = int(str3[1])
            #break
        if str3[0] == 'breake':
            breake = int(str3[1])
            #break
        if str3[0] == 'left':
            left = int(str3[1])
            # break
        if str3[0] == 'right':
            right = int(str3[1])
            #break
    return accel, breake, left, right

def print_comm(accel, breake, left, right):
    print('accel :',accel)
    print('breake :',breake)
    print('left :',left)
    print('right :',right)

#управляем моторами
def motor_control(accel, breake, left, right):
    if accel == 1:
        GPIO.output(7, 1)
        GPIO.output(11, 0)
    if breake == 1:
        GPIO.output(11, 1)
        GPIO.output(7, 0)
    if left == 1:
        GPIO.output(29, 1)
        GPIO.output(31, 0)
    if right == 1:
        GPIO.output(31, 1)
        GPIO.output(29, 0)

#считываем изображение с камеры
def camera(cap):
    success, image = cap.read()
    return image

def motors_clean(accel=0, breake=0, left=0, right=0):
    GPIO.output(7, accel)
    GPIO.output(11, breake)
    GPIO.output(29, left)
    GPIO.output(31, right)
