import cv2
import numpy as np





def draw_lanes(img, lines, color=[0, 255, 255], thickness=3):

    # if this fails, go with some default line
    try:

        # finds the maximum y value for a lane marker 
        # (since we cannot assume the horizon will always be at the same point.)

        ys = []  
        for i in lines:
            for ii in i:
                ys += [ii[1],ii[3]]
        min_y = min(ys)
        max_y = 600
        new_lines = []
        line_dict = {}

        for idx,i in enumerate(lines):
            for xyxy in i:
                # These four lines:
                # modified from http://stackoverflow.com/questions/21565994/method-to-return-the-equation-of-a-straight-line-given-two-points
                # Used to calculate the definition of a line, given two sets of coords.
                x_coords = (xyxy[0],xyxy[2])
                y_coords = (xyxy[1],xyxy[3])
                A = np.vstack([x_coords,np.ones(len(x_coords))]).T
                m, b = np.linalg.lstsq(A, y_coords)[0]

                # Calculating our new, and improved, xs
                x1 = (min_y-b) / m
                x2 = (max_y-b) / m

                line_dict[idx] = [m,b,[int(x1), min_y, int(x2), max_y]]
                new_lines.append([int(x1), min_y, int(x2), max_y])

        final_lanes = {}

        for idx in line_dict:
            final_lanes_copy = final_lanes.copy()
            m = line_dict[idx][0]
            b = line_dict[idx][1]
            line = line_dict[idx][2]
            
            if len(final_lanes) == 0:
                final_lanes[m] = [ [m,b,line] ]
                
            else:
                found_copy = False

                for other_ms in final_lanes_copy:

                    if not found_copy:
                        if abs(other_ms*1.2) > abs(m) > abs(other_ms*0.8):
                            if abs(final_lanes_copy[other_ms][0][1]*1.2) > abs(b) > abs(final_lanes_copy[other_ms][0][1]*0.8):
                                final_lanes[other_ms].append([m,b,line])
                                found_copy = True
                                break
                        else:
                            final_lanes[m] = [ [m,b,line] ]

        line_counter = {}

        for lanes in final_lanes:
            line_counter[lanes] = len(final_lanes[lanes])

        top_lanes = sorted(line_counter.items(), key=lambda item: item[1])[::-1][:2]

        lane1_id = top_lanes[0][0]
        lane2_id = top_lanes[1][0]

        def average_lane(lane_data):
            x1s = []
            y1s = []
            x2s = []
            y2s = []
            for data in lane_data:
                x1s.append(data[2][0])
                y1s.append(data[2][1])
                x2s.append(data[2][2])
                y2s.append(data[2][3])
            return int(np.mean(x1s)), int(np.mean(y1s)), int(np.mean(x2s)), int(np.mean(y2s)) 

        l1_x1, l1_y1, l1_x2, l1_y2 = average_lane(final_lanes[lane1_id])
        l2_x1, l2_y1, l2_x2, l2_y2 = average_lane(final_lanes[lane2_id])

        return [l1_x1, l1_y1, l1_x2, l1_y2], [l2_x1, l2_y1, l2_x2, l2_y2], lane1_id, lane2_id
    except Exception as e:
        print(str(e))





    
def roi(img, vertices):
    
    #blank mask:
    mask = np.zeros_like(img)   
    
    #filling pixels inside the polygon defined by "vertices" with the fill color    
    cv2.fillPoly(mask, vertices, 255)
    
    #returning the image only where mask pixels are nonzero
    masked = cv2.bitwise_and(img, mask)
    return masked    

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
    #cv2.imshow('warp', warp)
    gray_warp = cv2.cvtColor(warp, cv2.COLOR_BGR2GRAY)
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    # define range of blue color in HSV
    lower_blue = np.array([70,50,50])
    upper_blue = np.array([120,255,255])
    # Threshold the HSV image to get only blue colors
    mask = cv2.inRange(hsv, lower_blue, upper_blue)
    #cv2.imshow('mask',mask)
    #gray = cv2.cvtColor(mask,cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(mask,50,150,apertureSize = 3)
    vertices = np.array([[0,400],[0,275],[10,280],[390,280],[400,275],[400,400],
                         ], np.int32)

    edges = roi(edges, [vertices])
    #cv2.imshow('image',edges)
    minLineLength = 10
    maxLineGap = 5
    lines = cv2.HoughLinesP(edges,1,np.pi/180,5,minLineLength,maxLineGap)
    m1 = 0
    m2 = 0
    #cv2.imshow('wwww',img)
    try:
        l1, l2, m1,m2 = draw_lanes(img,lines)
        print(m1,m2)
        cv2.line(img, (l1[0], l1[1]), (l1[2], l1[3]), [0,255,0], 30)
        cv2.line(img, (l2[0], l2[1]), (l2[2], l2[3]), [0,255,0], 30)
        #cv2.imshow('qqqq',img)
    except Exception as e:
        print(str(e))
        pass
    try:
        for coords in lines:
            coords = coords[0]
            try:
                #print('eeee')
                cv2.line(edges, (coords[0], coords[1]), (coords[2], coords[3]), [255,0,0], 3)
                
                
            except Exception as e:
                print(str(e))
    except Exception as e:
        pass
    
    return edges,img, m1, m2


if __name__ == '__main__':
    image = cv2.imread('2.png')
    
    new_screen,original_image, m1, m2 = image_warp(image)
    cv2.imshow('window', new_screen)
    #cv2.imshow('window', new_screen)

    if m1 < 0 and m2 < 0:
        print('right')
    elif m1 > 0  and m2 > 0:
        print('left')
    else:
        print('forward')
    cv2.imshow('window1',cv2.cvtColor(original_image, cv2.COLOR_BGR2RGB))
    cv2.waitKey(0)
    cv2.destroyAllWindows()


    
    
    #cv2.imshow('window',cv2.cvtColor(screen, cv2.COLOR_BGR2RGB))
     #cv2.imshow('image mask')
    #image_final = draw_lanes(org_w_p, )
    