import cv2 as cv
import numpy as np
import os # used to loop through files
import csv # used to write data to csv

# will resize the image to the monitor size to ensure the coordinates will match the x,y coords from the eye tracker
monitor_width = 1920
monitor_height = 1080

# ----------
#  Code used to find the screen position of participants:
# ----------
# use the correctCorners.csv and save it as a dataframe (df) called corners_data
corners_data = []
default_screen_pos = [438, 32]
current_participant = 1
screen_translation = [0,0]
def save_screen_pos():
    with open('./csv/correctCorners.csv') as f:
        reader = csv.reader(f, delimiter=',') 
        for row in reader:
            corners_data.append(row)
# save_screen_pos()

# checks the difference between the current participant and participant 1
def update_screen_pos(participantID):
    # print("in update_screen_pos: current Participant: ", participantID)
    for row in corners_data:
        if "subject"+str(participantID)+".png" in row[0]:
            screen_translation[0] = default_screen_pos[0] - float(row[1])
            screen_translation[1] = default_screen_pos[1] - float(row[2])
            break
    # print(screen_translation)
    
# update_screen_pos(current_participant)

# ----------
#  Code used to find eyes:
# ----------
# draw rectangles around the eyes of the participants in different angles and translations
def rects_for_eyes():
    # change the angle var to go through different test files
    angle = 315
    directory = './angles/'+str(angle)
    # directory = './angles/subject10'

    def rotate_points(img, top_left, bottom_right, color):
        # make the points into a np array
        rect_points = np.array([[top_left[0], top_left[1]], 
                                [bottom_right[0], top_left[1]], 
                                [bottom_right[0], bottom_right[1]], 
                                [top_left[0], bottom_right[1]]], dtype=np.float32)
        # rotate the points in 45 degrees over the center point
        center = ((top_left[0] + bottom_right[0]) // 2, (top_left[1] + bottom_right[1]) // 2)
        rotation_matrix = cv.getRotationMatrix2D(center, 45, 1.0)
        rotated_points = cv.transform(np.array([rect_points]), rotation_matrix)[0]
        # convert points to integer (cv.polylines only take ints)
        rotated_points = np.int32(rotated_points)
        # print("rect rotated points: ", rotated_points)
        # draw the rotated rect
        cv.polylines(img, [rotated_points], isClosed=True, color=color, thickness=3)

    # draw rects around the eyes -- default values are using participant 1 screen
    # left_eye_top_left, left_eye_bottom_right (and the vars for the right eyes) are used to find the general positions of the eyes in each angle
    # then, y_trans and x_trans are used for the different transformations
        # for example, if that the image is centered around the nose and has an angle of 315 it will have different eye positions than if it was centered on the chin
        # used trial-and-error to set the AOI for the correct rotations
    def eyes(img, angle, transformation):
        # height transformations:
        x_trans = -screen_translation[0]
        y_trans = 7 - screen_translation[1]
        y_trans_315 = -50 - screen_translation[1]
        x_trans_315 = -85 - screen_translation[0]
        x_trans_45 = 150 - screen_translation[0]
        y_trans_45 = -150 - screen_translation[1]
        if (transformation == 3):
            y_trans = 250 - screen_translation[1]
            y_trans_315 = 100 - screen_translation[1]
            x_trans_315 = 95 - screen_translation[0]
            x_trans_45 = 0 - screen_translation[0]
            y_trans_45 = 0 - screen_translation[1]
        elif (transformation == 2):
            y_trans = 115 - screen_translation[1]
            y_trans_315 = 0 - screen_translation[1]
            x_trans_315 = 0 - screen_translation[0]
            x_trans_45 = 85 - screen_translation[0]
            y_trans_45 = -85 - screen_translation[1]
        # angle transformations:
        if (angle == 0):
            # positons for a straight face
            left_eye_top_left = [932+int(x_trans),int(330+y_trans)]
            left_eye_bottom_right = [1032+int(x_trans), int(417+y_trans)]
            right_eye_top_left = [1050+int(x_trans),int(330+y_trans)]
            right_eye_bottom_right = [1150+int(x_trans), int(417+y_trans)]
            # draw boundries on eyes
            cv.rectangle(img, left_eye_top_left, left_eye_bottom_right, (255,0,0), 3)
            cv.rectangle(img, right_eye_top_left, right_eye_bottom_right, (0,255,0), 3)
        elif (angle == 45):
            # 45 degrees rotation
            left_eye_top_left = [920+x_trans_45,600+y_trans_45]
            left_eye_bottom_right = [1020+x_trans_45, 500+y_trans_45]
            right_eye_top_left = [1100+x_trans_45,580+y_trans_45]
            right_eye_bottom_right = [1000+x_trans_45, 680+y_trans_45]
            rotate_points(img, left_eye_top_left, left_eye_bottom_right, (255,0,0))
            rotate_points(img, right_eye_top_left, right_eye_bottom_right, (0,255,0))
        elif (angle == 315):
            # 315 degrees rotation
            left_eye_top_left = [900+x_trans_315,580+y_trans_315]
            left_eye_bottom_right = [1000+x_trans_315, 480+y_trans_315]
            right_eye_top_left = [980+x_trans_315,500+y_trans_315]
            right_eye_bottom_right = [1080+x_trans_315, 400+y_trans_315]
            rotate_points(img, left_eye_top_left, left_eye_bottom_right, (255,0,0))
            rotate_points(img, right_eye_top_left, right_eye_bottom_right, (0,255,0))

    # using the library to load, resize, and display the image
    def setup_image(img_path):
        img = cv.imread(img_path)
        img = cv.resize(img, (monitor_width, monitor_height))
        print(img_path)
        # use the image path to understand the angle and the translation
            # names of images are: "angleX_translation" 
            # ex. "angle315_down"
        if ("angle0" in img_path):
            angle = 0
        elif ("angle315" in img_path):
            angle = 315
        elif ("angle45" in img_path):
            angle = 45

        translation = 1
        if ("down" in img_path):
            translation = 3
        elif ("middle" in img_path):
            translation = 2
        print(angle, translation)
        eyes(img, angle, translation)
        # Displaying the image  
        cv.imshow("Display window", img)   


    # this function can be used for testing:
    # prints the coordinates and the color of where the mouse was clicked
    def click_event(event, x, y, flags, param):
        if event == cv.EVENT_LBUTTONDOWN:
            print("mouse coords: ", x, y)
            # print("color: ", img_rgb[y, x])

    # get coords for each file
    for filename in os.listdir(directory):
        f = os.path.join(directory, filename)
        if os.path.isfile(f):
            print(f)
            setup_image(f)
            cv.setMouseCallback('Display window', click_event)
            cv.waitKey(0)

# rects_for_eyes()

# return the coords of each eye
def find_eye_coords(angle, translation, participantID):
    def rotate_points(top_left, bottom_right):
        # print("in eye coords rotate points")
        # make the points into a np array
        rect_points = np.array([[top_left[0], top_left[1]], 
                                [bottom_right[0], top_left[1]], 
                                [bottom_right[0], bottom_right[1]], 
                                [top_left[0], bottom_right[1]]], dtype=np.float32)
        # rotate the points in 45 degrees over the center point
        center = ((top_left[0] + bottom_right[0]) // 2, (top_left[1] + bottom_right[1]) // 2)
        rotation_matrix = cv.getRotationMatrix2D(center, 45, 1.0)
        rotated_points = cv.transform(np.array([rect_points]), rotation_matrix)[0]
        # convert points to integer (cv.polylines only take ints)
        rotated_points = np.int32(rotated_points).tolist()
        return rotated_points
    
    def eyes(transformation, angle):
        # height transformations:
        x_trans = -screen_translation[0]
        y_trans = 7 - screen_translation[1]
        y_trans_315 = -50 - screen_translation[1]
        x_trans_315 = -85 - screen_translation[0]
        x_trans_45 = 150 - screen_translation[0]
        y_trans_45 = -150 - screen_translation[1]
        if (transformation == 3):
            y_trans = 250 - screen_translation[1]
            y_trans_315 = 100 - screen_translation[1]
            x_trans_315 = 95 - screen_translation[0]
            x_trans_45 = 0 - screen_translation[0]
            y_trans_45 = 0 - screen_translation[1]
        elif (transformation == 2):
            y_trans = 115 - screen_translation[1]
            y_trans_315 = 0 - screen_translation[1]
            x_trans_315 = 0 - screen_translation[0]
            x_trans_45 = 85 - screen_translation[0]
            y_trans_45 = -85 - screen_translation[1]
        # angle transformations:
        if (angle == 0):
            # positons for a straight face
            left_eye_top_left = [932+int(x_trans),int(330+y_trans)]
            left_eye_bottom_right = [1032+int(x_trans), int(417+y_trans)]
            right_eye_top_left = [1050+int(x_trans),int(330+y_trans)]
            right_eye_bottom_right = [1150+int(x_trans), int(417+y_trans)]
            # print(left_eye_top_left)
            # draw boundries on eyes
            return [[left_eye_top_left, left_eye_bottom_right], [right_eye_top_left, right_eye_bottom_right]]
            # cv.rectangle(img, left_eye_top_left, left_eye_bottom_right, (255,0,0), 3)
            # cv.rectangle(img, right_eye_top_left, right_eye_bottom_right, (0,255,0), 3)
        elif (angle == 45):
            # 45 degrees rotation
            left_eye_top_left = [920+x_trans_45,600+y_trans_45]
            left_eye_bottom_right = [1020+x_trans_45, 500+y_trans_45]
            right_eye_top_left = [1100+x_trans_45,580+y_trans_45]
            right_eye_bottom_right = [1000+x_trans_45, 680+y_trans_45]
            left = rotate_points(left_eye_top_left, left_eye_bottom_right)
            right = rotate_points(right_eye_top_left, right_eye_bottom_right)
            return [[left], [right]]
        elif (angle == 315):
            # 315 degrees rotation
            left_eye_top_left = [900+x_trans_315,580+y_trans_315]
            left_eye_bottom_right = [1000+x_trans_315, 480+y_trans_315]
            right_eye_top_left = [980+x_trans_315,500+y_trans_315]
            right_eye_bottom_right = [1080+x_trans_315, 400+y_trans_315]
            # print("before rotation: ", left_eye_top_left, left_eye_bottom_right)
            left = rotate_points(left_eye_top_left, left_eye_bottom_right)
            # print("after rotation: ", left)
            right = rotate_points(right_eye_top_left, right_eye_bottom_right)
            return [[left], [right]]
    
    save_screen_pos()
    update_screen_pos(participantID)
    coords = eyes(angle, translation)
    # print("coords: " , coords)
    eye_coords_left.append(coords[0])
    eye_coords_right.append(coords[1])


# ----------
#  Code used to for timing calculations:
#   trial times starts from the second trial (so trial_times[0] refers to the start and end points of the second trial)
# ----------
trial_times = [] # will hold arrays of face appears to face disappears timings, skipping the first trial
eye_coords_left = [] # will hold arrays for the AOI of the left eye, based on trial
eye_coords_right = []
buffer_instruction_disappear_time = 6.5 #- 0.0744 # the video for the first participant starts before the first trial, so I checked when the instructions disappear and the clock starts
# rt_buffer = 0.03
def read_matlab():
    prev_exp_time = 13.19
    # looks at all the files in the folder
    for filename in os.listdir("matlab_data"):
        print("file name:" + filename)
        f = os.path.join("matlab_data", filename)
        with open(f, 'r') as file:
            lines = file.readlines() 
            lines_array = []
            for line in lines:
                l = line.split(",")
                if l[1].isdigit() and float(l[1]) > 1: # ignore first trial
                    # coords
                    angle = int(l[4])
                    translation = int(l[5])
                    find_eye_coords(angle, translation, 1)
                    # timing
                    exp_time = float(l[9])
                    rt = float(l[8])
                    print("trial: " + l[1], " current exp time: " + l[9] + " rt: " + l[8] + " prev exp time: " + str(prev_exp_time))
                    # duration_of_face = exp_time - rt
                    time_before_face_appears = exp_time - prev_exp_time - rt
                    duration_of_face = exp_time - prev_exp_time - time_before_face_appears
                    print("duration of time face was on screen: ", str(duration_of_face))
                    print(" prev exp time: " + str(prev_exp_time) + " time befoer face appears: " + str(time_before_face_appears))
                    face_appears = prev_exp_time + time_before_face_appears 
                    face_disappears = face_appears + duration_of_face
                    trial_times.append([face_appears+buffer_instruction_disappear_time, face_disappears+buffer_instruction_disappear_time])
                    # print("trial times: " , trial_times)
                    prev_exp_time = float(l[9])
                # stops after the 5th trial just for testing
                if l[1].isdigit() and float(l[1]) > 5: 
                    break
                lines_array.append(l)
    # print(lines_array)
    print("trial times: ", trial_times)
    print("eye coords left: ", eye_coords_left)
    print("eye coords right: ", eye_coords_right)

    # first trial is at about 2.64
    # time between current face disappearing and the next appearing = current exp time - prev exp time - RT
    # face is on screen: prev exp trial + time between current face disappearing and the next appearing
    # face disappears: face on screen time + RT
    # instructions disappear at 6.50 (in video)

    # trial 2 starts at 19.80 (in video)
    # face appears at trial 2 at 21.50, disappears 23.10
    # problem: my code says that the face appears for 23.138-21.5744=1.5636 while the video was 23.10-21.50=1.6, and I am not sure how to account for that 

read_matlab()

def read_gazepoint():
    for filename in os.listdir("gazepoint_data"):
        # print("file name:" + filename)
        f = os.path.join("gazepoint_data", filename)
        with open(f, 'r') as file:
            flag = 0
            lines = file.readlines() 
            count = 0

            for line in lines:
                l = line.split(",")
                print("in gazepoint, l is", l)
                if (l[0] != "MEDIA_ID"):
                    print("TRIAL " , count+2)
                    time = float(l[3])
                    if (abs(trial_times[count][0] - time) < 0.5 or abs(trial_times[count][1] - time) < 0.5 or (time < trial_times[count][1] and time > trial_times[count][0])):
                        print("found a match! current time of fixation" , time, " is in time interval from matlab: ", trial_times[count][0], " and ", trial_times[count][1])
                        # get where the participant looked
                        participant_x = float(l[5])*monitor_width
                        participant_y = monitor_height - float(l[6])*monitor_height #+ 100
                        print("looking at x: ", participant_x, " y: ", participant_y)
                        # compare to AOI of the trial
                        print("left eye coords: ", eye_coords_left[count])
                        print("right eye coords: ", eye_coords_right[count])


                        isInLeftAOI = cv.pointPolygonTest(np.array(eye_coords_left[count], dtype=np.int32), [participant_x, participant_y], True)
                        isInRightAOI = cv.pointPolygonTest(np.array(eye_coords_right[count], dtype=np.int32), [participant_x, participant_y], True)
                        print("distance from left: ", isInLeftAOI, " distance from right: ", isInRightAOI)
                        if (isInLeftAOI >= -30 and isInRightAOI < -30):
                            print("participant looked at left eye!")
                        elif (isInRightAOI >= -30 and isInLeftAOI < -30):
                            print("participant looked at right eye!")
                        elif (isInRightAOI >= -30 and isInLeftAOI >= - 30):
                            print("participant looked at both eye!")
                        else:
                            print("participant looked at neither eye")
                    else:
                        if (time > trial_times[count][0]):
                            count += 1
                    if (count == 5):
                        break
read_gazepoint()
# ----------
#  Code used to find the top left corner of each window:
# ----------
def save_top_left_values():
    # in my folder, I have a folder names "images" where I will upload images of the screen for each participant
    img_path = './images/'

    # I color picked some of the sections of the figure window, and will for bluish tones in this range:
    min_target_color = [50,0,0]#[130,153,180] 
    max_target_color = [255,255,255]#[255,255,255]
    # will resize the image to the monitor size to ensure the coordinates will match the x,y coords from the eye tracker
    monitor_width = 1920
    monitor_height = 1080
    # data to be written to csv
    data = []
    data.append(["filename", "xTop", "yTop"])#, "xBottom", "yBottom"])

    # search for the top left corner
    # move from top->bottom and left->right
    def search_color_top(img_rgb):
        for y in range(img_rgb.shape[0]):
            for x in range(img_rgb.shape[1]):
                # checks for all colors in the range I declared above
                # print(x, y, img_rgb[y, x])
                if np.all(img_rgb[y, x] >= min_target_color) and np.all(img_rgb[y, x] <= max_target_color) and x<640 and x>220:
                    return (x,y)

    # search for the bottom right corner
    # move from bottom->top and right->left          
    def search_color_bottom(img_rgb):
        for y in range(img_rgb.shape[0]-1,0,-1):
            for x in range(img_rgb.shape[1]-1,0,-1):
                if np.all(img_rgb[y, x] >= min_target_color) and np.all(img_rgb[y, x] <= max_target_color) and x>600:
                    return (x,y)
    
    # using the library to load, resize, and display the image
    def setup_image(img_path):
        img = cv.imread(img_path)
        img = cv.resize(img, (monitor_width, monitor_height))
        
        ## Change image:
        # filter the image to keep only bluish tones using an hsv mask
        hsv_image = cv.cvtColor(img, cv.COLOR_BGR2HSV)
        lower_blue = np.array([178, 50, 20])  
        upper_blue = np.array([255, 255, 255]) 
        blue_mask = cv.inRange(img, lower_blue, upper_blue)
        img = cv.bitwise_and(img, hsv_image, mask=blue_mask)

        non_black_mask = cv.inRange(img, np.array([1, 1, 1]), np.array([255, 255, 255]))
        # Convert the new color to a NumPy array in BGR format
        new_color_bgr = np.array([10,10,200], dtype=np.uint8)

        # Create a new image filled with the desired color
        colored_image = np.zeros_like(img)
        colored_image[:] = new_color_bgr

        # Apply the mask to keep only the non-black pixels and change them to the new color
        img = cv.bitwise_and(img,colored_image, mask=non_black_mask)
        
        # Add the black pixels from the original image
        img = cv.bitwise_or(img, cv.bitwise_and(img, img, mask=~non_black_mask))

        cv.imshow("Display window", img)
        # the library uses BRG color space, so I am switching to RGB so it will be easier to read the code
        img_rgb = cv.cvtColor(img, cv.COLOR_BGR2RGB)
        # prints the coords + colors
        (xTop,yTop) = search_color_top(img_rgb)
        (xBottom,yBottom) = search_color_bottom(img_rgb)
        print("Top:", xTop, yTop , img_rgb[yTop, xTop]) 
        print("Bottom:", xBottom, yBottom , img_rgb[yBottom, xBottom]) 
        img = cv.circle(img, (xTop, yTop), 2, (255, 0, 0) , 2) 
        img = cv.circle(img, (xBottom, yBottom), 2, (255, 0, 0) , 2) 
        # uncomment this line to actually change the csv:
        # data.append([img_path, xTop, yTop])#, xBottom, yBottom])
        # Displaying the image  
        cv.imshow("Display window", img)   


    for filename in os.listdir(img_path):
        f = os.path.join(img_path, filename)
        if os.path.isfile(f):
            setup_image(f, 1)
            cv.setMouseCallback('Display window', click_event)
            cv.waitKey(0)


    with open('gaze5corners.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(data)
