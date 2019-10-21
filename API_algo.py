# -*- coding: utf-8 -*-
import numpy as np 
import cv2 as cv
import imutils
import math

def detect_center_point(grab_image):
    
    kernel = np.ones((3,3), np.uint8)
    grab_gray = cv.cvtColor(grab_image, cv.COLOR_BGR2GRAY)
    blurred = cv.GaussianBlur(grab_gray, (5, 5), 0)
    thresh = cv.threshold(blurred, 50, 255, cv.THRESH_BINARY)[1]
    result = cv.erode(thresh, kernel, iterations = 10)
    result = cv.dilate(result, kernel, iterations = 20)
    cnts = cv.findContours(result.copy(), cv.RETR_EXTERNAL,cv.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)

    for c in cnts:
        M = cv.moments(c)
        cX = int(M["m10"] / M["m00"])
        cY = int(M["m01"] / M["m00"])
        cv.circle(grab_image.copy(), (cX, cY), 7, (0, 0, 255), -1)
        cv.putText(grab_image.copy(), "center", (cX - 20, cY - 20),cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

    edges = cv.Canny(result,50,150)
    lines = cv.HoughLinesP(edges,1,np.pi/180,50,minLineLength=0,maxLineGap=200)
    
    top_reference_distance = 1000
    bottom_reference_distance = 1000

    for line in lines:
        x1,y1,x2,y2 = line[0]
        if x1 is not None and y1 is not None and x2 is not None and y2 is not None:
            if cY > y1:
                top_line_x1, top_line_y1, top_line_x2, top_line_y2 = line[0]
                top_center_x = (top_line_x1+top_line_x2)/2
                top_center_y = (top_line_y1+top_line_y2)/2
                top_a = abs(top_center_x-cX)
                top_b = abs(top_center_y-cY)
                
                top_minimum_distance = math.sqrt((top_a*top_a)+(top_b*top_b))

                if top_reference_distance > top_minimum_distance: 
                    top_reference_distance = top_minimum_distance
                    top_line_p1_x1, top_line_p1_y1, top_line_p1_x2, top_line_p1_y2 = top_line_x1, top_line_y1, top_line_x2, top_line_y2
            elif cY < y1:

                bottom_line_x1, bottom_line_y1, bottom_line_x2, bottom_line_y2 = line[0]
                bottom_center_x = (bottom_line_x1+bottom_line_x2)/2
                bottom_center_y = (bottom_line_y1+bottom_line_y2)/2
                bottom_a = abs(bottom_center_x - cX)
                bottom_b = abs(bottom_center_y - cY)

                bottom_minimum_distance = math.sqrt((bottom_a*bottom_a)+(bottom_b*bottom_b))
                
                if bottom_reference_distance > bottom_minimum_distance: 
                    bottom_reference_distance = bottom_minimum_distance
                    bottom_line_p1_x1, bottom_line_p1_y1, bottom_line_p1_x2, bottom_line_p1_y2 = bottom_line_x1, bottom_line_y1, bottom_line_x2, bottom_line_y2
        else:
            print("Cant find line")
       

    print(top_line_p1_x1, top_line_p1_y1, top_line_p1_x2, top_line_p1_y2)
    cv.line(grab_image,(bottom_line_p1_x1, bottom_line_p1_y1),(bottom_line_p1_x2, bottom_line_p1_y2),(0,255,255),2)
    cv.line(grab_image,(top_line_p1_x1, top_line_p1_y1),(top_line_p1_x2, top_line_p1_y2),(255,255,0),2)
    cv.line(grab_image,(cX, 0),(cX, 1008),(0,255,0),2)

    # top intersaction point detect
    a1 = top_line_p1_y2 - top_line_p1_y1
    b1 = top_line_p1_x1 - top_line_p1_x2
    c1 = a1*top_line_p1_x1 + b1*top_line_p1_y1

    a2 = cY - 0
    b2 = cX - cX
    c2 = a2*cX + b2*0

    deteminate =  a1*b2 - a2*b1
    top_X = (b2*c1 - b1*c2)/deteminate
    top_Y = (a1*c2 - a2*c1)/deteminate
    
    # bottom intersaction point detect
    bottom_a1 = bottom_line_p1_y2 - bottom_line_p1_y1
    bottom_b1 = bottom_line_p1_x1 - bottom_line_p1_x2
    bottom_c1 = bottom_a1*bottom_line_p1_x1 + bottom_b1*bottom_line_p1_y1

    bottom_a2 = 1008 - cY 
    bottom_b2 = cX - cX
    bottom_c2 = bottom_a2*cX + bottom_b2*cY

    lower_deteminate =  bottom_a1*bottom_b2 - bottom_a2*bottom_b1
    bottom_X = (bottom_b2*bottom_c1 - bottom_b1*bottom_c2)/lower_deteminate; 
    bottom_Y = (bottom_a1*bottom_c2 - bottom_a2*bottom_c1)/lower_deteminate; 

    # [top info]
    # center: cX, cY
    # cross: top_X, top_Y
    # min_distance_point: line_p1_x2, line_p1_y2
    # [bottom info]
    # center: cX, cY
    # cross: bottom_X, bottom_Y
    # min_distance_point: bottom_center_x, bottom_center_y

    top_angle_height = math.atan2((cX - top_X),(0 - top_Y))
    top_angle_bottom = math.atan2((top_line_p1_x2 - top_X),(top_line_p1_y2 - top_Y))
    upper_angle = (top_angle_height-top_angle_bottom)*180/math.pi 
    print(upper_angle)

    bottom_angle_height = math.atan2((cX-bottom_X),(1008-bottom_Y))
    bottom_angle_width = math.atan2((bottom_line_p1_x2-bottom_X),(bottom_line_p1_y2-bottom_Y))
    bottom_angle = (bottom_angle_height-bottom_angle_width)*180/math.pi
    print(bottom_angle)

    check_rotate = abs(bottom_angle)+abs(upper_angle)
    distance = abs(top_Y-bottom_Y)
    print(check_rotate,distance)

    cv.imshow("imgig",grab_image)
    cv.waitKey()
    cv.destroyAllWindows()
    return check_rotate, distance, upper_angle, bottom_angle

def main(img2):
    original_img = img2
    cX = 0
    cY = 0
    (h, w) = original_img.shape[:2]
    grab_image = original_img.copy()
    rotate_angle, distance, upper_angle, bottom_angle = detect_center_point(grab_image)   
    count = 0 
    while True:    
        if abs(upper_angle) < 96 and abs(upper_angle) >= 88 and abs(bottom_angle) < 96 and abs(bottom_angle) >= 88:
            print("distance :", distance) 
            print("rotate_angle :", rotate_angle) 
            return distance          
        else:
            count += 1
            for_rotate_img = original_img.copy()
            M = cv.getRotationMatrix2D((cX,cY), -(180-rotate_angle), 1)
            rotate = cv.warpAffine(for_rotate_img, M, (w, h))
            rotate_angle, distance, upper_angle, bottom_angle = detect_center_point(rotate) 
            if count == 4:
                break

img2 = cv.imread("/home/hgh/hgh/project/test_img/test_grab.jpg")
main(img2)
        