# Attendance calculator for zoom

This script parses student attendance status with convenient override tools.

## Requirements

No requirements.

## Get started

1. Prepare a folder for the attendance csvs
2. Rename `config_sample.ini` as `config.ini`
3. Make sure you place the folder name for the right variable
4. Fill in the min, max attendance time to count as attendance
5. Fill in the override filename. There must be a override file but it can only contain headers.
6. If you want to rename your attendance files based on event and date, set `RENAME_FILE` in `config.ini` to `True`

## Override file

The current script supports four situations:

1. override min attendnace time for a specific date: `<time>, <date>`
2. override a student to mark as attended for a specific date: `<netid>, <date>`
3. override a student to mark as not attended for a specific date: `<netid>, <date>_not_present`
4. override all students attendance for a specific date: `all, <date>`

You can add # to neglect a specific row.

## LICENCE

This code is developed under MIT licence. Feel free to contribute or contact the author.
