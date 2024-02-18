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
def get_teacher_list(request):
    if request.method == 'GET':
        teachers = Teacher.objects.all()
        teacher_list = [{'id': teacher.id, 'name': f"{teacher.user.first_name} {teacher.user.last_name}"} for teacher in teachers]
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
            print(json_data)
            print(file_name)
            print(from_teacher_id)
            # Check if the section with the specified name, class_type, and teacher_id exists
            existing_section = Section.objects.filter(name=section, class_type="Advisory", teacher_id=target_teacher_id).exists()
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
            print(teacher)
            # Get inbox messages where the logged-in teacher is the intended recipient
            inbox_messages = InboxMessage.objects.filter(to_teacher=teacher)

            return render(request, 'teacher_template/adviserTeacher/inbox.html', {'inbox_messages': inbox_messages})

        else:
            # Handle the case where the logged-in user is not a teacher
            return render(request, 'teacher_template/adviserTeacher/inbox.html', {'inbox_messages': []})

    except Exception as e:
        # Handle any exceptions
        print(f"Error in inbox_open: {e}")
        return render(request, 'teacher_template/adviserTeacher/inbox.html', {'inbox_messages': []})




@login_required
def inbox(request):
    teacher_username = request.user.username  # Assuming the username is used for filtering
    teacher = get_user_model().objects.get(username=teacher_username)
    
    messages = InboxMessage.objects.filter(teacher=teacher).order_by('-timestamp')

    return render(request, 'teacher_template/adviserTeacher/inbox.html', {'messages': messages})



def transfer_quarterly_grade(request, grade, section, subject, class_record_id):
    teacher = request.user.teacher
    # Filter Section objects based on provided parameters
    sections = Section.objects.filter(name=section, teacher_id=teacher, class_type='Subject')

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
def accept_message(request):
    message_id = request.POST.get('message_id')
    try:
        message = InboxMessage.objects.get(pk=message_id)
        json_data = json.loads(message.json_data)
        
        if check_existing_data(message, json_data): 
            message.delete()
            return JsonResponse({'success': True, 'message': 'Data already exists in AdvisoryClass'})
        else:
            save_data(message, json_data)  # Call save_data only once
            save_accepted_message(message)  # Call save_accepted_message to save the accepted message
            message.delete()
            return JsonResponse({'success': True, 'message': 'Message accepted and saved to AdvisoryClass model.'})
    except InboxMessage.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Message not found'})



def check_existing_data(message, json_data):
    quarter_field_mapping = {
        "1st Quarter": "first_quarter",
        "2nd Quarter": "second_quarter",
        "3rd Quarter": "third_quarter",
        "4th Quarter": "fourth_quarter"
    }
    
    excluded_quarters = ["first_quarter", "second_quarter", "third_quarter", "fourth_quarter"]
    
    for student in json_data.get('students', []):
        student_name = student.get('name')
        for quarter in student.get('quarter', {}):
            field_name = quarter_field_mapping.get(quarter)
            if not field_name:
                continue
            
            if field_name in excluded_quarters:
                continue
            
            existing_advisory_classes = AdvisoryClass.objects.filter(
                grade=json_data.get('grade'),
                section=json_data.get('section'),
                subject=json_data.get('subject'),
                from_teacher_id=message.from_teacher,
                student__name=student_name,
            )
            
            for existing_advisory_class in existing_advisory_classes:
                existing_grade = getattr(existing_advisory_class, field_name)
                if existing_grade is None:
                    return False  # No existing value found, so we can save the data
                
                # If the existing grade is not the same as the transmuted grade, continue searching
                if existing_grade != student['quarter'][quarter]:
                    continue
                else:
                    return True  # Found existing value matching the transmuted grade
            
    return False  # No existing value found, so we can save the data

def save_data(message, json_data):
    quarter_field_mapping = {
        "1st Quarter": "first_quarter",
        "2nd Quarter": "second_quarter",
        "3rd Quarter": "third_quarter",
        "4th Quarter": "fourth_quarter"
    }

    replacements_made = set()  # Keep track of replacements made

    for student in json_data.get('students', []):
        student_name = student.get('name', None)
        student_instance, created = Student.objects.get_or_create(name=student_name, class_type='advisory')

        for quarter, transmuted_grade in student.get('quarter', {}).items():
            if transmuted_grade == '':
                transmuted_grade = None

            key = (student_name, quarter)  # Create a unique key for each student-quarter combination

            if key in replacements_made:
                continue  # Skip if a replacement has already been made for this combination

            existing_advisory_classes = AdvisoryClass.objects.filter(
                grade=json_data.get('grade'),
                section=json_data.get('section'),
                subject=json_data.get('subject'),
                from_teacher_id=json_data.get('teacher'),
                student=student_instance,
            )

            if existing_advisory_classes.exists():
                parent_advisory_class = existing_advisory_classes.first()
                field_to_update = quarter_field_mapping.get(quarter)
                existing_grade = getattr(parent_advisory_class, field_to_update)
                if existing_grade != transmuted_grade:
                    print(f"Replacing {quarter} value for {student_name}. Existing value: {existing_grade}. New value: {transmuted_grade}.")
                    setattr(parent_advisory_class, field_to_update, transmuted_grade)
                    parent_advisory_class.save()
                    replacements_made.add(key)  # Add the combination to replacements_made
                else:
                    print(f"{quarter} already has the same value for {student_name}.")
            else:
                new_advisory_class = AdvisoryClass(
                    grade=json_data.get('grade'),
                    section=json_data.get('section'),
                    subject=json_data.get('subject'),
                    from_teacher_id=json_data.get('teacher'),
                    student=student_instance,
                )
                setattr(new_advisory_class, quarter_field_mapping.get(quarter), transmuted_grade)
                new_advisory_class.save()
                print(f"Saved new AdvisoryClass with {quarter} for {student_name}.")



def save_accepted_message(message):
    # Save the accepted message information
    AcceptedMessage.objects.create(
        message_id=message.id,
        file_name=message.file_name,
        json_data=message.json_data
    )