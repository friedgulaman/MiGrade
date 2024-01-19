from django.db import IntegrityError
from django.contrib import messages
from django.shortcuts import redirect, render
from .models import CustomUser, Student, Teacher, Grade, Section
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


from django.contrib.auth.decorators import login_required


@login_required
def home_admin(request):
    # Retrieve the grades queryset
    grades = Grade.objects.all()
    teachers = Teacher.objects.all()

    # Retrieve all sections for each grade
    sections = Section.objects.all()

    # Include the grades and sections in the context
    context = {
        'grades': grades,
        'sections': sections,
        'teachers': teachers,
    }
    return render(request, 'admin_template/home_admin.html', context)

def add_teacher(request):
    return render(request, 'admin_template/add_teacher.html')

def add_teacher_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method ")
        return redirect('add_teacher')
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
                profile_image=''
            )

            # No need to create a Teacher object here
            # The Teacher object will be associated with the CustomUser automatically

            messages.success(request, "Teacher Added Successfully!")
            return redirect('add_teacher')
        except IntegrityError:
            messages.error(request, "Failed to Add Teacher!")
            return redirect('add_teacher')
        

def teacherList(request):
    grades = Grade.objects.all()
    teachers = Teacher.objects.all()
    sections = Section.objects.all()

    # Include the grades and sections in the context
    context = {
        'grades': grades,
        'sections': sections,
        'teachers': teachers,
    }
    return render(request, 'admin_template/list_of_teacher.html', context)



def submit_grade_section(request):
    if request.method == 'POST':
        # Lists to store created grades and sections
        created_grades = []
        created_sections = []

        # Iterate over the form data
        for key, value in request.POST.items():
            if key.startswith('grade_'):
                grade_name = value
                section_key = f'section_{key.split("_")[1]}[]'
                sections = request.POST.getlist(section_key)

                # Check if the grade already exists in the database
                grade, grade_created = Grade.objects.get_or_create(name=grade_name)

                # Create or update sections associated with the grade
                for section_name in sections:
                    section, section_created = Section.objects.get_or_create(name=section_name, grade=grade)
                    created_sections.append(section.name)

                # Append the created or retrieved grade name to the list
                if grade_created:
                    created_grades.append(grade.name)

        # Add a success message
        messages.success(request, 'Form data submitted successfully.')

    # Retrieve the grades queryset
    grades = Grade.objects.all()

    # Retrieve all sections for each grade
    sections = Section.objects.all()

    # Include the grades and sections in the context
    context = {
        'grades': grades,
        'sections': sections,
    }
    
    return render(request, 'admin_template/add_grade_section.html', context)

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

            # Handle birthdate separately
            if 'Birthdate' in key_mapping:
                birthdate_index = data_by_type['Type'].index('Birthdate') if 'Birthdate' in data_by_type['Type'] else None
                if birthdate_index is not None:
                    birthdate_str = data_by_type['Raw Value'][birthdate_index]
                    try:
                        my_data.birthdate = datetime.strptime(birthdate_str, "%m/%d/%Y").date()
                    except ValueError as e:
                        print(f"Error parsing birthdate: {e}")

            my_data.save()
          

        return render(request, 'admin_template/edit_extracted_data.html', {
                # 'extracted_data': extracted_data_for_review,
                'document_text': text,
                'uploaded_document_url': processed_document.document.url,
                # 'all_extracted_data': all_extracted_data,
                'processed_document': processed_document,
                'download_link': processed_document.document.url,
                'data_by_type': data_by_type,
                # 'extracted_text': extracted_text 
                'extracted_data': my_data
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
    # Query the ExtractedData model to retrieve all records
    all_extracted_data = ExtractedData.objects.all()

    # Pass the extracted data to the template context
    context = {
        'all_extracted_data': all_extracted_data,
    }

    # Render the sf10.html template with the context data
    return render(request, 'admin_template/sf10.html', context)


def add_subject(request):
    if request.method == 'POST':
        form = SubjectForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('subject_list')  # Redirect to a page showing the list of subjects

    else:
        form = SubjectForm()

    return render(request, 'admin_template/add_subject.html', {'form': form})

def subject_list(request):
    subjects = Subject.objects.all()
    return render(request, 'admin_template/subject_list.html', {'subjects': subjects})

