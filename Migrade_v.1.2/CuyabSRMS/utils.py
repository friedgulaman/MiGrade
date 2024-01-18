from .models import ActivityLog

def transmuted_grade(initial_grade):
                    if initial_grade is None:
                        return None
                    
                    if 98.40 <= initial_grade <= 99.99:
                        return 99
                    elif 96.80 <= initial_grade <= 98.39:
                        return 98
                    elif 95.20 <= initial_grade <= 96.79:
                        return 97
                    elif 93.60 <= initial_grade <= 95.19:
                        return 96
                    elif 92.00 <= initial_grade <= 93.59:
                        return 95
                    elif 90.40 <= initial_grade <= 91.99:
                        return 94
                    elif 88.80 <= initial_grade <= 90.39:
                        return 93
                    elif 87.20 <= initial_grade <= 88.79:
                        return 92
                    elif 85.60 <= initial_grade <= 87.19:
                        return 91
                    elif 84.00 <= initial_grade <= 85.59:
                        return 90
                    elif 82.40 <= initial_grade <= 83.99:
                        return 89
                    elif 80.80 <= initial_grade <= 82.39:
                        return 88
                    elif 79.20 <= initial_grade <= 80.79:
                        return 87
                    elif 77.60 <= initial_grade <= 79.19:
                        return 86
                    elif 76.00 <= initial_grade <= 77.59:
                        return 85
                    elif 74.40 <= initial_grade <= 75.99:
                        return 84
                    elif 72.80 <= initial_grade <= 74.39:
                        return 83
                    elif 71.20 <= initial_grade <= 72.79:
                        return 82
                    elif 69.60 <= initial_grade <= 71.19:
                        return 81
                    elif 68.00 <= initial_grade <= 69.59:
                        return 80
                    elif 66.40 <= initial_grade <= 67.99:
                        return 79
                    elif 64.80 <= initial_grade <= 66.39:
                        return 78
                    elif 63.20 <= initial_grade <= 64.79:
                        return 77
                    elif 61.60 <= initial_grade <= 63.19:
                        return 76
                    elif 60.00 <= initial_grade <= 61.59:
                        return 75
                    elif 56.00 <= initial_grade <= 59.99:
                        return 74
                    elif 52.00 <= initial_grade <= 55.99:
                        return 73
                    elif 48.00 <= initial_grade <= 51.99:
                        return 72
                    elif 44.00 <= initial_grade <= 47.99:
                        return 71
                    elif 40.00 <= initial_grade <= 43.99:
                        return 70
                    elif 36.00 <= initial_grade <= 39.99:
                        return 69
                    elif 32.00 <= initial_grade <= 35.99:
                        return 68
                    elif 28.00 <= initial_grade <= 31.99:
                        return 67
                    elif 24.00 <= initial_grade <= 27.99:
                        return 66
                    elif 20.00 <= initial_grade <= 23.99:
                        return 65
                    elif 16.00 <= initial_grade <= 19.99:
                        return 64
                    elif 12.00 <= initial_grade <= 15.99:
                        return 63
                    elif 8.00 <= initial_grade <= 11.99:
                        return 62
                    elif 4.00 <= initial_grade <= 7.99:
                        return 61
                    elif 0 <= initial_grade <= 3.99:
                        return 0
                    else:
                        return initial_grade
                    
def log_activity(user, action, details=''):
    ActivityLog.objects.create(user=user, action=action, details=details)


from django.http import HttpResponse
import openpyxl
import pandas as pd
import shutil
from datetime import datetime

from .models import GradeScores

# STUDENT NAME
def write_student_names(sheet, grade_scores_queryset):
    column_coordinates_student_name = 2
    row_coordinates_student_name = 12

    while sheet.cell(row=row_coordinates_student_name, column=column_coordinates_student_name).value:
        row_coordinates_student_name += 1

    for score_student_name in grade_scores_queryset:
        value_to_write = score_student_name.student_name
        sheet.cell(row=row_coordinates_student_name, column=column_coordinates_student_name, value=value_to_write)
        row_coordinates_student_name += 1

# HIGHEST POSSIBLE SCORE IN WRITTEN WORKS
def write_scores_hps_written(sheet, grade_scores_queryset):

    # SCORES IN HIGHEST POSSIBLE SCORE IN WRITTEN WORKS
    column_coordinates_score_hps_written = 6
    row_coordinates_scores_hps_written = 10

    while sheet.cell(row=row_coordinates_scores_hps_written, column=column_coordinates_score_hps_written).value:
        column_coordinates_score_hps_written += 1

    for score_hps_written in grade_scores_queryset:
        values_to_write = score_hps_written.scores_hps_written
        for value in values_to_write:
            sheet.cell(row=row_coordinates_scores_hps_written, column=column_coordinates_score_hps_written, value=value)
            column_coordinates_score_hps_written += 1

        column_coordinates_score_hps_written = 6

    # TOTAL HIGHEST POSSIBLE SCORE IN WRITTEN WORKS
        
    column_coordinates_total_scores_hps_written = 16
    row_coordinate_total_scores_hps_written = 10

    for scores_total_ww_hps in grade_scores_queryset:
        values_to_write = scores_total_ww_hps.total_ww_hps


        value_to_write = str(values_to_write)

        sheet.cell(row=row_coordinate_total_scores_hps_written, column=column_coordinates_total_scores_hps_written, value=value_to_write)
        column_coordinates_total_scores_hps_written += 1

        column_coordinates_total_scores_hps_written = 16

    # PERCENTAGE SCORE IN HIGHEST POSSIBLE SCORE IN WRITTEN WORKS
    column_coordinate_total_ww_ps = 17
    row_coordinate_total_ww_ps = 10

    for scores_total_ww_ps in grade_scores_queryset:
        value_to_write = 100

        value_to_write = str(value_to_write)
        sheet.cell(row=row_coordinate_total_ww_ps, column=column_coordinate_total_ww_ps, value=value_to_write)
        column_coordinate_total_ww_ps += 1

        column_coordinate_total_ww_ps = 17

    # WEIGHT INPUT IN HIGHEST POSSIBLE SCORE IN WRITTEN WORKS
    column_coordinate_weight_input_written = 18
    row_coordinate_weight_input_written = 10

    for scores_weight_input_written in grade_scores_queryset:
        value_to_write = scores_weight_input_written.weight_input_written
        value_to_write = str(value_to_write)
        sheet.cell(row=row_coordinate_weight_input_written, column=column_coordinate_weight_input_written, value=value_to_write)
        column_coordinate_weight_input_written += 1

        column_coordinate_weight_input_written = 18

def write_scores_hps_performance(sheet, grade_scores_queryset):
    column_coordinate = 19
    row_coordinate = 10

    while sheet.cell(row=row_coordinate, column=column_coordinate). value:
        column_coordinate += 1

    for score in grade_scores_queryset:
        values_to_write = score.scores_hps_performance
        for value in values_to_write:
            sheet.cell(row=row_coordinate, column=column_coordinate, value=value)
            column_coordinate += 1

        column_coordinate = 19

    # TOTAL HIGHEST POSSIBLE SCORE IN PERFORMANCE TASKS
        
    column_coordinates_total_scores_hps_performance = 29
    row_coordinate_total_scores_hps_performance = 10

    for scores_total_pt_hps in grade_scores_queryset:
        values_to_write = scores_total_pt_hps.total_pt_hps


        value_to_write = str(values_to_write)

        sheet.cell(row=row_coordinate_total_scores_hps_performance, column=column_coordinates_total_scores_hps_performance, value=value_to_write)
        column_coordinates_total_scores_hps_performance += 1

        column_coordinates_total_scores_hps_performance = 29

    # PERCENTAGE SCORE IN HIGHEST POSSIBLE SCORE IN WRITTEN WORKS
    column_coordinate_total_pt_ps = 30
    row_coordinate_total_pt_ps = 10

    for scores_total_pt_ps in grade_scores_queryset:
        value_to_write = 100

        value_to_write = str(value_to_write)
        sheet.cell(row=row_coordinate_total_pt_ps, column=column_coordinate_total_pt_ps, value=value_to_write)
        column_coordinate_total_pt_ps += 1

        column_coordinate_total_pt_ps = 30

    # WEIGHT INPUT IN HIGHEST POSSIBLE SCORE
    column_coordinate_weight_input_performance = 31
    row_coordinate_weight_input_performance = 10

    for scores_weight_input_performance in grade_scores_queryset:
        value_to_write = scores_weight_input_performance.weight_input_performance
        value_to_write = str(value_to_write)
        sheet.cell(row=row_coordinate_weight_input_performance, column=column_coordinate_weight_input_performance, value=value_to_write)
        column_coordinate_weight_input_performance += 1

        column_coordinate_weight_input_performance = 31

def write_scores_hps_quarterly(sheet, grade_scores_queryset):

    # TOTAL HIGHEST POSSIBLE SCORE IN QUARTERLY ASSESSMENT
        
    column_coordinates_total_scores_hps_performance = 32
    row_coordinate_total_scores_hps_performance = 10

    for scores_total_pt_hps in grade_scores_queryset:
        values_to_write = scores_total_pt_hps.total_qa_hps


        value_to_write = str(values_to_write)

        sheet.cell(row=row_coordinate_total_scores_hps_performance, column=column_coordinates_total_scores_hps_performance, value=value_to_write)
        column_coordinates_total_scores_hps_performance += 1

        column_coordinates_total_scores_hps_performance = 32

    # PERCENTAGE SCORE IN HIGHEST POSSIBLE SCORE IN QUARTERLY ASSESSMENT
    column_coordinate_total_pt_ps = 33
    row_coordinate_total_pt_ps = 10

    for scores_total_pt_ps in grade_scores_queryset:
        value_to_write = 100

        value_to_write = str(value_to_write)
        sheet.cell(row=row_coordinate_total_pt_ps, column=column_coordinate_total_pt_ps, value=value_to_write)
        column_coordinate_total_pt_ps += 1

        column_coordinate_total_pt_ps = 33

    # WEIGHT INPUT IN HIGHEST POSSIBLE SCORE QUARTERLY ASSESSMENT
    column_coordinate_weight_input_performance = 34
    row_coordinate_weight_input_performance = 10

    for scores_weight_input_performance in grade_scores_queryset:
        value_to_write = scores_weight_input_performance.weight_input_quarterly
        value_to_write = str(value_to_write)
        sheet.cell(row=row_coordinate_weight_input_performance, column=column_coordinate_weight_input_performance, value=value_to_write)
        column_coordinate_weight_input_performance += 1

        column_coordinate_weight_input_performance = 34

# def write_quarterly_assessment_score(sheet, grade_scores_queryset):
#     column_coordinates = 32
#     row_coordinates = 10

def write_written_works_scores(sheet, grade_scores_queryset):
    
    #WRITTEN WORKS SCORES
    column_coordinates = 6
    row_coordinates = 12
    max_column_index = 15

    for score in grade_scores_queryset:
        written_works_scores_list = score.written_works_scores

        for value in written_works_scores_list:
            value_to_write = str(value)
            sheet.cell(row=row_coordinates, column=column_coordinates, value=value_to_write)
            column_coordinates += 1

            # If we reach the last column, move to the next row
            if column_coordinates > max_column_index:  # Update max_column_index with the actual maximum column index
                column_coordinates = 6  # Reset column index to the starting column
                row_coordinates += 1  # Move to the next row

    # TOTAL WRITTEN WORKS SCORE
    column_coordinates_total_written_works_score = 16
    row_coordinates_total_written_works_score = 12

    for scores in grade_scores_queryset:
        total_written_works_score = scores.total_score_written

        # Convert the float value to a string
        value_to_write = str(total_written_works_score)

        sheet.cell(row=row_coordinates_total_written_works_score, column=column_coordinates_total_written_works_score, value=value_to_write)
        column_coordinates_total_written_works_score += 1

        if column_coordinates_total_written_works_score > max_column_index:  # Update max_column_index with the actual maximum column index
            column_coordinates_total_written_works_score = 16  # Reset column index to the starting column
            row_coordinates_total_written_works_score += 1

    # TOTAL PERCENTAGE SCORE WRITTEN WORKS
    column_coordinates_percentage_score_written = 17
    row_coordinates_percentage_score_written = 12

    for scores in grade_scores_queryset:
        percentage_score_written = scores.percentage_score_written
        rounded_percentage_score = round(percentage_score_written, 2)  # You can adjust the number of decimal places as needed
        value_to_write = str(rounded_percentage_score)
        sheet.cell(row=row_coordinates_percentage_score_written, column=column_coordinates_percentage_score_written, value=value_to_write)
        column_coordinates_percentage_score_written += 1

        if column_coordinates_percentage_score_written > max_column_index:
            column_coordinates_percentage_score_written = 17
            row_coordinates_percentage_score_written += 1

    # TOTAL WEIGHTED SCORE WRITTEN WORKS
    column_coordinates_weighted_score_written = 18
    row_coordinates_weighted_score_written = 12

    for scores in grade_scores_queryset:
        weighted_score_written = scores.weighted_score_written
        rounded_weighted_score_written = round(weighted_score_written, 2)
        value_to_write = str(rounded_weighted_score_written)
        sheet.cell(row=row_coordinates_weighted_score_written, column=column_coordinates_weighted_score_written, value=value_to_write)
        column_coordinates_weighted_score_written += 1

        if column_coordinates_weighted_score_written > max_column_index:
            column_coordinates_weighted_score_written = 18
            row_coordinates_weighted_score_written += 1


def write_performance_tasks_scores(sheet, grade_scores_queryset):

    # PERFORMANCE TASKS SCORES
    column_coordinates = 19
    row_coordinates = 12
    max_column_index = 28

    for score in grade_scores_queryset:
        performance_tasks_scores_list = score.performance_task_scores

        for value in performance_tasks_scores_list:
            value_to_write = str(value)
            sheet.cell(row=row_coordinates, column=column_coordinates, value=value_to_write)
            column_coordinates += 1

            # If we reach the last column, move to the next row
            if column_coordinates > max_column_index:  # Update max_column_index with the actual maximum column index
                column_coordinates = 19  # Reset column index to the starting column
                row_coordinates += 1  # Move to the next row

    # TOTAL PERFORMANCE TASKS SCORE
    column_coordinates_total_performance_tasks_score = 29
    row_coordinates_total_performance_tasks_score = 12

    for scores in grade_scores_queryset:
        total_performance_tasks_score = scores.total_score_performance

        # Convert the float value to a string
        value_to_write = str(total_performance_tasks_score)

        sheet.cell(row=row_coordinates_total_performance_tasks_score, column=column_coordinates_total_performance_tasks_score, value=value_to_write)
        column_coordinates_total_performance_tasks_score += 1

        if column_coordinates_total_performance_tasks_score > max_column_index:  # Update max_column_index with the actual maximum column index
            column_coordinates_total_performance_tasks_score = 29  # Reset column index to the starting column
            row_coordinates_total_performance_tasks_score += 1  

        # TOTAL PERCENTAGE SCORE WRITTEN WORKS
    column_coordinates_percentage_score_performance = 30
    row_coordinates_percentage_score_performance = 12

    for scores in grade_scores_queryset:
        percentage_score_performance = scores.percentage_score_performance
        rounded_percentage_score = round(percentage_score_performance, 2)  # You can adjust the number of decimal places as needed
        value_to_write = str(rounded_percentage_score)
        sheet.cell(row=row_coordinates_percentage_score_performance, column=column_coordinates_percentage_score_performance, value=value_to_write)
        column_coordinates_percentage_score_performance += 1

        if column_coordinates_percentage_score_performance > max_column_index:
            column_coordinates_percentage_score_performance = 30
            row_coordinates_percentage_score_performance += 1

    # TOTAL WEIGHTED SCORE WRITTEN WORKS
    column_coordinates_weighted_score_performance = 31
    row_coordinates_weighted_score_performance = 12

    for scores in grade_scores_queryset:
        weighted_score_performance = scores.weighted_score_performance
        rounded_weighted_score_performance = round(weighted_score_performance, 2)
        value_to_write = str(rounded_weighted_score_performance)
        sheet.cell(row=row_coordinates_weighted_score_performance, column=column_coordinates_weighted_score_performance, value=value_to_write)
        column_coordinates_weighted_score_performance += 1

        if column_coordinates_weighted_score_performance > max_column_index:
            column_coordinates_weighted_score_performance = 31
            row_coordinates_weighted_score_performance += 1

def write_quarterly_assessment_scores(sheet, grade_scores_queryset):
    #    # PERFORMANCE TASKS SCORES
    # column_coordinates = 19
    # row_coordinates = 12
    max_column_index = 31

    # for score in grade_scores_queryset:
    #     performance_tasks_scores_list = score.performance_task_scores

    #     for value in performance_tasks_scores_list:
    #         value_to_write = str(value)
    #         sheet.cell(row=row_coordinates, column=column_coordinates, value=value_to_write)
    #         column_coordinates += 1

    #         # If we reach the last column, move to the next row
    #         if column_coordinates > max_column_index:  # Update max_column_index with the actual maximum column index
    #             column_coordinates = 19  # Reset column index to the starting column
    #             row_coordinates += 1  # Move to the next row

    # TOTAL QUARTERLY ASSESSMENT SCORE
    column_coordinates_total_performance_tasks_score = 32
    row_coordinates_total_performance_tasks_score = 12

    for scores in grade_scores_queryset:
        total_performance_tasks_score = scores.total_score_quarterly

        # Convert the float value to a string
        value_to_write = str(total_performance_tasks_score)

        sheet.cell(row=row_coordinates_total_performance_tasks_score, column=column_coordinates_total_performance_tasks_score, value=value_to_write)
        column_coordinates_total_performance_tasks_score += 1

        if column_coordinates_total_performance_tasks_score > max_column_index:  # Update max_column_index with the actual maximum column index
            column_coordinates_total_performance_tasks_score = 32  # Reset column index to the starting column
            row_coordinates_total_performance_tasks_score += 1  

        # TOTAL PERCENTAGE SCORE WRITTEN WORKS
    column_coordinates_percentage_score_performance = 33
    row_coordinates_percentage_score_performance = 12

    for scores in grade_scores_queryset:
        percentage_score_performance = scores.percentage_score_quarterly
        rounded_percentage_score = round(percentage_score_performance, 2)  # You can adjust the number of decimal places as needed
        value_to_write = str(rounded_percentage_score)
        sheet.cell(row=row_coordinates_percentage_score_performance, column=column_coordinates_percentage_score_performance, value=value_to_write)
        column_coordinates_percentage_score_performance += 1

        if column_coordinates_percentage_score_performance > max_column_index:
            column_coordinates_percentage_score_performance = 33
            row_coordinates_percentage_score_performance += 1

    # TOTAL WEIGHTED SCORE WRITTEN WORKS
    column_coordinates_weighted_score_performance = 34
    row_coordinates_weighted_score_performance = 12

    for scores in grade_scores_queryset:
        weighted_score_performance = scores.weighted_score_quarterly
        rounded_weighted_score_performance = round(weighted_score_performance, 2)
        value_to_write = str(rounded_weighted_score_performance)
        sheet.cell(row=row_coordinates_weighted_score_performance, column=column_coordinates_weighted_score_performance, value=value_to_write)
        column_coordinates_weighted_score_performance += 1

        if column_coordinates_weighted_score_performance > max_column_index:
            column_coordinates_weighted_score_performance = 34
            row_coordinates_weighted_score_performance += 1
    

def write_initial_grade(sheet, grade_scores_queryset):
    max_column_index = 35
    column_coordinates_total_performance_tasks_score = 35
    row_coordinates_total_performance_tasks_score = 12

    for scores in grade_scores_queryset:
        total_performance_tasks_score = scores.initial_grades

        # Convert the float value to a string
        value_to_write = str(total_performance_tasks_score)

        sheet.cell(row=row_coordinates_total_performance_tasks_score, column=column_coordinates_total_performance_tasks_score, value=value_to_write)
        column_coordinates_total_performance_tasks_score += 1

        if column_coordinates_total_performance_tasks_score > max_column_index:  # Update max_column_index with the actual maximum column index
            column_coordinates_total_performance_tasks_score = 35  # Reset column index to the starting column
            row_coordinates_total_performance_tasks_score += 1  

def write_transmuted_grade(sheet, grade_scores_queryset):
    max_column_index = 36
    column_coordinates_total_performance_tasks_score = 36 
    row_coordinates_total_performance_tasks_score = 12

    for scores in grade_scores_queryset:
        total_performance_tasks_score = scores.transmuted_grades

        # Convert the float value to a string
        value_to_write = str(total_performance_tasks_score)

        sheet.cell(row=row_coordinates_total_performance_tasks_score, column=column_coordinates_total_performance_tasks_score, value=value_to_write)
        column_coordinates_total_performance_tasks_score += 1

        if column_coordinates_total_performance_tasks_score > max_column_index:  # Update max_column_index with the actual maximum column index
            column_coordinates_total_performance_tasks_score = 36  # Reset column index to the starting column
            row_coordinates_total_performance_tasks_score += 1  