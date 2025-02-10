import cv2 as cv
import numpy as np
import os # used to loop through files
import csv # used to write data to csv
import sys
from collections import defaultdict

# will resize the image to the monitor size to ensure the coordinates will match the x,y coords from the eye tracker
monitor_width = 1680
monitor_height = 1050
# used for debugging
output_file = open('./output.txt', 'w')
sys.stdout = output_file

# ----------
#  Code used to find the screen position of participants:
# ----------
# use the correctCorners.csv and save it as an array called corners_data
corners_data = []
default_screen_pos = [438, 32] # participant 1 coords
current_participant = 1
screen_translation = [0,0]
def save_screen_pos():
    with open('./csv/correctCorners.csv') as f:
        reader = csv.reader(f, delimiter=',') 
        for row in reader:
            corners_data.append(row)

# checks the difference between the current participant and participant 1
def update_screen_pos(participantID):
    for row in corners_data:
        if "subject"+str(participantID)+".png" in row[0]:
            screen_translation[0] = default_screen_pos[0] - float(row[1])
            screen_translation[1] = default_screen_pos[1] - float(row[2])
            break
    
# return the coords of each eye
def find_eye_coords(angle, translation):
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
        x_trans = - screen_translation[0]
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
            y_trans_315 = 20 - screen_translation[1]
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
human_coder = []
human_computer_agreement = []
prop_dict = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
total_prop_dict = defaultdict(lambda: defaultdict(int))
time_spend_per_trial_list = []

# the video for the first participant starts before the first trial, so I checked when the instructions disappear and the clock starts
# buffer_instruction_disappear_times = [6.5]#[6.5, 13.4, 5.5]  
trial_2_start = [19.8, 31.9, 13.00, 9.9, 20.30, 14.0, 25.8, 8.0, 21.9, 10.0, 14.0, 26.60, 19.6, 38.80, 10.2, 75.8, 43.70, 20.80, 80.7, 11.9, 2.0, 18.4, 46.5, 14.2]
# rt_buffer = 0.03

# vars used to write to the output files
    # first fixation by trial 
first_fixation_header = ["participant", "trial", "angle", "translation", "first eye fixation", "human_coder", "human_computer_agreement"]
first_fixation_data = []
    # proportion based on angle + height
proportion_header = ["participant", "angle", "height", "proportion left", "proportion right"]
proportion_data = [""]
    # left vs right proportion in each trial
time_spent_on_left_in_trial_header = ["participant", "trial", "proportion to left eye", "proportion to right eye", "angle", "translation"]
time_spent_on_left_in_trial_data = []
    # agreements 
first_fixation_agreement_header = ["participant", "human_computer_agreement"]
first_fixation_agreement_data = []



def read_matlab(f, participant_num, first_valid_trial):
    trial_times.clear()
    eye_coords_left.clear()
    eye_coords_right.clear()
    angles_prop.clear()
    translations_prop.clear()
    human_coder.clear()
    human_computer_agreement.clear()
    save_screen_pos()
    update_screen_pos(participant_num)

    # looks at all the files in the folder
    # for filename in os.listdir("matlab_data"):
    #     print("file name:" + filename)
    #     f = os.path.join("matlab_data", filename)
    with open(f, 'r') as file:
        participant_index = participants.index(participant_num)
        #buffer_instruction_disappear_time = buffer_instruction_disappear_times[participant_index]
        lines = file.readlines() 
        lines_array = []
        print("participant: ", participant_index, "valid trial: ", first_valid_trial)
        for line in lines:
            l = line.split(",")
            # gets when the first trial ended
            if l[1].isdigit() and float(l[1]) == first_valid_trial:
                prev_exp_time = float(l[9])
                buffer_instruction_disappear_time = trial_2_start[participant_index] - prev_exp_time
                print("buffer: ", buffer_instruction_disappear_time, " trial 2 start: ", trial_2_start[participant_index], " prev exp: ", prev_exp_time)
            if l[1].isdigit() and float(l[1]) > first_valid_trial: # ignore first trial
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
                face_appears = prev_exp_time + time_before_face_appears
                face_disappears = face_appears + duration_of_face
                trial_times.append([face_appears+buffer_instruction_disappear_time, face_disappears+buffer_instruction_disappear_time])
                # coords
                angle = int(l[5])
                translation = int(l[6])
                human = -2 # no coding
                if len(l) > 11:
                    if l[11].isdigit():
                        human = int(l[11])
                    elif l[11] == "-1":
                        human = -1
                human_coder.append(human)
                angles_prop.append(angle)
                translations_prop.append(translation)
                find_eye_coords(angle, translation)

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


def read_gazepoint(f, participant_num, first_valid_trial):
    # for filename in os.listdir("gazepoint_data"):
    #     # print("file name:" + filename)
    #     f = os.path.join("gazepoint_data", filename)
    with open(f, 'r') as file:
        lines = file.readlines() 
        count = 0
        trial_line_count = 0
        total_agreement = 0
        print("gazzepint: participant", participant_num, "first valid trial: ", first_valid_trial)
        for line in lines:
            l = line.split(",")
            if (l[0] != "MEDIA_ID"):
                time = float(l[3])
                print("time: ", time, "trial_times[count][0]", trial_times[count][0], "trial_times[count][1]", trial_times[count][1])
                # if (trial_times[count][0]+0.05 <= time) and (time <= trial_times[count][1]+0.2):

                if (time > trial_times[count][0]+0.01 and time < trial_times[count][1]):
                    trial_line_count += 1
                    print("in gazepoint, current line is", l)
                    print("TRIAL " , count+first_valid_trial, "participant ", participant_num)

                    print("found a match! current time of fixation" , time, " is in time interval from matlab: ", trial_times[count][0], " and ", trial_times[count][1])
                    # get where the participant looked
                    participant_x = float(l[5])*monitor_width
                    participant_y = float(l[6])*monitor_height#+100
                    # print("looking at x: ", participant_x, " y: ", participant_y)
                    # compare to AOI of the trial
                    # print("left eye coords: ", eye_coords_left[count])
                    # print("right eye coords: ", eye_coords_right[count])
                    left_eye_coords = np.array(eye_coords_left[count]).reshape(-1, 2)
                    right_eye_coords = np.array(eye_coords_right[count]).reshape(-1, 2)
                    # find centers of the eyes
                    left_eye_center = np.mean(left_eye_coords, axis=0)
                    right_eye_center = np.mean(right_eye_coords, axis=0)
                    print("Left eye center:", left_eye_center) 
                    print("Right eye center:", right_eye_center)
                    # calculate Euclidean distances
                    distance_to_left = np.sqrt((participant_x - left_eye_center[0])**2 + (participant_y - left_eye_center[1])**2)
                    distance_to_right = np.sqrt((participant_x - right_eye_center[0])**2 + (participant_y - right_eye_center[1])**2)
                    print("dist to left: ", distance_to_left, " dist to right: ", distance_to_right)
                    
                    isLeftEye = -1 # -1 = neither, 1 = left, 0 = right, 2 = both
                    AOIdist = 44
                    # if (distance_to_right <= AOIdist and distance_to_left <= AOIdist):
                    #     print("participant looked at both eye!")
                    #     isLeftEye = 2
                    if (distance_to_left <= AOIdist and distance_to_right > AOIdist):
                        print("participant looked at left eye!")
                        isLeftEye = 1
                    elif (distance_to_right <= AOIdist and distance_to_left > AOIdist):
                        print("participant looked at right eye!")
                        isLeftEye = 0
                    else:
                        print("participant looked at neither eye")
                    # validity
                    if (float(l[10]) == 1):
                        time_spend_per_trial_list.append(isLeftEye)
                    if (float(l[10]) == 0 and trial_line_count<=1): 
                        trial_line_count -= 1
                    # save proportions
                    if (trial_line_count == 1):
                        # print("appending data for csv", trial_line_count)
                        # print("currrent participant 2: ", participant_num)
                        # checking for agreement;
                        agreement = False
                        if isLeftEye == 1 and human_coder[count] == 1:
                            agreement = True
                        elif isLeftEye == 0 and human_coder[count] == 2:
                            agreement = True
                        elif isLeftEye == -1 and (human_coder[count] != -2 and human_coder[count] != 1 and human_coder[count] != 2):
                            agreement = True
                        if agreement:
                            total_agreement += 1
                        first_fixation_data.append([str(participant_num), str(count+first_valid_trial), angles_prop[count], translations_prop[count], str(isLeftEye), human_coder[count], agreement])
                        total_prop_dict[angles_prop[count]][translations_prop[count]] += 1
                        if (distance_to_left <= AOIdist and distance_to_right > AOIdist):
                            prop_dict[angles_prop[count]][translations_prop[count]]["left"] += 1
                        if (distance_to_right <= AOIdist and distance_to_left > AOIdist):
                            prop_dict[angles_prop[count]][translations_prop[count]]["right"] += 1

                else:
                    if (time > trial_times[count][1]):
                        count += 1
                        trial_line_count = 0
                        num_left_per_trial = time_spend_per_trial_list.count(1)
                        num_right_per_trial = time_spend_per_trial_list.count(0)
                        total_time_of_trial = len(time_spend_per_trial_list)
                        time = 0
                        if (total_time_of_trial > 0):
                            time = num_left_per_trial/total_time_of_trial
                            time_right = num_right_per_trial/total_time_of_trial
                        time_spent_on_left_in_trial_data.append([str(participant_num), str(count+1), str(time), str(time_right), angles_prop[count-1], translations_prop[count-1]])
                        time_spend_per_trial_list.clear()
                if (count >= len(trial_times)):
                    break
        print(f"total agreement for participant {participant_num} is: {total_agreement/len(angles_prop)*100}")
        first_fixation_agreement_data.append((participant_num, total_agreement/len(angles_prop)*100))
# read_gazepoint()

participants = [1, 3, 6, 10, 15, 19, 23, 24, 31, 35, 38, 44, 57, 59, 60, 61, 63, 66, 70, 77, 87, 96, 97, 99]
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
        first_valid_trial = 1
        if current_participant == 87:
            first_valid_trial = 8
        read_matlab(os.path.join("matlab_data", matlab_files[participant_index]), current_participant, first_valid_trial)
        read_gazepoint(os.path.join("gazepoint_data", gazepoint_files[participant_index]), current_participant, first_valid_trial)
        
        for angle, inner_dict in total_prop_dict.items():
            print(f"Outer Key: {angle}")
            for translation, count in inner_dict.items():
                print(f"  Inner Key: {translation}, Value: {count}")
                print("left eye: ", prop_dict[angle][translation]["left"])
                print("right eye: ", prop_dict[angle][translation]["right"])
                proportion_data.append([str(current_participant), angle, translation, prop_dict[angle][translation]["left"]/count, prop_dict[angle][translation]["right"]/count])

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
prop_fixation_file_path = "./data/human_computer_agreement.csv"
with open(prop_fixation_file_path, "w", newline="") as file:
    writer = csv.writer(file)
    # Write first header and data
    writer.writerow(first_fixation_agreement_header)
    writer.writerows(first_fixation_agreement_data)
