import json
import queue
from django.http import Http404, JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from .models import AcceptedMessage, AdvisoryClass, FinalGrade, Grade, InboxMessage,  Quarters, Section, Teacher, ClassRecord, GradeScores, Student
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.db import transaction
from collections import defaultdict
from django.db import IntegrityError
from django.db.models import Q
from .views import log_activity
from django.db.models import F

def transfer_record(request):
    teacher = request.user.teacher
    final_grades = FinalGrade.objects.filter(teacher=teacher)
    unique_final_grades = final_grades.values('grade', 'section', 'subject').distinct()
    
  
    # Filter based on related students' class_type in GradeScores
    grade_scores = GradeScores.objects.filter(student__class_type='Subject', student__teacher_id=teacher).distinct()

    # Extract unique ClassRecord instances from the filtered GradeScores
    class_records = set(score.class_record for score in grade_scores)



    print(unique_final_grades)
    context = {
        'class_records': class_records,
        'unique_final_grades': unique_final_grades,
    }

    return render(request, 'teacher_template/adviserTeacher/transfer_records.html', context)



def final_grade_details(request):
    teacher = request.user.teacher
    # Retrieve data based on the provided grade, section, and subject
    grade = request.GET.get('grade')
    section = request.GET.get('section')
    subject = request.GET.get('subject')

    final_grades = FinalGrade.objects.filter(grade=grade, section=section, subject=subject, teacher=teacher)
    # Extract final grade JSON data
    final_grade_data = []
    for final_grade in final_grades:
        final_grade_data.append(final_grade.final_grade)

    context = {
        'final_grades': final_grades,
        'final_grade_data': final_grade_data,
    }

    return render(request, 'teacher_template/adviserTeacher/final_grades_details.html', context)


def transfer_details(request):
    # Use 'class_record_id' instead of 'class_record_id'
    class_record_id = request.GET.get('id')

    # Check if class_record_id is provided in the request
    if class_record_id:
        # Filter based on related students' class_type in GradeScores
        grade_scores = GradeScores.objects.filter(student__class_type='Subject', class_record__id=class_record_id).distinct()

        # Extract unique ClassRecord instances from the filtered GradeScores
        class_records = set(score.class_record for score in grade_scores)
    else:
        # If class_record_id is not provided, handle accordingly (e.g., redirect, show an error message)
        class_records = None

    return render(request, 'teacher_template/adviserTeacher/transfer_details.html', {'class_records': class_records})

@csrf_exempt
@login_required
def get_teacher_list(request):
    if request.method == 'GET':
        # Get the currently logged-in teacher
        current_teacher = request.user.teacher
        current_subject_classes = []
        
        print("before current_subject", current_subject_classes)

        # Retrieve all subject classes of the current teacher
        for grade_section, class_type in current_teacher.grade_section.items():
            if class_type == 'Subject Class' or class_type == 'Advisory Class, Subject Class':
                current_subject_classes.append(grade_section)
        print("Current Subject Classes:", current_subject_classes)

        teacher_list = []

        # If the current teacher has any subject classes
        if current_subject_classes:
            # Iterate through each teacher
            for teacher in Teacher.objects.all():
                # Check if grade_section exists and is not None
                print("teacher", teacher.user.first_name)
                print(f"teacher {teacher.user.first_name}`s = {teacher.grade_section}")
                if teacher.grade_section:
                    # Iterate through each grade_section of the current teacher
                    for current_subject_class in current_subject_classes:
                        print("AVAILABLE CURRENT SUBJECT CLASS", current_subject_class)
                        # Check if the teacher has the same grade_section as the current teacher
                        if current_subject_class in teacher.grade_section.keys():
                            # Check if the value of the grade_section contains 'Advisory Class'
                            # or 'Advisory Class, Subject Class'
                            if 'Advisory Class' in teacher.grade_section[current_subject_class] or 'Advisory Class, Subject Class' in teacher.grade_section[current_subject_class]:
                                # Create a dictionary to store teacher information
                                teacher_info = {
                                    'id': teacher.id,
                                    'name': f"{teacher.user.first_name} {teacher.user.last_name}",
                                    'grade_section': current_subject_class
                                }
                                teacher_list.append(teacher_info)
                                # break  # Break after finding a match to avoid duplicate entries
        print(teacher_list)
        return JsonResponse({'teachers': teacher_list})


    elif request.method == 'POST':
        try:
            # Assuming you receive JSON data in the request
            data = json.loads(request.body.decode('utf-8'))
            teacher_id = data.get('teacher_id')
            json_data = data.get('json_data')

            # Now you can use teacher_id and json_data as needed
            # For example, save the json_data to the corresponding teacher

            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})


@require_POST
@login_required
def submit_json(request):
    try:
        # Get JSON data from request.body
        json_data = json.loads(request.body.decode('utf-8'))

        to_teacher = json_data.get('teacherId')
        user = request.user
        from_teacher = user.teacher  # Assuming user.teacher is a Teacher instance
        file_name = json_data.get('className')
        grade = json_data.get('transferRecords', [])[0].get('grade', None)
        section = json_data.get('transferRecords', [])[0].get('section', None)

        class_type = "Advisory" or "Advisory Class, Subject Class"

        # Check if the section with the specified name, class_type, and teacher_id exists
        existing_section = Section.objects.filter(name=section, class_type="Advisory", teacher_id=to_teacher).exists()

        if existing_section:
            # Save the data to the InboxMessage model
            InboxMessage.objects.create(to_teacher=to_teacher, from_teacher=from_teacher, json_data=json.dumps(json_data), file_name=file_name)
            return JsonResponse({'success': True, 'message': 'Data submitted successfully.'})
        else:
            return JsonResponse({'success': False, 'message': 'Invalid section or teacher.'})

    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})
    
@csrf_exempt
@require_POST
@login_required
def transfer_json_to_teacher(request):
    if request.method == 'POST':
        try:
            json_data = json.loads(request.body.decode('utf-8'))
            target_teacher_id = json_data.get('target_teacher')
            from_teacher_id = json_data.get('teacher')
            subject = json_data.get('subject')
            grade = json_data.get('grade')
            section = json_data.get('section')
            first_student = json_data['students'][0]  # Get the first student
            quarter_info = first_student['quarter']  # Access the quarter information
            quarter_name = next(iter(quarter_info.keys()))
            file_name = (grade, section, quarter_name, subject)
            section = json_data.get('section')
            user = request.user
            action = f'{user} send the {grade} {section} - {subject} {quarter_name} Classrecord to the adviser of {grade} {section}'
            details = f'{user} send the {grade} {section} - {subject} {quarter_name} Classrecord to the adviser of {grade} {section}'
            log_activity(user, action, details)

            print(json_data)
            print(file_name)
            print(from_teacher_id)
            class_types_to_check = ['Advisory Class', 'Advisory Class, Subject Class']
            # Check if the section with the specified name, class_type, and teacher_id exists
            existing_section = Section.objects.filter( Q(name=section) &
            (Q(class_type__icontains=class_types_to_check[0]) | Q(class_type__icontains=class_types_to_check[1]))).exists()
            print(existing_section)
            if existing_section:
                # Save the data to the InboxMessage model
                InboxMessage.objects.create(to_teacher=target_teacher_id, from_teacher=from_teacher_id, json_data=json.dumps(json_data), file_name=file_name)
                return JsonResponse({'success': True, 'message': 'Data submitted successfully.'})
            else:
                return JsonResponse({'success': False, 'message': 'Invalid section or teacher.'})

        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})

    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)

def inbox_open(request):
    try:
        user = request.user

        # Check if the logged-in user is a teacher
        if hasattr(user, 'teacher'):
            teacher = user.teacher.id
            # Get inbox messages where the logged-in teacher is the intended recipient
            inbox_messages = InboxMessage.objects.filter(to_teacher=teacher)
            accepted_messages = AcceptedMessage.objects.filter(accepted_by_id=teacher).order_by(F('accepted_at').desc())

            # Convert json_data to dictionary for each accepted message
            for message in accepted_messages:
                message.json_data = json.loads(message.json_data)

            # Convert json_data to dictionary for each inbox message
            for message in inbox_messages:
                message.json_data = json.loads(message.json_data)

            context = {
                'inbox_messages': inbox_messages,
                'accepted_messages': accepted_messages
            }
            return render(request, 'teacher_template/adviserTeacher/inbox.html', context)

        else:
            # Handle the case where the logged-in user is not a teacher
            return render(request, 'teacher_template/adviserTeacher/inbox.html', {'inbox_messages': [], 'accepted_messages': []})

    except Exception as e:
        # Handle any exceptions
        print(f"Error in inbox_open: {e}")
        return render(request, 'teacher_template/adviserTeacher/inbox.html', {'inbox_messages': [], 'accepted_messages': []})



def inbox_count(request):
    try:
        user = request.user
        # Check if the logged-in user is a teacher
        if hasattr(user, 'teacher'):
            teacher = user.teacher.id
            count = InboxMessage.objects.filter(to_teacher=teacher).count()
            return {'count': count}
        else:
            # Handle the case where the logged-in user is not a teacher
            count = 0
            return{'count': count}
    except Exception as e:
        # Handle any exceptions
        return JsonResponse({'success': False, 'message': str(e)})


def transfer_quarterly_grade(request, grade, section, subject, class_record_id):
    teacher = request.user.teacher
    teacher_id = teacher.id
    # Filter Section objects based on provided parameters
    class_types_to_check = ['Subject Class', 'Advisory Class, Subject Class']

    sections = Section.objects.filter(
    Q(name=section) &
    (Q(class_type__icontains=class_types_to_check[0]) | Q(class_type__icontains=class_types_to_check[1]) )
    )
    
  
    # Check if there is more than one Section returned
    if sections.count() != 1:
        raise Http404("Section not found or multiple sections found for the provided parameters.")

    # Retrieve the specific class record based on the provided class_record_id
    class_record = get_object_or_404(ClassRecord, id=class_record_id, grade=grade, section=sections.first(), subject=subject, teacher_id=teacher)

    # Retrieve grade scores related to the class record
    grade_scores = GradeScores.objects.filter(class_record=class_record)

    context = {
        'class_record': class_record,
        'grade_scores': grade_scores,
    }
    
    return render(request, "teacher_template/adviserTeacher/transfer_quarterly_grade.html", context)

@require_POST
def reject_message(request):
    message_id = request.POST.get('message_id')

    try:
        message = InboxMessage.objects.get(pk=message_id)
        message.delete()
        return JsonResponse({'success': True, 'message': 'Message rejected and deleted.'})
    except InboxMessage.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Message not found'})

@require_POST
def accept_message(request):
    message_id = request.POST.get('message_id')
    teacher = request.user.teacher

    try:
        message = InboxMessage.objects.get(pk=message_id)
        json_data = json.loads(message.json_data)
        
        existing_data = check_existing_data(json_data) 
        
        if existing_data['exists']: 
            message.delete()
            return JsonResponse({'success': True, 'message': existing_data['message']})
        else:
            save_data(message, json_data, teacher)  # Call save_data only once
            save_accepted_message(message)  # Call save_accepted_message to save the accepted message
            message.delete()
            return JsonResponse({'success': True, 'message': '✓ Successfully Saved Records.'})
    except InboxMessage.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Message not found'})

def check_existing_data(json_data):
    quarter_field_mapping = {
        "1st Quarter": "first_quarter",
        "2nd Quarter": "second_quarter",
        "3rd Quarter": "third_quarter",
        "4th Quarter": "fourth_quarter"
    }

    all_students_exist = True  # Flag to track if data exists for all students

    for student in json_data.get('students', []):
        student_name = student.get('name')
        student_exists = False  # Flag to track if data exists for current student

        for quarter in student.get('quarter', {}):
            field_name = quarter_field_mapping.get(quarter)
            if not field_name:
                continue

            existing_advisory_classes = AdvisoryClass.objects.filter(
                grade=json_data.get('grade'),
                section=json_data.get('section'),
                student__name=student_name,
            )

            for existing_advisory_class in existing_advisory_classes:
                grades_data = existing_advisory_class.get_grades_data()
                if not grades_data:
                    continue

                subject_teacher_data = grades_data.get(json_data.get('subject'), {})
                existing_grade = subject_teacher_data.get(field_name)
                if existing_grade is None:
                    continue  # No existing value found, continue searching

                # If the existing grade is not the same as the transmuted grade, continue searching
                if existing_grade != student['quarter'][quarter]:
                    continue
                else:
                    student_exists = True  # Data exists for current student
                    break  # No need to continue searching for this student

            if student_exists:
                break  # No need to continue searching if data exists for current student
        else:
            all_students_exist = False  # Data doesn't exist for at least one student

    if all_students_exist:
        return {'exists': True, 'message': 'Data already exists in AdvisoryClass'}
    else:
        return {'exists': False, 'message': 'No existing data found in AdvisoryClass'}


def save_data(message, json_data, teacher):
    quarter_field_mapping = {
        "1st Quarter": "first_quarter",
        "2nd Quarter": "second_quarter",
        "3rd Quarter": "third_quarter",
        "4th Quarter": "fourth_quarter"
    }

    # Fetch advisory classes once outside the loop
    advisory_classes = AdvisoryClass.objects.filter(
        grade=json_data.get('grade'),
        section=json_data.get('section')
    ).select_related('student')

    # Organize existing advisory classes by student name for quick access
    advisory_classes_by_student = defaultdict(list)
    for advisory_class in advisory_classes:
        advisory_classes_by_student[advisory_class.student.name].append(advisory_class)

    for student in json_data.get('students', []):
        student_name = student.get('name')
        student_instance, created = Student.objects.get_or_create(name=student_name)

        for quarter, transmuted_grade in student.get('quarter', {}).items():
            if transmuted_grade == '':
                transmuted_grade = None

            existing_advisory_classes = advisory_classes_by_student.get(student_name, [])

            for advisory_class in existing_advisory_classes:
                grades_data = advisory_class.grades_data
                subject_teacher_data = grades_data.get(json_data.get('subject'), {})  # Get existing or empty dictionary

                # Update the subject_teacher_data with the new grade and teacher info
                subject_teacher_data[quarter_field_mapping[quarter]] = transmuted_grade
                subject_teacher_data['from_teacher_id'] = json_data.get('teacher')
                subject_teacher_data['subject'] = json_data.get('subject')

                quarter_grades = [float(subject_teacher_data[q]) for q in quarter_field_mapping.values() 
                                  if q in subject_teacher_data and subject_teacher_data[q] and subject_teacher_data[q].strip()]
                
                # print(quarter_grades)
                final_grade = round(sum(quarter_grades) / len(quarter_grades)) if quarter_grades else None

                subject_teacher_data['final_grade'] = final_grade
                subject_teacher_data['status'] = determine_status(final_grade)    

                advisory_class.set_grade_for_subject(json_data.get('subject'), subject_teacher_data)
                advisory_class.save()   
                      

                if json_data.get('subject') in ['MUSIC', 'ARTS', 'PE', 'HEALTH']:
                    mapeh_quarter_data = grades_data.get('MAPEH', {})
                    mapeh_quarter_data[quarter_field_mapping[quarter]] = transmuted_grade
                    grades_data['MAPEH'] = mapeh_quarter_data

                    mapeh_quarter_grades = []
                    for subject in ['MUSIC', 'ARTS', 'PE', 'HEALTH']:
                        if subject in grades_data:
                            print("Subject:", subject)  # Debugging
                            for q in quarter_field_mapping.values():
                                if q in grades_data[subject] and q == quarter_field_mapping[quarter] and isinstance(grades_data[subject][q], str) and grades_data[subject][q] and grades_data[subject][q].strip():
                                    print("Quarter:", q)  # Debugging
                                    mapeh_quarter_grades.append(float(str(grades_data[subject][q]))) 
                                
                                    print(f"Quarter grades for {subject} subjects:", mapeh_quarter_grades)
                        mapeh_final_grade = round(sum(mapeh_quarter_grades) / len(mapeh_quarter_grades)) if mapeh_quarter_grades else None
                        print(f"Calculated {subject}:", mapeh_final_grade)
                                    # Update MAPEH's final grade
                        mapeh_quarter_grade = grades_data.get('MAPEH', {})
                        mapeh_quarter_grade[quarter_field_mapping[quarter]] = mapeh_final_grade
                        mapeh_quarter_data['from_teacher_id'] = json_data.get('teacher')
                        mapeh_quarter_data['subjects'] = "MAPEH"


                    mapeh_average = []
                        # Iterate through each quarter
                    for q in quarter_field_mapping.values():
                            # Check if the quarter exists in the MAPEH grades data and it's not empty
                            if 'MAPEH' in grades_data and q in grades_data['MAPEH'] and isinstance(grades_data['MAPEH'][q], (int, float)):
                                # Append the quarter grade to the list after converting it to float
                                mapeh_average.append(float(grades_data['MAPEH'][q]))

                        # Calculate the final grade for MAPEH
                    mapeh_final_grade = round(sum(mapeh_average) / len(mapeh_average)) if mapeh_average else None
                    print("mapeh final grade", mapeh_final_grade)
                    mapeh_quarter_grade['final_grade'] = mapeh_final_grade
                    mapeh_quarter_grade['status'] = determine_status(mapeh_final_grade)


                        # Calculate average final grade for all quarters

                        # mapeh_quarter_grade['final_grade'] = average_final_grade
                    grades_data['MAPEH'] = mapeh_quarter_grade


                    

                advisory_class.set_grade_for_subject(json_data.get('subject'), subject_teacher_data)
                advisory_class.save()
                # print(f"Updated AdvisoryClass with {json_data.get('subject')} {quarter} for {student_name}.")

            # If no existing advisory classes, create a new one
            if not existing_advisory_classes:
                new_advisory_class = AdvisoryClass(
                    grade=json_data.get('grade'),
                    section=json_data.get('section'),
                    teacher=teacher,
                    student=student_instance,
                )
                quarters = quarter_field_mapping[quarter]

                # Add from_teacher_id to the subject_teacher_data dictionary
                subject_teacher_data = {
                    "subject": json_data.get('subject'),
                    "from_teacher_id": json_data.get('teacher'),
                    quarters: transmuted_grade,
                    'final_grade': transmuted_grade,  # Assuming the final grade is initially set to the first quarter grade
                    'status': determine_status(transmuted_grade)
                }
                
                
                # if json_data.get('subject') in ['MUSIC', 'ARTS', 'PE', 'HEALTH']:
                #     mapeh_quarter_data = grades_data.get('MAPEH', {})  # Get existing data or create an empty dictionary
                #     mapeh_quarter_data[quarter_field_mapping[quarter]] = transmuted_grade
                #     mapeh_quarter_data['final_grade'] = transmuted_grade  # Update or add the transmuted grade for the current quarter
                #     mapeh_quarter_data['subject'] = "MAPEH"
                #     new_advisory_class.set_grade_for_subject("MAPEH", mapeh_quarter_data)
                #     print("GUMANA ATA?")
                

                new_advisory_class.set_grade_for_subject(json_data.get('subject'), subject_teacher_data)
                new_advisory_class.save()

         
                print(f"Saved new AdvisoryClass with {quarter} for {student_name}.")


def save_accepted_message(message):
    try:
        accepted_by_id=message.to_teacher
        teacher_instance = get_object_or_404(Teacher, pk=accepted_by_id)
        # Attempt to create the AcceptedMessage instance
        AcceptedMessage.objects.create(
            message_id=message.id,
            file_name=message.file_name,
            json_data=message.json_data,
            accepted_by=teacher_instance
        )
    except IntegrityError as e:
        # Handle duplicate primary key error
        print(f"Error: {e}")
        # Add additional error handling or logging here as needed

def determine_status(general_average):
    if general_average is None:
        return 'No Grade'
     
    if general_average and float(general_average) >= 98:
        return 'PASSED'
    elif general_average and float(general_average) >= 95:
        return 'PASSED'
    elif general_average and float(general_average) >= 90:
        return 'PASSED'
    elif general_average and float(general_average) >= 75:
        return 'PASSED'
    else:
        return 'FAILED'