from django.shortcuts import render, redirect
from django.urls import reverse
from django.db import transaction
from .models import ClassRecord, ArchivedClassRecord, GradeScores, ArchivedGradeScores, Student, ArchivedStudent, FinalGrade, ArchivedFinalGrade, GeneralAverage, ArchivedGeneralAverage, ArchivedQuarterlyGrades, QuarterlyGrades
import logging
from django.utils import timezone
from django.http import HttpResponseRedirect
from .utils import log_activity
from django.db import IntegrityError
from django.http import HttpResponse
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
                school_year=class_record.school_year,
                is_restore_approve = False
            )
            class_record_teacher = class_record.teacher


            user = request.user
            action = f'{user} archive a Class Record "{class_record.name}"'
            details = f'{user} archived the Class Record {class_record.name} in the system.'
            log_activity(user, action, details)

            logs = user, action, details    
            print(logs)
            # Retrieve the ClassRecord instance to be archived         
            # Archive related GradeScores
            archived_students = []

            for grade_score in class_record.GradeScores.all():
                archived_student, _ = ArchivedStudent.objects.get_or_create(
                    archived_name=grade_score.student,
                    archived_teacher=class_record_teacher
                )
                ArchivedGradeScores.objects.create(
                    archived_class_record=archived_class_record,
                    student=archived_student,
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

            archived_records = ArchivedClassRecord.objects.filter(id=archived_record_id, is_restore_approved=False)
            restore = is_restore_approved = True
            for restore_approved in archived_records:
                restore_approved.is_restore_approved = restore
                archived_record.save()

            # # Create a new instance of ClassRecord using archived data
            # class_record = ClassRecord.objects.create(
            #     name=archived_record.name,
            #     grade=archived_record.grade,
            #     section=archived_record.section,
            #     subject=archived_record.subject,
            #     teacher=archived_record.teacher,
            #     quarters=archived_record.quarters,
            #     school_year=archived_record.school_year,

            # )

            user = request.user
            action = f'{user} restore a Class Record "{archived_record.name}"'
            details = f'{user} restored the Class Record {archived_record.name} in the system.'
            log_activity(user, action, details)

            logs = user, action, details    
            print(logs)
            
            # Restore related GradeScores
            archived_grade_scores = archived_record.archived_gradescores.all()
            for archived_grade_score in archived_grade_scores:
                student_name = archived_grade_score.student.archived_name  # Adjust based on your ArchivedStudent model
                student = Student.objects.get(name=student_name) 
                GradeScores.objects.create(
                    student=student,
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
                archived_grade_score.student.delete()
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
            students_to_archive = Student.objects.filter(grade=grade, section=section)
            class_records_to_archive = ClassRecord.objects.filter(grade=grade, section=section)

            user = request.user
            action = f'{user} archive a Class "{grade} {section}"'
            details = f'{user} archived the Class {grade} {section} in the system.'
            log_activity(user, action, details)

            print(f"grade: {grade}")
            print(f"section: {section}")
            logs = user, action, details    
            print(logs)

            if class_records_to_archive.exists():
                for class_record in class_records_to_archive:
                    # Create an archived class record
                    archived_class_record = ArchivedClassRecord.objects.create(
                        name=class_record.name,
                        grade=class_record.grade,
                        section=class_record.section,
                        subject=class_record.subject,
                        teacher=class_record.teacher,
                        quarters=class_record.quarters,
                        date_archived=timezone.now(),
                        school_year=class_record.school_year
                    )

                    # Log the archived class record
                    print(f"Archived class record: {archived_class_record.name}")

                    # Archive associated GradeScores records for each student
                    for student in students_to_archive:
                        # Check if an archived student already exists with the same LRN
                        existing_archived_student = ArchivedStudent.objects.filter(archived_lrn=student.lrn).first()

                        if existing_archived_student:
                            # Update existing archived student information
                            existing_archived_student.archived_name = student.name
                            existing_archived_student.archived_sex = student.sex
                            existing_archived_student.archived_birthday = student.birthday
                            existing_archived_student.archived_teacher = student.teacher
                            existing_archived_student.archived_school_id = student.school_id
                            existing_archived_student.archived_division = student.division
                            existing_archived_student.archived_district = student.district
                            existing_archived_student.archived_school_name = student.school_name
                            existing_archived_student.archived_school_year = student.school_year
                            existing_archived_student.archived_grade = student.grade
                            existing_archived_student.archived_section = student.section
                            existing_archived_student.archived_class_type = student.class_type
                            existing_archived_student.save()
                            print(f"Updated archived student: {existing_archived_student.archived_name}")
                            
                            archived_student = existing_archived_student
                            
                        else:
                            # Create archived student if it doesn't exist
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
                                archived_section=student.section,
                                archived_class_type=student.class_type
                            )
                            print(f"Archived student: {archived_student.archived_name}")

                        # Archive associated GradeScores records
                        grade_scores_to_archive = GradeScores.objects.filter(student=student, class_record=class_record)
                        for grade_score in grade_scores_to_archive:
                            archived_grade_score = ArchivedGradeScores.objects.create(
                                archived_class_record=archived_class_record,
                                student=archived_student,
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
                                weighted_score_quarterly=grade_score.weighted_score_quarterly
                            )
                            # Log the archived grade score
                            print(f"Archived grade score for {archived_student.archived_name}")


                        # Add similar code blocks for archiving FinalGrade, QuarterlyGrades, and GeneralAverage records here
                        # Archive associated FinalGrade records
                        final_grades_to_archive = FinalGrade.objects.filter(student=student)
                        for final_grade in final_grades_to_archive:
                            # Check if an archived final grade already exists for the student, grade, and section
                            existing_archived_final_grade = ArchivedFinalGrade.objects.filter(
                                archived_student=archived_student,
                                archived_teacher=final_grade.teacher,
                                archived_grade=final_grade.grade,
                                archived_section=final_grade.section
                            ).first()

                            if existing_archived_final_grade:
                                # Update existing archived final grade
                                existing_archived_final_grade.archived_final_grade = final_grade.final_grade
                                existing_archived_final_grade.save()
                                print(f"Updated final grade for {archived_student.archived_name}: {final_grade.final_grade}")
                            else:
                                # Create archived final grade if it doesn't exist
                                ArchivedFinalGrade.objects.create(
                                    archived_teacher=final_grade.teacher,
                                    archived_student=archived_student,
                                    archived_grade=final_grade.grade,
                                    archived_section=final_grade.section,
                                    archived_final_grade=final_grade.final_grade
                                )
                                print(f"Archived final grade for {archived_student.archived_name}: {final_grade.final_grade}")

                        # Archive associated GeneralAverage records
                        general_averages_to_archive = GeneralAverage.objects.filter(student=student)
                        for general_average in general_averages_to_archive:
                            # Check if an existing archived general average record exists
                            existing_archived_general_average = ArchivedGeneralAverage.objects.filter(
                                archived_student=archived_student,
                                archived_grade=general_average.grade,
                                archived_section=general_average.section
                            ).first()

                            if existing_archived_general_average:
                                # Update existing archived general average record
                                existing_archived_general_average.archived_general_average = general_average.general_average
                                existing_archived_general_average.save()
                                print(f"Updated archived general average for {archived_student.archived_name}: {general_average.general_average}")
                            else:
                                # Create archived general average record if it doesn't exist
                                ArchivedGeneralAverage.objects.create(
                                    archived_student=archived_student,
                                    archived_grade=general_average.grade,
                                    archived_section=general_average.section,
                                    archived_general_average=general_average.general_average
                                )
                                print(f"Archived general average for {archived_student.archived_name}: {general_average.general_average}")

                        # Archive associated QuarterlyGrades records
                        quarterly_grades_to_archive = QuarterlyGrades.objects.filter(student=student)
                        for quarterly_grade in quarterly_grades_to_archive:
                            # Check if an existing archived quarterly grade record exists
                            existing_archived_quarterly_grade = ArchivedQuarterlyGrades.objects.filter(
                                archived_student=archived_student,
                                archived_quarter=quarterly_grade.quarter
                            ).first()

                            if existing_archived_quarterly_grade:
                                # Update existing archived quarterly grade record
                                existing_archived_quarterly_grade.archived_grades = quarterly_grade.grades
                                existing_archived_quarterly_grade.save()
                                print(f"Updated archived quarterly grades for {archived_student.archived_name}: {quarterly_grade.grades}")
                            else:
                                # Create archived quarterly grade record if it doesn't exist
                                ArchivedQuarterlyGrades.objects.create(
                                    archived_student=archived_student,
                                    archived_quarter=quarterly_grade.quarter,
                                    archived_grades=quarterly_grade.grades
                                )
                                print(f"Archived quarterly grades for {archived_student.archived_name}: {quarterly_grade.grades}")

                # Now delete the original students after archiving
                students_to_archive.delete()
                class_records_to_archive.delete()

                
                referer_url = request.META.get('HTTP_REFERER')
                if referer_url:
                    # Redirect to the referer URL
                    return redirect(referer_url)
                else:
                    # If referer URL is not available, redirect to a default URL
                    return redirect('archived_records')  # Redirect to the archived records page
                
            else:
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
                            archived_section=student.section,
                            archived_class_type=student.class_type
                        )

                    # Log the archived student
                        print(f"Archived student: {archived_student.archived_name}")
                    
                            # Archive associated GradeScores records
                        grade_scores_to_archive = GradeScores.objects.filter(student=student)
                        for grade_score in grade_scores_to_archive:
                                archived_grade_score = ArchivedGradeScores.objects.create(
                                    archived_class_record=archived_class_record,
                                    student=archived_student,
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
                                    weighted_score_quarterly=grade_score.weighted_score_quarterly
                                )
                                # Log the archived grade score
                                print(f"Archived grade score for {archived_student.archived_name}")

                        final_grades_to_archive = FinalGrade.objects.filter(student=student)
                        for final_grade in final_grades_to_archive:
                            # Check if an archived final grade already exists for the student, grade, and section
                            existing_archived_final_grade = ArchivedFinalGrade.objects.filter(
                                archived_student=archived_student,
                                archived_teacher=final_grade.teacher,
                                archived_grade=final_grade.grade,
                                archived_section=final_grade.section
                            ).first()

                            if existing_archived_final_grade:
                                # Update existing archived final grade
                                existing_archived_final_grade.archived_final_grade = final_grade.final_grade
                                existing_archived_final_grade.save()
                                print(f"Updated final grade for {archived_student.archived_name}: {final_grade.final_grade}")
                            else:
                                # Create archived final grade if it doesn't exist
                                ArchivedFinalGrade.objects.create(
                                    archived_teacher=final_grade.teacher,
                                    archived_student=archived_student,
                                    archived_grade=final_grade.grade,
                                    archived_section=final_grade.section,
                                    archived_final_grade=final_grade.final_grade
                                )
                                print(f"Archived final grade for {archived_student.archived_name}: {final_grade.final_grade}")

                        # Archive associated GeneralAverage records
                        general_averages_to_archive = GeneralAverage.objects.filter(student=student)
                        for general_average in general_averages_to_archive:
                            # Check if an existing archived general average record exists
                            existing_archived_general_average = ArchivedGeneralAverage.objects.filter(
                                archived_student=archived_student,
                                archived_grade=general_average.grade,
                                archived_section=general_average.section
                            ).first()

                            if existing_archived_general_average:
                                # Update existing archived general average record
                                existing_archived_general_average.archived_general_average = general_average.general_average
                                existing_archived_general_average.save()
                                print(f"Updated archived general average for {archived_student.archived_name}: {general_average.general_average}")
                            else:
                                # Create archived general average record if it doesn't exist
                                ArchivedGeneralAverage.objects.create(
                                    archived_student=archived_student,
                                    archived_grade=general_average.grade,
                                    archived_section=general_average.section,
                                    archived_general_average=general_average.general_average
                                )
                                print(f"Archived general average for {archived_student.archived_name}: {general_average.general_average}")

                        # Archive associated QuarterlyGrades records
                        quarterly_grades_to_archive = QuarterlyGrades.objects.filter(student=student)
                        for quarterly_grade in quarterly_grades_to_archive:
                            # Check if an existing archived quarterly grade record exists
                            existing_archived_quarterly_grade = ArchivedQuarterlyGrades.objects.filter(
                                archived_student=archived_student,
                                archived_quarter=quarterly_grade.quarter
                            ).first()

                            if existing_archived_quarterly_grade:
                                # Update existing archived quarterly grade record
                                existing_archived_quarterly_grade.archived_grades = quarterly_grade.grades
                                existing_archived_quarterly_grade.save()
                                print(f"Updated archived quarterly grades for {archived_student.archived_name}: {quarterly_grade.grades}")
                            else:
                                # Create archived quarterly grade record if it doesn't exist
                                ArchivedQuarterlyGrades.objects.create(
                                    archived_student=archived_student,
                                    archived_quarter=quarterly_grade.quarter,
                                    archived_grades=quarterly_grade.grades
                                )
                                print(f"Archived quarterly grades for {archived_student.archived_name}: {quarterly_grade.grades}")
                # Now delete the original students after archiving
                students_to_archive.delete()
                class_records_to_archive.delete()

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
        return HttpResponse("An error occurred during archival: " + str(e), status=500)
    


def restore_archived_students(request, grade, section):
    try:
        user = request.user
        action = f'{user} restore a Class "{grade} {section}"'
        details = f'{user} restored the Class {grade} {section} in the system.'
        log_activity(user, action, details)

        logs = user, action, details    
        print(logs)
        with transaction.atomic():
            # Get the archived students based on grade and section
            archived_students = ArchivedStudent.objects.filter(archived_grade=grade, archived_section=section)
            archived_class_records = ArchivedClassRecord.objects.filter(grade=grade, section=section)
            
            if archived_class_records.exists():
                for archived_class_record in archived_class_records:
                    class_record, created = ClassRecord.objects.get_or_create(
                        name=archived_class_record.name,
                        grade=archived_class_record.grade,
                        section=archived_class_record.section,
                        subject=archived_class_record.subject,
                        teacher=archived_class_record.teacher,
                        quarters=archived_class_record.quarters,
                        school_year=archived_class_record.school_year
                    )
                    print(f"Restore classrecord for {class_record.name}")

                    # Filter grade scores based on the archived class record
                    archived_grade_scores = ArchivedGradeScores.objects.filter(archived_class_record=archived_class_record)

                    for archived_grade_score in archived_grade_scores:
                        print(f"Archived GradeScore details: {archived_grade_score}")

                        # Restore the student associated with the archived grade score
                        archived_student = archived_grade_score.student
                        student, _ = Student.objects.get_or_create(
                            name=archived_grade_score.student.archived_name,
                            lrn=archived_grade_score.student.archived_lrn,
                            sex=archived_grade_score.student.archived_sex,
                            birthday=archived_grade_score.student.archived_birthday,
                            teacher=archived_grade_score.student.archived_teacher,
                            school_id=archived_grade_score.student.archived_school_id,
                            division=archived_grade_score.student.archived_division,
                            district=archived_grade_score.student.archived_district,
                            school_name=archived_grade_score.student.archived_school_name,
                            school_year=archived_grade_score.student.archived_school_year,
                            grade=archived_grade_score.student.archived_grade,
                            section=archived_grade_score.student.archived_section,
                            class_type=archived_grade_score.student.archived_class_type
                        )
                        print(f"Restore student for {student.name}")

                        # Create GradeScores object for the restored student and class record
                        GradeScores.objects.create(
                            class_record=class_record,
                            student=student,
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
                            weighted_score_quarterly=archived_grade_score.weighted_score_quarterly
                        )

                        print(f"Gradescores for {student.name}")
                        print("GradeScore restored.")

                        # Restore associated FinalGrade records
                        archived_final_grades = ArchivedFinalGrade.objects.filter(archived_student=archived_student)
                        for archived_final_grade in archived_final_grades:
                            # Check if an existing FinalGrade record exists
                            existing_final_grade = FinalGrade.objects.filter(
                                student=student,
                                grade=archived_final_grade.archived_grade,
                                section=archived_final_grade.archived_section
                            ).first()

                            if existing_final_grade:
                                # Update existing FinalGrade record
                                existing_final_grade.final_grade = archived_final_grade.archived_final_grade
                                existing_final_grade.save()
                                print(f"Updated final grade for {student.name}: {archived_final_grade.archived_final_grade}")
                            else:
                                # Create FinalGrade record if it doesn't exist
                                FinalGrade.objects.create(
                                    teacher=archived_final_grade.archived_teacher,
                                    student=student,
                                    grade=archived_final_grade.archived_grade,
                                    section=archived_final_grade.archived_section,
                                    final_grade=archived_final_grade.archived_final_grade
                                )
                                print(f"Restored final grade for {student.name}: {archived_final_grade.archived_final_grade}")

                        # Restore associated GeneralAverage records
                        archived_general_averages = ArchivedGeneralAverage.objects.filter(archived_student=archived_student)
                        for archived_general_average in archived_general_averages:
                            # Check if an existing GeneralAverage record exists
                            existing_general_average = GeneralAverage.objects.filter(
                                student=student,
                                grade=archived_general_average.archived_grade,
                                section=archived_general_average.archived_section
                            ).first()

                            if existing_general_average:
                                # Update existing GeneralAverage record
                                existing_general_average.general_average = archived_general_average.archived_general_average
                                existing_general_average.save()
                                print(f"Updated general average for {student.name}: {archived_general_average.archived_general_average}")
                            else:
                                # Create GeneralAverage record if it doesn't exist
                                GeneralAverage.objects.create(
                                    student=student,
                                    grade=archived_general_average.archived_grade,
                                    section=archived_general_average.archived_section,
                                    general_average=archived_general_average.archived_general_average
                                )
                                print(f"Restored general average for {student.name}: {archived_general_average.archived_general_average}")

                        # Restore associated QuarterlyGrades records
                        archived_quarterly_grades = ArchivedQuarterlyGrades.objects.filter(archived_student=archived_student)
                        for archived_quarterly_grade in archived_quarterly_grades:
                            # Check if an existing QuarterlyGrades record exists
                            existing_quarterly_grade = QuarterlyGrades.objects.filter(
                                student=student,
                                quarter=archived_quarterly_grade.archived_quarter
                            ).first()

                            if existing_quarterly_grade:
                                # Update existing QuarterlyGrades record
                                existing_quarterly_grade.grades = archived_quarterly_grade.archived_grades
                                existing_quarterly_grade.save()
                                print(f"Updated quarterly grades for {student.name}: {archived_quarterly_grade.archived_grades}")
                            else:
                                # Create QuarterlyGrades record if it doesn't exist
                                QuarterlyGrades.objects.create(
                                    student=student,
                                    quarter=archived_quarterly_grade.archived_quarter,
                                    grades=archived_quarterly_grade.archived_grades
                                )
                                print(f"Restored quarterly grades for {student.name}: {archived_quarterly_grade.archived_grades}")

                    # Delete the archived student instance
                archived_students.delete()
                    # Delete the archived class record instance after restoring associated data
                archived_class_records.delete()
                return HttpResponseRedirect(reverse('archived_records'))
            
            else:
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
                        section=archived_student.archived_section,
                        class_type=archived_student.archived_class_type
                    )

                        # Restore associated grade scores
                    archived_grade_scores = ArchivedGradeScores.objects.filter(student=archived_student)
                    for archived_grade_score in archived_grade_scores:
                            GradeScores.objects.create(
                                class_record=class_record,
                                student=restored_student,
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
                                weighted_score_quarterly=archived_grade_score.weighted_score_quarterly
                            )

                        
                    archived_final_grades = ArchivedFinalGrade.objects.filter(archived_student=archived_student)
                    for archived_final_grade in archived_final_grades:
                        # Create a new FinalGrade instance with restored data
                        FinalGrade.objects.create(
                            teacher=archived_final_grade.archived_teacher,
                            student=restored_student,
                            grade=archived_final_grade.archived_grade,
                            section=archived_final_grade.archived_section,
                            final_grade=archived_final_grade.archived_final_grade
                        )

                    # Restore associated general averages
                    archived_general_averages = ArchivedGeneralAverage.objects.filter(archived_student=archived_student)
                    for archived_general_average in archived_general_averages:
                        # Create a new GeneralAverage instance with restored data
                        GeneralAverage.objects.create(
                            student=restored_student,
                            grade=archived_general_average.archived_grade,
                            section=archived_general_average.archived_section,
                            general_average=archived_general_average.archived_general_average
                        )

                    # Restore associated quarterly grades
                    archived_quarterly_grades = ArchivedQuarterlyGrades.objects.filter(archived_student=archived_student)
                    for archived_quarterly_grade in archived_quarterly_grades:
                        # Create a new QuarterlyGrades instance with restored data
                        QuarterlyGrades.objects.create(
                            student=restored_student,
                            quarter=archived_quarterly_grade.archived_quarter,
                            grades=archived_quarterly_grade.archived_grades
                        )

                    # Delete the archived student instance
                    archived_student.delete()

                return HttpResponseRedirect(reverse('archived_records'))


    except Exception as e:
        print(f"Error occurred during restoration: {str(e)}")
        return HttpResponseRedirect(reverse('error_page'))
