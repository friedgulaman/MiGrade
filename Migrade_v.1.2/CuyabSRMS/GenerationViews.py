from django.http import HttpResponse
import openpyxl
import pandas as pd
import shutil
from datetime import datetime
from .utils import (
    write_student_names,
    write_scores_hps_written,
    write_scores_hps_performance,
    write_scores_hps_quarterly,
    write_written_works_scores,
    write_performance_tasks_scores,
    write_quarterly_assessment_scores,
    write_initial_grade,
    write_transmuted_grade,
)

from .models import GradeScores


def generate_excel_for_grades(request, grade, section, subject):
    # Get GradeScores for the specified grade, section, and subject
    grade_scores_queryset = GradeScores.objects.filter(class_record__grade=grade,
                                                        class_record__section=section,
                                                        class_record__subject=subject)

    # Original file path
    original_file_path = r'C:\Users\angelo\Documents\GitHub\ces_migrade\MiGrade\migrade_v.1.2\TEMPLATE - SF1.xlsx'

    # Generate a timestamp for the copy
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    
    # Create a copy of the Excel file with a timestamp in its name
    copied_file_path = fr'C:\Users\angelo\Documents\GitHub\ces_migrade\MiGrade\migrade_v.1.2\TEMPLATE - SF1_copy_{timestamp}.xlsx'
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

        # Write scores_hps_quarterly
        write_scores_hps_quarterly(sheet, grade_scores_queryset)

        # Write Written_works_score
        write_written_works_scores(sheet, grade_scores_queryset)

        #Write performance_tasks_score
        write_performance_tasks_scores(sheet, grade_scores_queryset)

        #Write quarterly assessment score
        write_quarterly_assessment_scores(sheet, grade_scores_queryset)

        #Write Initial Grade
        write_initial_grade(sheet, grade_scores_queryset)

        #Write transmuted Grade
        write_transmuted_grade(sheet, grade_scores_queryset)

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