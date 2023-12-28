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

# def write_scores_hps_quarterly(sheet, grade_scores_queryset):
#     column_coordinate = 32
#     row_coordinate = 10

#     while sheet.cell(row=row_coordinate, column=column_coordinate).value:
#         column_coordinate += 1

#     for score in grade_scores_queryset:
#         values_to_write = score.scores_hps_quarterly
#         for value in values_to_write:
#             sheet.cell(row=row_coordinate, column=column_coordinate, value=value)
#             column_coordinate += 1

#         column_coordinate = 32

#     # TOTAL HIGHEST POSSIBLE SCORE IN PERFORMANCE TASKS
        
#     column_coordinates_total_scores_hps_performance = 
#     row_coordinate_total_scores_hps_performance = 10

#     for scores_total_pt_hps in grade_scores_queryset:
#         values_to_write = scores_total_pt_hps.total_qa_hps


#         value_to_write = str(values_to_write)

#         sheet.cell(row=row_coordinate_total_scores_hps_performance, column=column_coordinates_total_scores_hps_performance, value=value_to_write)
#         column_coordinates_total_scores_hps_performance += 1

#         column_coordinates_total_scores_hps_performance = 29

#     # PERCENTAGE SCORE IN HIGHEST POSSIBLE SCORE IN WRITTEN WORKS
#     column_coordinate_total_pt_ps = 32
#     row_coordinate_total_pt_ps = 10

#     for scores_total_pt_ps in grade_scores_queryset:
#         value_to_write = 100

#         value_to_write = str(value_to_write)
#         sheet.cell(row=row_coordinate_total_pt_ps, column=column_coordinate_total_pt_ps, value=value_to_write)
#         column_coordinate_total_pt_ps += 1

#         column_coordinate_total_pt_ps = 32

#     # WEIGHT INPUT IN HIGHEST POSSIBLE SCORE
#     column_coordinate_weight_input_performance = 33
#     row_coordinate_weight_input_performance = 10

#     for scores_weight_input_performance in grade_scores_queryset:
#         value_to_write = scores_weight_input_performance.weight_input_quarterly
#         value_to_write = str(value_to_write)
#         sheet.cell(row=row_coordinate_weight_input_performance, column=column_coordinate_weight_input_performance, value=value_to_write)
#         column_coordinate_weight_input_performance += 1

#         column_coordinate_weight_input_performance = 33

def write_quarterly_assessment_score(sheet, grade_scores_queryset):
    column_coordinates = 32
    row_coordinates = 10

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
            row_coordinates_percentage_score_written += 1


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
    
def generate_excel_for_grades(request, grade, section, subject):
    # Get GradeScores for the specified grade, section, and subject
    grade_scores_queryset = GradeScores.objects.filter(class_record__grade=grade,
                                                        class_record__section=section,
                                                        class_record__subject=subject)

    # Original file path
    original_file_path = r'C:\Users\Administrator\Documents\ces_migrade\MiGrade\Migrade_v.1.2\TEMPLATE - SF1.xlsx'

    # Generate a timestamp for the copy
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    
    # Create a copy of the Excel file with a timestamp in its name
    copied_file_path = fr'C:\Users\Administrator\Documents\ces_migrade\MiGrade\Migrade_v.1.2\TEMPLATE - SF1_copy_{timestamp}.xlsx'
    shutil.copyfile(original_file_path, copied_file_path)

    try:
        # Open the copied Excel file
        workbook = openpyxl.load_workbook(copied_file_path)

        # Select the desired sheet (use the correct sheet name from the output)
        desired_sheet_name = 'Sheet1'
        sheet = workbook[desired_sheet_name]

        # # Write student names
        write_student_names(sheet, grade_scores_queryset)

        # Write scores_hps_written
        write_scores_hps_written(sheet, grade_scores_queryset)

        # Write scores_hps_performance
        write_scores_hps_performance(sheet, grade_scores_queryset)

        # # Write scores_hps_quarterly
        # write_scores_hps_quarterly(sheet, grade_scores_queryset)

        # Write Written_works_score
        write_written_works_scores(sheet, grade_scores_queryset)

        #Write performance_tasks_score
        write_performance_tasks_scores(sheet, grade_scores_queryset)

        #Write 

        # Save the changes to the workbook
        workbook.save(copied_file_path)

        # Create an HTTP response with the updated Excel file
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename=grades_export_{timestamp}.xlsx'

        with open(copied_file_path, 'rb') as excel_file:
            response.write(excel_file.read())

        return response

    except Exception as e:
        # Handle exceptions, such as a corrupted file
        return HttpResponse(f"An error occurred: {e}")