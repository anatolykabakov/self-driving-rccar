import numpy as np
import protocol
import handler
import socket
import base64
import cv2
import sys, tty, termios




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
        image = handler.decode_recv(data)
        image_w_m=handler.image_warp(image)
        #warp_line=handler.draw_line(image_w)
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
