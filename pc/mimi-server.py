import numpy as np
import protocol
import socket
import base64
import cv2
import sys, tty, termios

def draw_line(img,lines):
    gray = cv2.cvtColor(warp,cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray,50,150,apertureSize = 3)
    #cv2.imshow('image',edges)
    minLineLength = 2
    maxLineGap = 1
    lines = cv2.HoughLinesP(edges,1,np.pi/180,5,minLineLength,maxLineGap)
    #print(lines)
    for line in lines:
        x1,y1,x2,y2 = line[0]
        cv2.line(warp,(x1,y1),(x2,y2),(100,50,50),4)

#import command_system
def getch():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch
def decode_recv(data):
    jpg_original = base64.b64decode(data)
    jpg_as_np = np.frombuffer(jpg_original, dtype=np.uint8)
    image = cv2.imdecode(jpg_as_np, flags=1)
    return image

def encode_send(char):
    accel=0
    breake=0
    left=0
    right=0
    if(char == "w"):
        accel = 1
    if(char == "s"):
        breake = 1      
    if(char == "a"):
        left = 1
    if(char == "d"):
        right = 1
    
    input1 = "(accel " +\
                 str(accel) +\
                 ")" +\
                 "*" +\
                 "(breake " +\
                 str(breake) +\
                 ")" +\
                 "*" +\
                 "(left " +\
                 str(left) +\
                 ")" +\
                 "*" +\
                 "(right " +\
                 str(right) +\
                 ")";
    data = base64.b64encode(input1.encode('utf-8'))
    return data

def image_warp(image):
    img = cv2.resize(image, (400, 400))  
    src = np.array([[82,247],[227,247],[280,360],[32,360]],np.float32)
    center_x = 150
    center_y = 250
    maxWidth, maxHeight = 400, 400
    hwratio = 11/8.5 #letter size paper
    scale = int(maxWidth/12)
    dst = np.array([
    [center_x - scale, center_y - scale*hwratio], #top left
    [center_x + scale, center_y - scale*hwratio], #top right
    [center_x + scale, center_y + scale*hwratio], #bottom right
    [center_x - scale, center_y + scale*hwratio], #bottom left
    ], dtype = "float32")
    M = cv2.getPerspectiveTransform(src, dst)
    warp =  cv2.warpPerspective(img, M, (400, 300))
    gray_warp = cv2.cvtColor(warp, cv2.COLOR_BGR2GRAY)
    hsv = cv2.cvtColor(warp, cv2.COLOR_BGR2HSV)
    # define range of blue color in HSV
    lower_blue = np.array([70,50,50])
    upper_blue = np.array([120,255,255])
    # Threshold the HSV image to get only blue colors
    mask = cv2.inRange(hsv, lower_blue, upper_blue)
    
    return mask


if __name__ == '__main__':
    host = "10.0.48.228"
    port = 5001
    #fp = StringIO()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((host, port))
        
    sock.listen(True)
    conn, addr = sock.accept()
    print("Connection from: " + str(addr))

    while(True):
        data = protocol.recv(conn)
        image = decode_recv(data)
        image_w_m=image_warp(image)
        #warp_line=draw_line(image_w)
        #cv2.imshow('image warp line',warp_line)
        cv2.imshow('image warp mask',image_w_m)
        #cv2.imshow('image original',image)
        #key = getch()
        #send_data=process_send(key)
        send_data = base64.b64encode('success'.encode('utf-8'))
        protocol.send(conn, send_data)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
