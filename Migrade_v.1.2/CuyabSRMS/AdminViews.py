from django.db import IntegrityError
from django.contrib import messages
from django.shortcuts import redirect, render, get_object_or_404
from .models import CustomUser, Quarters, Student, Teacher, Grade, Section
from django.contrib.auth import get_user_model  # Add this import statement
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.http import JsonResponse
from django.db import models
from django.views.decorators.http import require_GET
from django.db.models import Q
from .forms import SubjectForm
from .models import Subject

#OCR
from .models import ExtractedData
from .models import ProcessedDocument
from google.cloud import documentai_v1beta3 as documentai
import re
import os
import json
from .forms import DocumentUploadForm
from django.conf import settings
from django.shortcuts import HttpResponse
from django.utils.text import get_valid_filename
from .forms import ExtractedDataForm

import openpyxl
from django.utils import timezone
import datetime
from datetime import datetime
from dateutil import parser



from django.contrib.auth.decorators import login_required
from django.http import FileResponse
import base64

from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User

@login_required
def home_admin(request):
    # Retrieve the grades queryset
    grades = Grade.objects.all()
    teachers = Teacher.objects.all()
    sections = Section.objects.all()
    total_teachers = Teacher.objects.count()
    total_students = Student.objects.count()
    total_grades = Grade.objects.count()
    total_sections = Section.objects.count()
    total_subjects = Subject.objects.count()
   
    context = {
        'grades': grades,
        'sections': sections,
        'teachers': teachers,
        'total_teachers': total_teachers,
        'total_students': total_students,
        'total_grades': total_grades,
        'total_sections': total_sections,
        'total_subjects': total_subjects,
    }
    return render(request, 'admin_template/home_admin.html', context)

def add_teacher(request):
    return render(request, 'admin_template/add_teacher.html')

def grade_and_section(request):
    grades = Grade.objects.all()
    sections = Section.objects.all()
    total_student = Section.objects.aggregate(total_students=models.Sum('total_students'))

    context = {
        'grades': grades,
        'sections': sections,
        'total_student': total_student['total_students'] if total_student else 0,
    }

    return render(request, 'admin_template/manage_grade_and_section.html', context)

def teachers(request):
    grades = Grade.objects.all()
    teachers = Teacher.objects.all()
    sections = Section.objects.all()
    students = Student.objects.all()

    # Include the grades and sections in the context
    context = {
        'grades': grades,
        'sections': sections,
        'teachers': teachers,
        'students': students,
    }
    return render(request, 'admin_template/manage_teacher.html', context)

@require_GET
def get_teacher_data(request):
    teacher_id = request.GET.get('teacherId')
    teacher = get_object_or_404(Teacher, id=teacher_id)
    data = {
        'id': teacher.id,
        'first_name': teacher.user.first_name,
        'last_name': teacher.user.last_name,
    }
    return JsonResponse(data)

def students(request):
    # Get distinct combinations of grade and section
    unique_combinations = Student.objects.values('grade', 'section').distinct()

    # Prepare a list to store dictionaries with grade, section, and total_students
    data = []

    # Calculate total_students for each grade and section combination
    for combination in unique_combinations:
        grade = combination['grade']
        section = combination['section']
        total_students = Student.objects.filter(grade=grade, section=section).count()

        # Append data to the list
        data.append({
            'grade': grade,
            'section': section,
            'total_students': total_students,
        })

    # Prepare context to pass to the template
    context = {
        'unique_grades_sections': data,
    }

    # Render the template with the context
    return render(request, 'admin_template/students.html', context)

def get_student_details(request):
    student_id = request.GET.get('studentId')
    student = get_object_or_404(Student, id=student_id)
    data = {
        'name': student.name,
    }
    return JsonResponse(data)

@require_POST
def update_student_details(request):
    student_id = request.POST.get('student_id')
    student_name = request.POST.get('student_name')
    # Add other form fields here as needed

    # Retrieve the student from the database
    student = get_object_or_404(Student, id=student_id)

    # Update the student details
    student.name = student_name
    # Update other fields as needed
    student.save()

    # Return a success response
    return JsonResponse({'message': 'Student details updated successfully'})

@require_POST
def delete_student(request):
    student_id = request.POST.get('student_id')
    student = get_object_or_404(Student, id=student_id)
    student.delete()

    return JsonResponse({'message': 'Student deleted successfully'})

def student_lists(request):
    grade = request.GET.get('grade')
    section = request.GET.get('section')

    # Fetch students based on grade and section
    students = Student.objects.filter(grade=grade, section=section)

    context = {
        'grade': grade,
        'section': section,
        'students': students,

    }
    return render(request, 'admin_template/manage_students.html', context)

def student_lists_grade_section(request):
    grade = request.GET.get('grade')
    section = request.GET.get('section')

    # Fetch students based on grade and section
    students = Student.objects.filter(grade=grade, section=section)

    context = {
        'grade': grade,
        'section': section,
        'students': students,

    }
    return render(request, 'admin_template/manage_students.html', context)
def add_student(request):
    if request.method == 'POST':
        # Retrieve form data
        name = request.POST.get('name')
        lrn = request.POST.get('lrn')
        sex = request.POST.get('sex')
        birthday = request.POST.get('birthday')


        # Get default values based on grade and section
        grade = request.POST.get('grade')
        section = request.POST.get('section')
        default_values = Student.objects.filter(grade=grade, section=section).first()

        # Create a new student with default values
        new_student = Student(
            grade=grade,
            section=section,
            name=name,
            lrn=lrn,
            sex=sex,
            birthday=birthday,
            teacher_id=default_values.teacher_id if default_values else None,
            school_id=default_values.school_id if default_values else None,
            school_name=default_values.school_name if default_values else None,
            school_year=default_values.school_year if default_values else None,
            division=default_values.division if default_values else None,
            district=default_values.district if default_values else None,
            # Add other fields as needed
        )
        new_student.save()

        redirect_url = reverse('student_lists', kwargs={'grade': grade, 'section': section})

    # Fetch default values for the form
    grade = request.GET.get('grade')
    section = request.GET.get('section')
    default_values = Student.objects.filter(grade=grade, section=section).first()

    context = {
        'default_values': default_values,
    }
    return render(request, 'admin_template/manage_students.html', context)


def subjects(request):
    subjects = Subject.objects.all()

    context = {
        'subjects': subjects,
    }
    return render(request, 'admin_template/manage_subjects.html', context)

def get_subject_data(request):
    subject_id = request.GET.get('subjectId')
    subject = get_object_or_404(Subject, id=subject_id)

    # Return subject data as JSON
    data = {
        'id': subject.id,
        'name': subject.name,
        'written_works_percentage': subject.written_works_percentage,
        'performance_task_percentage': subject.performance_task_percentage,
        'quarterly_assessment_percentage': subject.quarterly_assessment_percentage,
    }

    return JsonResponse(data)
def add_subject(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        written_works_percentage = request.POST.get('written_works_percentage')
        performance_task_percentage = request.POST.get('performance_task_percentage')
        quarterly_assessment_percentage = request.POST.get('quarterly_assessment_percentage')

        if name and written_works_percentage is not None and performance_task_percentage is not None and quarterly_assessment_percentage is not None:
            subject = Subject.objects.create(
                name=name,
                written_works_percentage=written_works_percentage,
                performance_task_percentage=performance_task_percentage,
                quarterly_assessment_percentage=quarterly_assessment_percentage
            )
            return JsonResponse({'success': True, 'subject_id': subject.id})

    return JsonResponse({'success': False, 'error_message': 'Invalid form data'})


def subject_list(request):
    subjects = Subject.objects.all()
    return render(request, 'admin_template/subject_list.html', {'subjects': subjects})

def update_subject(request):
    if request.method == 'POST':
        subject_id = request.POST.get('subjectId')
        subject_name = request.POST.get('subjectName')
        written_works_percentage = request.POST.get('writtenWorksPercentage')
        performance_task_percentage = request.POST.get('performanceTaskPercentage')
        quarterly_assessment_percentage = request.POST.get('quarterlyAssessmentPercentage')

        subject = get_object_or_404(Subject, id=subject_id)
        subject.name = subject_name
        subject.written_works_percentage = written_works_percentage
        subject.performance_task_percentage = performance_task_percentage
        subject.quarterly_assessment_percentage = quarterly_assessment_percentage
        subject.save()

        # Return a success response
        return JsonResponse({'success': True, 'message': 'Subject updated successfully'})

    # Return a failure response if not a POST request
    return JsonResponse({'success': False, 'message': 'Invalid request'})
@csrf_exempt
@login_required
def delete_subject(request):
    if request.method == 'POST':
        subject_id = request.POST.get('subjectId')

        subject = get_object_or_404(Subject, id=subject_id)
        subject.delete()

        # Return a success response
        return JsonResponse({'success': True, 'message': 'Subject deleted successfully'})

    # Return a failure response if not a POST request
    return JsonResponse({'success': False, 'message': 'Invalid request'})

def quarters(request):
    quarters = Quarters.objects.all()
    return render(request, 'admin_template/manage_quarters.html', {'quarters': quarters})

def add_quarter(request):
    if request.method == 'POST':
        quarters = request.POST.get('quarters')

        if quarters:
            quarter = Quarters.objects.create(
                quarters=quarters
            )
            return JsonResponse({'success': True, 'quarter_id': quarter.id})

    return JsonResponse({'success': False, 'error_message': 'Invalid form data'})
def get_quarters_data(request):
    quarter_id = request.GET.get('quarterId')
    quarter = get_object_or_404(Quarters, id=quarter_id)

    # Return quarter data as JSON
    data = {
        'id': quarter.id,
        'quarters': quarter.quarters,
    }

    return JsonResponse(data)

@csrf_exempt
@login_required
def add_quarter(request):
    if request.method == 'POST':
        quarters = request.POST.get('quarters')

        if quarters:
            quarter = Quarters.objects.create(quarters=quarters)
            return JsonResponse({'success': True, 'quarter_id': quarter.id})

    return JsonResponse({'success': False, 'error_message': 'Invalid form data'})

def update_quarter(request):
    if request.method == 'POST':
        quarter_id = request.POST.get('quarterId')
        quarters = request.POST.get('quarters')

        quarter = get_object_or_404(Quarters, id=quarter_id)
        quarter.quarters = quarters
        quarter.save()

        # Return a success response
        return JsonResponse({'success': True, 'message': 'Quarter updated successfully'})

    # Return a failure response if not a POST request
    return JsonResponse({'success': False, 'message': 'Invalid request'})

@csrf_exempt
@login_required
def delete_quarter(request):
    if request.method == 'POST':
        quarter_id = request.POST.get('quarterId')

        quarter = get_object_or_404(Quarters, id=quarter_id)
        quarter.delete()

        # Return a success response
        return JsonResponse({'success': True, 'message': 'Quarter deleted successfully'})

    # Return a failure response if not a POST request
    return JsonResponse({'success': False, 'message': 'Invalid request'})
@require_POST
def update_teacher(request):
    teacher_id = request.POST.get('teacherId')
    first_name = request.POST.get('firstName')
    last_name = request.POST.get('lastName')

    teacher = get_object_or_404(Teacher, id=teacher_id)
    teacher.user.first_name = first_name
    teacher.user.last_name = last_name
    teacher.user.save()

    return JsonResponse({'message': 'Teacher updated successfully'})
@csrf_exempt
@login_required
def delete_teacher(request):
    if request.method == 'POST':
        teacher_id = request.POST.get('teacherId')

        # Check if the teacher exists
        teacher = get_object_or_404(Teacher, id=teacher_id)

        try:
            # Perform the teacher deletion
            user_id = teacher.user.id  # Get the associated user ID
            teacher.delete()

            # Delete the associated CustomUser
            user = get_object_or_404(get_user_model(), id=user_id)
            user.delete()

            response_data = {'message': 'Teacher and associated user deleted successfully'}
            return JsonResponse(response_data)
        except Exception as e:
            response_data = {'message': f'Error deleting teacher and user: {str(e)}'}
            return JsonResponse(response_data, status=500)

def add_teacher_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method ")
        return redirect('teachers')
    else:
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        middle_ini = request.POST.get('middle_ini')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password', 'default_pass')

        try:
            # Create a CustomUser
            user = CustomUser.objects.create_user(
                username=username,
                password=password,
                email=email,
                first_name=first_name,
                last_name=last_name,
                middle_ini=middle_ini,
                user_type=2,  # This represents a teacher user
            )

            return JsonResponse({'success': True, 'message': 'Teacher Added Successfully!'})
        except IntegrityError:
            messages.error(request, "Failed to Add Teacher!")

            # Return a JSON response for error
            return JsonResponse({'success': False, 'message': 'Failed to Add Teacher!'})
        




@require_GET
def get_sections(request):
    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        grade_id = request.GET.get('grade_id')
        sections = Section.objects.filter(grade_id=grade_id)
        section_list = [{'id': section.id, 'name': section.name} for section in sections]
        
        # Check if there are sections to return
        if section_list:
            return JsonResponse({'sections': section_list})
        else:
            return JsonResponse({'message': 'No sections available for the selected grade'})
    else:
        # Handle non-AJAX requests if needed
        return JsonResponse({'message': 'Invalid request'})
    


def assign_teacher(request):
    # Retrieve the grades, teachers, and sections queryset
    grades = Grade.objects.all()
    teachers = Teacher.objects.all()
    sections = Section.objects.all()

    # Include the grades, sections, and teachers in the context
    context = {
        'grades': grades,
        'sections': sections,
        'teachers': teachers,
    }
    return render(request, 'admin_template/assign_teacher.html', context)

def save_assignment(request):
    if request.method == 'POST':
        # Retrieve the data from the form
        teacher_id = request.POST.get('teacher')
        grade_id = request.POST.get('grade')
        section_id = request.POST.get('section')

        # Validate the data
        if teacher_id and grade_id and section_id:
            try:
                section = Section.objects.get(id=section_id)
                teacher = Teacher.objects.get(id=teacher_id)
                # Assign the teacher to the section
                section.teacher = teacher
                section.save()
                # Store a success message
                messages.success(request, 'Assignment saved successfully')
                return JsonResponse({'success': True})
            except (Section.DoesNotExist, Teacher.DoesNotExist):
                messages.error(request, 'Invalid teacher or section')
        else:
            # Handle the case where data is missing
            messages.error(request, 'Invalid data')
    else:
        # Handle other request methods if needed
        messages.error(request, 'Invalid request method')

    return JsonResponse({'success': False})


def add_grade_section(request):
    grades = Grade.objects.all()
    sections = Section.objects.all()

    # Include the grades and sections in the context
    context = {
        'grades': grades,
        'sections': sections,
    }
    return render(request, 'admin_template/add_grade_section.html', context)


def search_students(request):
    if request.method == 'GET':
        search_query = request.GET.get('q', '')

        students = Student.objects.filter(
            Q(name__icontains=search_query) |
            Q(lrn__icontains=search_query) |
            Q(sex__icontains=search_query) |
            Q(birthday__icontains=search_query) |
            Q(teacher__id__icontains=search_query) |
            Q(grade__icontains=search_query) |
            Q(section__icontains=search_query)
        )

        context = {
            'students': students,
            'search_query': search_query,
        }

        return render(request, 'admin_template/home_admin.html', context)

#sf10 views

# def extract_and_edit_data(request):
#     if request.method == 'POST':
#         # Extract data from the form submission
#         extracted_data = request.POST.get('extracted_data')
        
#         # Parse the extracted data (assuming it is in JSON format)
#         extracted_data_dict = json.loads(extracted_data)
        
#         # Render the editable form with the extracted data
#         return render(request, 'teacher_template/adviserTeacher/edit_extracted_data.html', {'extracted_data': extracted_data_dict})

#     else:
#         # Handle GET request, redirect user to the upload document page
#         return render(request, 'teacher_template/adviserTeacher/upload_document.html', {'form': DocumentUploadForm()})
# def edit_extracted_data(request):
#     if request.method == 'POST':
#         # Assuming extracted_data is sent as POST data, retrieve it
#         extracted_data = {
#              'last_name': request.POST.get('Last_Name', ''),
#             'first_name': request.POST.get('First_Name', ''),
#             'middle_name': request.POST.get('Middle_Name', ''),
#             'sex': request.POST.get('SEX', ''),
#             'classified_as_grade': request.POST.get('Classified_as_Grade', ''),
#             'lrn': request.POST.get('LRN', ''),
#             'name_of_school': request.POST.get('Name_of_School', ''),
#             'school_year': request.POST.get('School_Year', ''),
#             'general_average': request.POST.get('General_Average', ''),
#             'birthdate': request.POST.get('Birthdate', ''),
#         }

#         print("Extracted Data:", extracted_data)
#         # Render the edit page with the extracted data for verification
#         return render(request, 'admin_template/edit_extracted_data.html', {'extracted_data': extracted_data})
#     else:
#         # Handle GET request if necessary
#         return HttpResponse("Invalid request method")

def upload_documents_ocr(request):
    if request.method == 'POST':
        form = DocumentUploadForm(request.POST, request.FILES)
        if form.is_valid():
            # Replace 'YOUR_PROJECT_ID' with your Google Cloud project ID.
            project_id = '1083879771832'


            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"ces-ocr-5a2441a9fd54.json"

            client = documentai.DocumentProcessorServiceClient()

            # Define the processor resource name.
            processor_name = f"projects/{project_id}/locations/us/processors/84dec1544028cc60"

            uploaded_file = request.FILES['document']

            # Read the document content from the uploaded file.
            content = uploaded_file.read()

            # Determine the MIME type based on the file extension.
            file_extension = os.path.splitext(uploaded_file.name)[-1].lower()
            if file_extension in ['.pdf']:
                mime_type = "application/pdf"
            elif file_extension in ['.jpg', '.jpeg']:
                mime_type = "image/jpeg"
            else:
                # Handle unsupported file types or provide an error message.
                return render(request, 'unsupported_file_type.html')

            # Configure the processing request.
            processing_request = {
                "name": processor_name,
                "document": {"content": content, "mime_type": mime_type},
            }

            # Process the document.
            response = client.process_document(request=processing_request)

            # Access the extracted text from the document content.
            document = response.document
            text = document.text

            data_by_type = {
                'Type': [],
                'Raw Value': [],
                'Normalized Value': [],
                'Confidence': [],
            }

            # Iterate through your data extraction process and populate the dictionary
            for entity in document.entities:
                data_by_type['Type'].append(entity.type_)
                data_by_type['Raw Value'].append(entity.mention_text)
                data_by_type['Normalized Value'].append(entity.normalized_value.text)
                data_by_type['Confidence'].append(f"{entity.confidence:.0%}")

                # Get Properties (Sub-Entities) with confidence scores
                for prop in entity.properties:
                    data_by_type['Type'].append(prop.type_)
                    data_by_type['Raw Value'].append(prop.mention_text)
                    data_by_type['Normalized Value'].append(prop.normalized_value.text)
                    data_by_type['Confidence'].append(f"{prop.confidence:.0%}")

            print(data_by_type)
            # Create a ProcessedDocument instance and save it
            processed_document = ProcessedDocument(document=uploaded_file, upload_date=timezone.now())
            processed_document.save()

            my_data = ExtractedData(processed_document=processed_document)

            # Define a mapping of keys from data_by_type to ExtractedData fields
            key_mapping = {
                'Last_Name': 'last_name',
                'First_Name': 'first_name',
                'Middle_Name': 'middle_name',
                'SEX': 'sex',
                'Classified_as_Grade': 'classified_as_grade',
                'LRN': 'lrn',
                'Name_of_School': 'name_of_school',
                'School_Year': 'school_year',
                'General_Average': 'general_average',
                'Birthdate': 'birthdate',
            }

            last_values = {}

            for i in range(len(data_by_type['Type'])):
                data_type = data_by_type['Type'][i]
                raw_value = data_by_type['Raw Value'][i]

                # Update the last value for the type
                last_values[data_type] = {'value': raw_value}

            # Set the last values to the corresponding fields in my_data
            for key, field_name in key_mapping.items():
                if key in last_values:
                    setattr(my_data, field_name, last_values[key]['value'])

            # # Handle birthdate separately
            #     if 'Birthdate' in key_mapping:
            #         birthdate_index = data_by_type['Type'].index('Birthdate') if 'Birthdate' in data_by_type['Type'] else None
            #         if birthdate_index is not None:
            #             birthdate_str = data_by_type['Raw Value'][birthdate_index]
            #             try:
            #                 # Provide a specific format string based on the expected format
            #                 my_data.birthdate = parser.parse(birthdate_str).date()
            #             except ValueError as e:
            #                 print(f"Error parsing birthdate: {e}")
            if 'Birthdate' in key_mapping:
                birthdate_index = data_by_type['Type'].index('Birthdate') if 'Birthdate' in data_by_type['Type'] else None
                if birthdate_index is not None:
                    birthdate_str = data_by_type['Raw Value'][birthdate_index]
                    try:
                        # Provide a specific format string based on the expected format
                        my_data.birthdate = parser.parse(birthdate_str).date()
                    except ValueError as e:
                        print(f"Error parsing birthdate: {e}")

            my_data.save()

            # response = FileResponse(open(processed_document.document.path, 'rb'), content_type='application/pdf')
            # response['Content-Disposition'] = f'inline; filename="{uploaded_file.name}"'
            # return response

            pdf_content_base64 = base64.b64encode(content).decode('utf-8')

        
        return render(request, 'admin_template/edit_extracted_data.html', {
                # 'extracted_data': extracted_data_for_review,
                'document_text': text,
                'uploaded_document_url': processed_document.document.url,
                # 'all_extracted_data': all_extracted_data,
                'processed_document': processed_document,
                'download_link': processed_document.document.url,
                'data_by_type': data_by_type,
                # 'extracted_text': extracted_text 
                'extracted_data': my_data,
                'pdf_content_base64': pdf_content_base64, 
            })
    else: 
        form = DocumentUploadForm()

    return render(request, 'admin_template/upload_documents.html', {'form': form})




def save_edited_data(request):  
    if request.method == 'POST':
        # Assuming extracted_data is sent as POST data, retrieve it
        extracted_data = {
            'last_name': request.POST.get('Last_Name', ''),
            'first_name': request.POST.get('First_Name', ''),
            'middle_name': request.POST.get('Middle_Name', ''),
            'sex': request.POST.get('SEX', ''),
            'classified_as_grade': request.POST.get('Classified_as_Grade', ''),
            'lrn': request.POST.get('LRN', ''),
            'name_of_school': request.POST.get('Name_of_School', ''),
            'school_year': request.POST.get('School_Year', ''),
            'general_average': request.POST.get('General_Average', ''),
            'birthdate': request.POST.get('Birthdate', ''),
        }

        # Retrieve the existing ProcessedDocument instance based on some criteria
        # For example, assuming you have a unique identifier like an ID:
        processed_document_id = request.POST.get('processed_document_id')
        print(f"Processed Document ID: {processed_document_id}")
        processed_document = ProcessedDocument.objects.get(pk=processed_document_id)

        # Retrieve the existing ExtractedData instance based on the associated ProcessedDocument
        try:
            extracted_data_instance = ExtractedData.objects.get(processed_document=processed_document)
        except ExtractedData.DoesNotExist:
            # Handle the case where the ExtractedData instance does not exist
            return HttpResponse("ExtractedData instance not found.")

        # Update the fields of the existing ExtractedData instance
        extracted_data_instance.last_name = extracted_data['last_name']
        extracted_data_instance.first_name = extracted_data['first_name']
        extracted_data_instance.middle_name = extracted_data['middle_name']
        extracted_data_instance.sex = extracted_data['sex']
        extracted_data_instance.classified_as_grade = extracted_data['classified_as_grade']
        extracted_data_instance.lrn = extracted_data['lrn']
        extracted_data_instance.name_of_school = extracted_data['name_of_school']
        extracted_data_instance.school_year = extracted_data['school_year']
        extracted_data_instance.general_average = extracted_data['general_average']

        birthdate_str = request.POST.get('Birthdate', '')

        # Convert the birthdate string to the "YYYY-MM-DD" format
        try:
            birthdate_obj = datetime.strptime(birthdate_str, "%b. %d, %Y")
            formatted_birthdate = birthdate_obj.strftime("%Y-%m-%d")
        except ValueError:
            # Handle the case where the date string is not in the expecsted format
            return HttpResponse("Invalid birthdate format.")

        # Update the birthdate field of the existing ExtractedData instance
        extracted_data_instance.birthdate = formatted_birthdate

        # ... update other fields

        # Save the changes
        extracted_data_instance.save()

        return redirect('sf10_view')

    else:
        # Handle GET request if necessary
        return HttpResponse("Invalid request method")

def sf10_views(request):
    # Retrieve the search query from the request's GET parameters
    search_query = request.GET.get('search', '')

    # If a search query is present, filter the ExtractedData model
    if search_query:
        # You can customize the fields you want to search on
        search_fields = ['last_name', 'first_name', 'middle_name', 'lrn', 'name_of_school', 'sex', 'birthdate', 'school_year', 'classified_as_grade', 'general_average']
        
        # Use Q objects to create a complex OR query
        query = Q()
        for field in search_fields:
            query |= Q(**{f'{field}__icontains': search_query})

        # Filter the ExtractedData model based on the search query
        all_extracted_data = ExtractedData.objects.filter(query)
    else:
        # If no search query, retrieve all records
        all_extracted_data = ExtractedData.objects.all()

    # Pass the filtered data and search query to the template context
    context = {
        'all_extracted_data': all_extracted_data,
        'search_query': search_query,
    }

    # Render the sf10.html template with the context data
    return render(request, 'admin_template/sf10.html', context)

