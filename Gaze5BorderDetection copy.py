import cv2 as cv
import numpy as np
import os # used to loop through files
import csv # used to write data to csv
import sys
from collections import defaultdict

# will resize the image to the monitor size to ensure the coordinates will match the x,y coords from the eye tracker
monitor_width = 1680
monitor_height = 1050

output_file = open('./output.txt', 'w')
sys.stdout = output_file

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
    angle_path = 45
    directory = './angles/'+str(angle_path)
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
        cv.polylines(img, [rotated_points], isClosed=True, color=color, thickness=3)    # draw rects around the eyes -- default values are using participant 1 screen
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
            y_trans_315 = 95 - screen_translation[1]
            x_trans_315 = 65 - screen_translation[0]
            x_trans_45 = 0 - screen_translation[0]
            y_trans_45 = 0 - screen_translation[1]
        elif (transformation == 2):
            y_trans = 115 - screen_translation[1]
            y_trans_315 = 15 - screen_translation[1]
            x_trans_315 = -10 - screen_translation[0]
            x_trans_45 = 85 - screen_translation[0]
            y_trans_45 = -85 - screen_translation[1]
        # angle transformations:
        if (angle == 0):
            # positons for a straight face
            left_eye_top_left = [810+int(x_trans),int(313+y_trans)]
            left_eye_bottom_right = [910+int(x_trans), int(400+y_trans)]
            right_eye_top_left = [928+int(x_trans),int(313+y_trans)]
            right_eye_bottom_right = [1028+int(x_trans), int(400+y_trans)]
            # draw boundries on eyesi
            cv.rectangle(img, left_eye_top_left, left_eye_bottom_right, (255,0,0), 3)
            cv.rectangle(img, right_eye_top_left, right_eye_bottom_right, (0,255,0), 3)
        elif (angle == 45):
            # 45 degrees rotation
            left_eye_top_left = [780+x_trans_45,590+y_trans_45]
            left_eye_bottom_right = [880+x_trans_45, 490+y_trans_45]
            right_eye_top_left = [960+x_trans_45,570+y_trans_45]
            right_eye_bottom_right = [860+x_trans_45, 670+y_trans_45]
            rotate_points(img, left_eye_top_left, left_eye_bottom_right, (255,0,0))
            rotate_points(img, right_eye_top_left, right_eye_bottom_right, (0,255,0))
        elif (angle == 315):
            # 315 degrees rotation
            left_eye_top_left = [800+x_trans_315,570+y_trans_315]
            left_eye_bottom_right = [900+x_trans_315, 470+y_trans_315]
            right_eye_top_left = [880+x_trans_315,490+y_trans_315]
            right_eye_bottom_right = [980+x_trans_315, 390+y_trans_315]
            rotate_points(img, left_eye_top_left, left_eye_bottom_right, (255,0,0))
            rotate_points(img, right_eye_top_left, right_eye_bottom_right, (0,255,0))

    # using the library to load, resize, and display the image
    def setup_image(img_path):
        img = cv.imread(img_path)
        img = cv.resize(img, (monitor_width, monitor_height))
        print("img path in setup image: ", img_path)
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
            y_trans_315 = 95 - screen_translation[1]
            x_trans_315 = 65 - screen_translation[0]
            x_trans_45 = 0 - screen_translation[0]
            y_trans_45 = 0 - screen_translation[1]
        elif (transformation == 2):
            y_trans = 115 - screen_translation[1]
            y_trans_315 = 15 - screen_translation[1]
            x_trans_315 = -10 - screen_translation[0]
            x_trans_45 = 85 - screen_translation[0]
            y_trans_45 = -85 - screen_translation[1]
        # angle transformations:
        if (angle == 0):
            # positons for a straight face
            left_eye_top_left = [810+int(x_trans),int(313+y_trans)]
            left_eye_bottom_right = [910+int(x_trans), int(400+y_trans)]
            right_eye_top_left = [928+int(x_trans),int(313+y_trans)]
            right_eye_bottom_right = [1028+int(x_trans), int(400+y_trans)]
            # print(left_eye_top_left)
            # draw boundries on eyes
            return [[left_eye_top_left, left_eye_bottom_right], [right_eye_top_left, right_eye_bottom_right]]
            # cv.rectangle(img, left_eye_top_left, left_eye_bottom_right, (255,0,0), 3)
            # cv.rectangle(img, right_eye_top_left, right_eye_bottom_right, (0,255,0), 3)
        elif (angle == 45):
            # 45 degrees rotation
            left_eye_top_left = [780+x_trans_45,590+y_trans_45]
            left_eye_bottom_right = [880+x_trans_45, 490+y_trans_45]
            right_eye_top_left = [960+x_trans_45,570+y_trans_45]
            right_eye_bottom_right = [860+x_trans_45, 670+y_trans_45]
            left = rotate_points(left_eye_top_left, left_eye_bottom_right)
            right = rotate_points(right_eye_top_left, right_eye_bottom_right)
            return [[left], [right]]
        elif (angle == 315):
            # 315 degrees rotation
            left_eye_top_left = [800+x_trans_315,570+y_trans_315]
            left_eye_bottom_right = [900+x_trans_315, 470+y_trans_315]
            right_eye_top_left = [880+x_trans_315,490+y_trans_315]
            right_eye_bottom_right = [980+x_trans_315, 390+y_trans_315]
            left = rotate_points(left_eye_top_left, left_eye_bottom_right)
            right = rotate_points(right_eye_top_left, right_eye_bottom_right)
            return [[left], [right]]
    
    save_screen_pos()
    update_screen_pos(participantID)
    # print("angle: ", angle, " translation: ", translation)
    coords = eyes(translation, angle)
    # print("coords: " , coords)
    eye_coords_left.append(coords[0])
    eye_coords_right.append(coords[1])
    # print("0 of eye coords:" ,eye_coords_left[0], eye_coords_right[0])


# ----------
#  Code used to for timing calculations:
#   trial times starts from the second trial (so trial_times[0] refers to the start and end points of the second trial)
# ----------
trial_times = [] # will hold arrays of face appears to face disappears timings, skipping the first trial
eye_coords_left = [] # will hold arrays for the AOI of the left eye, based on trial
eye_coords_right = []
angles_prop = []
translations_prop = []
prop_dict = defaultdict(lambda: defaultdict(int))
total_prop_dict = defaultdict(lambda: defaultdict(int))
time_spend_per_trial_list = []

# the video for the first participant starts before the first trial, so I checked when the instructions disappear and the clock starts
# buffer_instruction_disappear_times = [6.5]#[6.5, 13.4, 5.5]  
trial_2_start = [19.8, 31.9, 13.00, 9.9, 20.30, 14.0, 25.8, 8.0, 21.9, 10.0, 14.0, 26.60, 19.6, 38.80, 10.2, 75.8, 43.70, 20.80, 80.7, 11.9, 18.3, 46.5, 14.2]
# rt_buffer = 0.03

# vars used to write to the output files
    # first fixation by trial 
first_fixation_header = ["participant", "trial", "first eye fixation", "angle", "translation"]
first_fixation_data = []
    # proportion based on angle + height
proportion_header = ["participant", "angle", "height", "proportion"]
proportion_data = [""]
    # left vs right proportion in each trial
time_spent_on_left_in_trial_header = ["participant", "trial", "proportion to left eye", "angle", "translation"]
time_spent_on_left_in_trial_data = []



def read_matlab(f, participant_num):
    trial_times.clear()
    eye_coords_left.clear()
    eye_coords_right.clear()
    angles_prop.clear()
    translations_prop.clear()
    # looks at all the files in the folder
    # for filename in os.listdir("matlab_data"):
    #     print("file name:" + filename)
    #     f = os.path.join("matlab_data", filename)
    with open(f, 'r') as file:
        participant_index = participants.index(participant_num)
        #buffer_instruction_disappear_time = buffer_instruction_disappear_times[participant_index]
        lines = file.readlines() 
        lines_array = []
        
        for line in lines:
            l = line.split(",")
            # gets when the first trial ended
            if l[1].isdigit() and float(l[1]) == 1:
                prev_exp_time = float(l[9])
                buffer_instruction_disappear_time = trial_2_start[participant_index] - prev_exp_time
                print("buffer: ", buffer_instruction_disappear_time, " trial 2 start: ", trial_2_start[participant_index], " prev exp: ", prev_exp_time)
            if l[1].isdigit() and float(l[1]) > 1: # ignore first trial
                print (prev_exp_time)
                # timing
                exp_time = float(l[9])
                rt = float(l[8])
                print("trial: " + l[1], " current exp tme: " + l[9] + " rt: " + l[8] + " prev exp time: " + str(prev_exp_time))
                # duration_of_face = exp_time - rt
                time_before_face_appears = exp_time - prev_exp_time - rt
                duration_of_face = exp_time - prev_exp_time - time_before_face_appears
                print("duration of time face was on screen: ", str(duration_of_face))
                print(" prev exp time: " + str(prev_exp_time) + " time befoer face appears: " + str(time_before_face_appears))
                face_appears = prev_exp_time + time_before_face_appears  #1.8239
                face_disappears = face_appears + duration_of_face
                trial_times.append([face_appears+buffer_instruction_disappear_time, face_disappears+buffer_instruction_disappear_time])
                #video: trial 2 starts : 31.9, face appears: 33.6, time before face: 1.7
                # coords
                angle = int(l[5])
                translation = int(l[6])
                angles_prop.append(angle)
                translations_prop.append(translation)
                find_eye_coords(angle, translation, participant_num)

                # print("trial times: " , trial_times)
                prev_exp_time = float(l[9])
            # stops after the 5th trial just for testing
            # if l[1].isdigit() and float(l[1]) > 15: 
            #     break
            lines_array.append(l)
    # print(lines_array)
    print("trial times: ", trial_times)
    print("eye coords left: ", eye_coords_left)
    print("eye coords right: ", eye_coords_right)
    print("all angles: " , angles_prop)
    print("all translations: ", translations_prop)

    # first trial is at about 2.64
    # time between current face disappearing and the next appearing = current exp time - prev exp time - RT
    # face is on screen: prev exp trial + time between current face disappearing and the next appearing
    # face disappears: face on screen time + RT
    # instructions disappear at 6.50 (in video)

    # trial 2 starts at 19.80 (in video)
    # face appears at trial 2 at 21.50, disappears 23.10
    # problem: my code says that the face appears for 23.138-21.5744=1.5636 while the video was 23.10-21.50=1.6, and I am not sure how to account for that 

# read_matlab()

def read_gazepoint(f, participant_num):
    # for filename in os.listdir("gazepoint_data"):
    #     # print("file name:" + filename)
    #     f = os.path.join("gazepoint_data", filename)
    with open(f, 'r') as file:
        flag = 0
        lines = file.readlines() 
        count = 0
        trial_line_count = 0
        for line in lines:
            l = line.split(",")
            print("in gazepoint, current line is", l)
            if (l[0] != "MEDIA_ID"):
                print("TRIAL " , count+2)
                time = float(l[3])
                if (abs(trial_times[count][0] - time) < 0.1 or abs(trial_times[count][1] - time) < 0.1 or (time < trial_times[count][1] and time > trial_times[count][0])):
                    trial_line_count += 1
                    print("found a match! current time of fixation" , time, " is in time interval from matlab: ", trial_times[count][0], " and ", trial_times[count][1])
                    # get where the participant looked
                    participant_x = float(l[5])*monitor_width
                    participant_y = float(l[6])*monitor_height#+100
                    print("looking at x: ", participant_x, " y: ", participant_y)
                    # compare to AOI of the trial
                    print("left eye coords: ", eye_coords_left[count])
                    print("right eye coords: ", eye_coords_right[count])
                    left_eye_coords = np.array(eye_coords_left[count]).reshape(-1, 2)
                    right_eye_coords = np.array(eye_coords_right[count]).reshape(-1, 2)

                    
                    
                    # Calculate centers of the eyes
                    left_eye_center = np.mean(left_eye_coords, axis=0)
                    right_eye_center = np.mean(right_eye_coords, axis=0)
                    print("Left eye center:", left_eye_center)  # This should print [x, y] coordinates
                    print("Right eye center:", right_eye_center)
                    # Calculate Euclidean distances
                    distance_to_left = np.sqrt((participant_x - left_eye_center[0])**2 + (participant_y - left_eye_center[1])**2)
                    distance_to_right = np.sqrt((participant_x - right_eye_center[0])**2 + (participant_y - right_eye_center[1])**2)
                    print("dist to left: ", distance_to_left, " dist to right: ", distance_to_right)
                    
                    isLeftEye = -1 # -1 = neither, 1 = left, 0 = right, 2 = both
                    AOIdist = 90
                    if (distance_to_right <= AOIdist and distance_to_left <= AOIdist):
                        print("participant looked at both eye!")
                        isLeftEye = 2
                    elif (distance_to_left <= AOIdist and distance_to_right > AOIdist):
                        print("participant looked at left eye!")
                        isLeftEye = 1
                    elif (distance_to_right <= AOIdist and distance_to_left > AOIdist):
                        print("participant looked at right eye!")
                        isLeftEye = 0
                    else:
                        print("participant looked at neither eye")


                    # isInLeftAOI = cv.pointPolygonTest(np.array(eye_coords_left[count], dtype=np.int32), [participant_x, participant_y], True)
                    # isInRightAOI = cv.pointPolygonTest(np.array(eye_coords_right[count], dtype=np.int32), [participant_x, participant_y], True)
                    # print("distance from left: ", isInLeftAOI, " distance from right: ", isInRightAOI)
                    # AOIdist = 40
                    # isLeftEye = -1 # -1 = neither, 1 = left, 0 = right, 2 = both
                    # if (isInRightAOI >= -AOIdist and isInLeftAOI >= -AOIdist):
                    #     print("participant looked at both eye!")
                    #     isLeftEye = 2
                    # elif (isInLeftAOI >= -AOIdist and isInRightAOI < -AOIdist):
                    #     print("participant looked at left eye!")
                    #     isLeftEye = 1
                    # elif (isInRightAOI >= -AOIdist and isInLeftAOI < -AOIdist):
                    #     print("participant looked at right eye!")
                    #     isLeftEye = 0
                    # else:
                    #     print("participant looked at neither eye")
                    # print("total prop: ", total_prop_dict, "angle:", angles_prop[count], "translation: ", translations_prop[count])
                    
                    # total_prop_dict[315][2] += 1
                    # validity
                    if (float(l[10]) == 1):
                        time_spend_per_trial_list.append(isLeftEye)
                    if (float(l[10]) == 0 and trial_line_count<=1): 
                        trial_line_count -= 1
                    # save proportions
                    if (trial_line_count == 1):
                        print("appending data for csv", trial_line_count)
                        print("currrent participant 2: ", participant_num)

                        first_fixation_data.append([str(participant_num), str(count+2), str(isLeftEye), angles_prop[count], translations_prop[count]])
                        total_prop_dict[angles_prop[count]][translations_prop[count]] += 1
                        if (distance_to_left <= AOIdist and distance_to_right > AOIdist):
                            prop_dict[angles_prop[count]][translations_prop[count]] += 1

                else:
                    if (time > trial_times[count][0]):
                        count += 1
                        trial_line_count = 0
                        num_left_per_trial = time_spend_per_trial_list.count(1)
                        total_time_of_trial = len(time_spend_per_trial_list)
                        time = 0
                        if (total_time_of_trial > 0):
                            time = num_left_per_trial/total_time_of_trial
                        time_spent_on_left_in_trial_data.append([str(participant_num), str(count+1), str(time), angles_prop[count-1], translations_prop[count-1]])
                        time_spend_per_trial_list.clear()
                if (count >= len(trial_times)):
                    break
# read_gazepoint()

participants = [1, 3, 6, 10, 15, 19, 23, 24, 31, 35, 38, 44, 57, 59, 60, 61, 63, 66, 70, 77, 96, 97, 99]
def read_participant_files():
    print("lisitng directories!!")
    gazepoint_files = os.listdir("gazepoint_data")
    matlab_files = os.listdir("matlab_data")

    for participant in participants:
        prop_dict.clear()
        total_prop_dict.clear()
        current_participant = participant
        print("currrent participant: ", current_participant)
        participant_index = participants.index(current_participant)
        read_matlab(os.path.join("matlab_data", matlab_files[participant_index]), current_participant)
        read_gazepoint(os.path.join("gazepoint_data", gazepoint_files[participant_index]), current_participant)
        
        for angle, inner_dict in total_prop_dict.items():
            print(f"Outer Key: {angle}")
            for translation, count in inner_dict.items():
                print(f"  Inner Key: {translation}, Value: {count}")
                print("left eye: ", prop_dict[angle][translation])
                proportion_data.append([str(current_participant), angle, translation, prop_dict[angle][translation]/count])
        # if current_participant == 19:
        #     break

read_participant_files()
# ----------
#  Create the output files
# ---------
# trial per line, which eye did they look at first?
first_fixation_file_path = "./data/first_fixation.csv"
with open(first_fixation_file_path, "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(first_fixation_header)
    writer.writerows(first_fixation_data)
# for all trials, based on height and angle, how often they looked at left eye first?
prop_fixation_file_path = "./data/prop_first_fixation.csv"
with open(prop_fixation_file_path, "w", newline="") as file:
    writer = csv.writer(file)
    # Write first header and data
    writer.writerow(proportion_header)
    writer.writerows(proportion_data)
# trial per line, proportion of left to right eye
prop_fixation_file_path = "./data/time_spent_per_trial.csv"
with open(prop_fixation_file_path, "w", newline="") as file:
    writer = csv.writer(file)
    # Write first header and data
    writer.writerow(time_spent_on_left_in_trial_header)
    writer.writerows(time_spent_on_left_in_trial_data)

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
    monitor_width = 1680
    monitor_height = 1050
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
