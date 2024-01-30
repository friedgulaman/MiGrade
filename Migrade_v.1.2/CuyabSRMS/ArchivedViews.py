from django.shortcuts import render, redirect
from django.urls import reverse
from django.db import transaction
from .models import ClassRecord, ArchivedClassRecord, GradeScores, ArchivedGradeScores, Student, ArchivedStudent, FinalGrade, ArchivedFinalGrade
import logging

def archive_class_record(request, class_record_id):
    
    try:

        with transaction.atomic():
            class_record = ClassRecord.objects.get(id=class_record_id)
            archived_class_record = ArchivedClassRecord.objects.create(
                name=class_record.name,
                grade=class_record.grade,
                section=class_record.section,
                subject=class_record.subject,
                teacher=class_record.teacher,
                quarters=class_record.quarters,
            )
            # Retrieve the ClassRecord instance to be archived         
            # Archive related GradeScores
            for grade_score in class_record.GradeScores.all():
                ArchivedGradeScores.objects.create(
                    archived_class_record=archived_class_record,
                    student=grade_score.student,
                    scores_hps_written=grade_score.scores_hps_written,
                    scores_hps_performance=grade_score.scores_hps_performance,
                    total_ww_hps=grade_score.total_ww_hps,
                    total_pt_hps=grade_score.total_pt_hps,
                    total_qa_hps=grade_score.total_qa_hps,
                    written_works_scores=grade_score.written_works_scores,
                    performance_task_scores=grade_score.performance_task_scores,
                    initial_grades=grade_score.initial_grades,
                    transmuted_grades=grade_score.transmuted_grades,
                    total_score_written=grade_score.total_score_written,
                    total_max_score_written=grade_score.total_max_score_written,
                    total_score_performance=grade_score.total_score_performance,
                    total_max_score_performance=grade_score.total_max_score_performance,
                    total_score_quarterly=grade_score.total_score_quarterly,
                    total_max_score_quarterly=grade_score.total_max_score_quarterly,
                    percentage_score_written=grade_score.percentage_score_written,
                    percentage_score_performance=grade_score.percentage_score_performance,
                    percentage_score_quarterly=grade_score.percentage_score_quarterly,
                    weight_input_written=grade_score.weight_input_written,
                    weight_input_performance=grade_score.weight_input_performance,
                    weight_input_quarterly=grade_score.weight_input_quarterly,
                    weighted_score_written=grade_score.weighted_score_written,
                    weighted_score_performance=grade_score.weighted_score_performance,
                    weighted_score_quarterly=grade_score.weighted_score_quarterly,
                    # Copy other relevant fields
                )


            # Delete the original ClassRecord instance
            class_record.delete()

            referer_url = request.META.get('HTTP_REFERER')
            
            if referer_url:
        # Redirect to the referer URL
                return redirect(referer_url)
            else:
        # If referer URL is not available, redirect to a default URL
                return redirect('archived_records')  # Redirect to the archived records page
    except Exception as e:
        print(f"Error occurred during archiving: {str(e)}")
        return redirect('error_page')  # Redirect to an error page or handle as needed
    

def restore_archived_record(request, archived_record_id):
    archived_record = ArchivedClassRecord.objects.get(id=archived_record_id)
    
    try:
        with transaction.atomic():
            # Create a new instance of ClassRecord using archived data
            class_record = ClassRecord.objects.create(
                name=archived_record.name,
                grade=archived_record.grade,
                section=archived_record.section,
                subject=archived_record.subject,
                teacher=archived_record.teacher,
                quarters=archived_record.quarters,
            )
            
            # Restore related GradeScores
            archived_grade_scores = archived_record.archived_gradescores.all()
            for archived_grade_score in archived_grade_scores:
                GradeScores.objects.create(
                    student=archived_grade_score.student,
                    class_record=class_record,
                    scores_hps_written=archived_grade_score.scores_hps_written,
                    scores_hps_performance=archived_grade_score.scores_hps_performance,
                    total_ww_hps=archived_grade_score.total_ww_hps,
                    total_pt_hps=archived_grade_score.total_pt_hps,
                    total_qa_hps=archived_grade_score.total_qa_hps,
                    written_works_scores=archived_grade_score.written_works_scores,
                    performance_task_scores=archived_grade_score.performance_task_scores,
                    initial_grades=archived_grade_score.initial_grades,
                    transmuted_grades=archived_grade_score.transmuted_grades,
                    total_score_written=archived_grade_score.total_score_written,
                    total_max_score_written=archived_grade_score.total_max_score_written,
                    total_score_performance=archived_grade_score.total_score_performance,
                    total_max_score_performance=archived_grade_score.total_max_score_performance,
                    total_score_quarterly=archived_grade_score.total_score_quarterly,
                    total_max_score_quarterly=archived_grade_score.total_max_score_quarterly,
                    percentage_score_written=archived_grade_score.percentage_score_written,
                    percentage_score_performance=archived_grade_score.percentage_score_performance,
                    percentage_score_quarterly=archived_grade_score.percentage_score_quarterly,
                    weight_input_written=archived_grade_score.weight_input_written,
                    weight_input_performance=archived_grade_score.weight_input_performance,
                    weight_input_quarterly=archived_grade_score.weight_input_quarterly,
                    weighted_score_written=archived_grade_score.weighted_score_written,
                    weighted_score_performance=archived_grade_score.weighted_score_performance,
                    weighted_score_quarterly=archived_grade_score.weighted_score_quarterly,
                    # Copy other relevant fields
                )
            # Delete the archived record after restoration
            archived_record.delete()

            return redirect('archived_records')
    except Exception as e:
        print(f"Error occurred during restoration: {str(e)}")
        return redirect('error_page')  # Redirect to an error page or handle as needed

def archived_records(request):
    archived_records = ArchivedClassRecord.objects.all()
    archived_students =  ArchivedStudent.objects.values('archived_grade', 'archived_section').distinct()
    return render(request, 'archive_template/archived_records.html', {'archived_records': archived_records, 'archived_students': archived_students})

# def archived_records(request):
#     archived_records = ArchivedClassRecord.objects.all()
#     return render(request, 'archive_template/archived_records.html', {'archived_records': archived_records})


def archive_students_with_grade_and_section(request, grade, section):
    try:
        with transaction.atomic():
            # Get the students with the specified grade and section
            students_to_archive = Student.objects.filter(grade=grade, section=section, teacher=request.user.teacher)

            # Iterate over each student and archive them
            for student in students_to_archive:
                # Archive the student
                archived_student = ArchivedStudent.objects.create(
                    archived_name=student.name,
                    archived_lrn=student.lrn,
                    archived_sex=student.sex,
                    archived_birthday=student.birthday,
                    archived_teacher=student.teacher,
                    archived_school_id=student.school_id,
                    archived_division=student.division,
                    archived_district=student.district,
                    archived_school_name=student.school_name,
                    archived_school_year=student.school_year,
                    archived_grade=student.grade,
                    archived_section=student.section
                )

                # Log the archived student
                print(f"Archived student: {archived_student.archived_name}")

                # Archive associated FinalGrade records
                final_grades_to_archive = FinalGrade.objects.filter(student=student)
                for final_grade in final_grades_to_archive:
                    archived_final_grade = ArchivedFinalGrade.objects.create(
                        original_final_grade=final_grade,
                        archived_teacher=final_grade.teacher,
                        archived_student=final_grade.student,
                        archived_grade=final_grade.grade,
                        archived_section=final_grade.section,
                        archived_final_grade=final_grade.final_grade
                    )
                    # Log the archived final grade
                    print(f"Archived final grade for {archived_final_grade.archived_student.name}")


            # Now delete the original students after archiving
            students_to_archive.delete()

            referer_url = request.META.get('HTTP_REFERER')
            if referer_url:
                # Redirect to the referer URL
                return redirect(referer_url)
            else:
                # If referer URL is not available, redirect to a default URL
                return redirect('archived_records')  # Redirect to the archived records page

    except Exception as e:
        # Handle exceptions gracefully
        print(f"Error occurred during archiving: {str(e)}")
        return redirect('error_page')  # Redirect to an error page or handle as needed
    

def restore_archived_students(request, grade, section):
    try:
        # Get the archived students based on grade and section
        archived_students = ArchivedStudent.objects.filter(archived_grade=grade, archived_section=section)

        # Restore each archived student
        for archived_student in archived_students:
            # Create a new student instance using the archived student's data
            restored_student = Student.objects.create(
                name=archived_student.archived_name,
                lrn=archived_student.archived_lrn,
                sex=archived_student.archived_sex,
                birthday=archived_student.archived_birthday,
                teacher=archived_student.archived_teacher,
                school_id=archived_student.archived_school_id,
                division=archived_student.archived_division,
                district=archived_student.archived_district,
                school_name=archived_student.archived_school_name,
                school_year=archived_student.archived_school_year,
                grade=archived_student.archived_grade,
                section=archived_student.archived_section
            )

            # Delete the archived student instance
            archived_student.delete()

        return redirect('archived_records')
    except Exception as e:
        print(f"Error occurred during restoration: {str(e)}")
        return redirect('error_page')  # Redirect to an error page or handle as needed