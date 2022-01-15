import configparser
import csv
from curses import meta
import json
import re
from datetime import date, datetime
from os import listdir, rename
from os.path import isfile, join

from helper import is_int

# cleanup raw attendance files
def clean_up_filenames(ROOT_FOLDER, rename_files=False):
    if rename_files:
        for f in listdir(ROOT_FOLDER):
            if isfile(join(ROOT_FOLDER, f)):
                if not bool(re.match("\d{8}.*", f)):
                    meeting_info = [r for r in csv.reader(open(join(ROOT_FOLDER, f)))][1]
                    meeting_name = meeting_info[1].replace(" ", "_")
                    meeting_date = meeting_info[2].split(" ")[0].split("/")
                    meeting_date = ''.join([meeting_date[2], meeting_date[0], meeting_date[1]])
                    filename = meeting_date + '-' + meeting_name + '.csv'
                    print(join(ROOT_FOLDER, filename))
                    rename(join(ROOT_FOLDER, f), join(ROOT_FOLDER, filename))
    return [f for f in listdir(ROOT_FOLDER) if isfile(join(ROOT_FOLDER, f))]

# variables
config = configparser.ConfigParser()
config.read('config.ini')
setup = config['DEFAULT']
ROOT_FOLDER = setup['ROOT_FOLDER']
DEFAULT_MIN_DURATION = int(setup['DEFAULT_MIN_DURATION'])
DEFAULT_MAX_DURATION = int(setup['DEFAULT_MAX_DURATION'])
YEAR = str(setup['YEAR'])
OVERRIDE = setup['OVER_RIDE_FILE']
RENAME_FILE = eval(setup['RENAME_FILE'].capitalize())
attendance_files = clean_up_filenames(ROOT_FOLDER, rename_files=RENAME_FILE)
attendance_files.sort()
all_students = {}
duration_tacker = {}
all_dates = set()
except_dates = []
excepted_MIN_DURATION = {}
individual_override = []
remove_student = []

# exceptions and overrides preprocessing
overrides = [r for r in csv.reader(open(OVERRIDE))]
for status, date in overrides:
    if status == 'status':
        pass
    elif status[0] == '#':
        pass
    elif status == 'all':
        except_dates.append(date.strip())
    elif not is_int(date):
        remove_student.append([status, str(date.split('_')[0]).strip()])
    elif is_int(status):
        excepted_MIN_DURATION[str(date)] = status
    else:
        individual_override.append([status, date])

# process all files
for files in attendance_files:
    try:
        current_file = '/'.join([ROOT_FOLDER, files])
        # print(current_file)
        rows = [r for r in csv.reader(open(current_file))]

        if "Duration (Minutes)" in rows[3]:
            duration_idx = rows[3].index("Duration (Minutes)")
        elif "Total Duration (Minutes)" in rows[3]:
            duration_idx = rows[3].index("Total Duration (Minutes)")
        else:
            raise RuntimeError ("Cannot find duration information")
        
        user_email_idx = rows[3].index("User Email")
        meta_data = rows[1]
        student_data = rows[4:]

        # from sys import exit; exit()
        # extract metadata
        date = str(meta_data[2].split(" ")[0].replace(
            "'", '').replace('/', '').replace(YEAR, ''))
        if str(date) in except_dates:  # early stop if that class is exempted from attendance
            continue
        all_dates.add(date)

        for student in student_data:
            # print(student)
            netid = student[user_email_idx].split('@')[0]
            duration = student[duration_idx]

            # duration processing
            if duration == 'Yes' or duration == 'No':
                continue
            try:
                duration = int(duration)
            except:
                print("Error on line 91: duration value " + str(duration))
                continue

            # check if student is new
            if netid not in all_students:
                all_students[netid] = {}

            if date not in all_students[netid]:
                all_students[netid][date] = duration
            else:
                all_students[netid][date] += duration

            # add the time record to the record book
            if duration < DEFAULT_MAX_DURATION:
                if date not in duration_tacker:
                    duration_tacker[date] = [duration]
                else:
                    duration_tacker[date].append(duration)
                    duration_tacker[date] = sorted(duration_tacker[date])

    except BaseException as e:
        print("error occured in the following file:", files)
        print("Error Msg: ", e)

# from sys import exit; exit()

# apply overrides
for entry in individual_override:
    # print(entry)
    netid = entry[0].strip()
    date = entry[1].strip()

    if netid not in all_students:
        all_students[netid] = {}

    if date == '0000':
        for key in all_students[netid]:
            all_students[netid][key] = 75
    else: 
        if date not in all_students[netid]:
            all_students[netid][date] = 75
        else:
            all_students[netid][date] += 75

# apply negative overrides
for entry in remove_student:
    # print(entry)
    netid = entry[0].strip()
    date = entry[1].strip()

    if netid not in all_students:
        all_students[netid] = {}

    all_students[netid][date] = -1


# dump intermediate file
with open("all_students.json", "w") as outfile:
    json.dump(all_students, outfile, indent='\t', sort_keys=True)

# prepare doc
csv_file = open("attendance.csv", "w")
writer = csv.writer(csv_file)
writer.writerow(["netid", "attendance", "notes"])

for student in all_students:
    student_record = all_students[student]
    dates = sorted(list(student_record))
    counter = 0
    notes = "This note is updated on: " + str(datetime.now().date()) + '\n'

    for date in dates:
        # check if the date contains exceptions
        if date in excepted_MIN_DURATION:
            threshold = excepted_MIN_DURATION[date]
        else:
            threshold = DEFAULT_MIN_DURATION

        # count attendance
        if student_record[date] >= threshold:
            counter += 1

        if student_record[date] == -1:
            notes += str(date) + \
                ": attendance removed due to not present upon row call.\n"
        else:
            notes += str(date) + ": " + \
                str(student_record[date]) + str(" mins\n")

    notes += "free attendance given: " + ', '.join(except_dates) + '\n'

    writer.writerow([student, counter, notes])

csv_file.close()

print("Completed.")
print("Number of sessions: " + str(len(all_dates)) + '.')
