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
        password = request.POST.get('password')

        try:
            # Create a CustomUser
            user = CustomUser.objects.create_user(
                username=username,
                password=password,
                email=email,
                first_name=first_name,
                last_name=last_name,
                middle_ini=middle_ini,
                user_type=2  # This represents a teacher user
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

def upload_documents_ocr(request):
    if request.method == 'POST':
        form = DocumentUploadForm(request.POST, request.FILES)
        if form.is_valid():
            # Replace 'YOUR_PROJECT_ID' with your Google Cloud project ID.
            project_id = '359239664082'


            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"doc-ai-ocr-b135d04e24a7.json"

            client = documentai.DocumentProcessorServiceClient()

            # Define the processor resource name.
            processor_name = f"projects/{project_id}/locations/us/processors/6ff59e15c7cbbbc3"

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

            multi_value_fields = {}

            for key, field_name in key_mapping.items():
                indices = [i for i, item in enumerate(data_by_type['Type']) if item == key]
                if indices:
                    values = [data_by_type['Raw Value'][index] for index in indices]
                    combined_value = ", ".join(values)
                    setattr(my_data, field_name, combined_value)

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
                    # Extract specific data using regular expressions
        #     key_phrases = {
        #         "LAST NAME": r"(?i)LAST\s*NAME:\s*([^\n]+)(?:\s*NAME\s*EXTN\s*\([^)]*\))?",
        #         "FIRST NAME": r"(?i)FIRST\s*NAME:\s*([^\n]+)(?:\s*NAME\s*EXTN\s*\([^)]*\))?",
        #         "MIDDLE NAME": r"(?i)MIDDLE\s*NAME:\s*([^\n]+)",
        #         "LRN": r"Learner\s*Reference\s*Number\s*\(LRN\):\s*(\d+)",
        #         "SCHOOL YEAR": r"School\s*Year:\s*(\b\d{4}-\d{4}\b)",
        #         "BIRTHDATE": r"Birthdate\s*\(mm/dd/yyyy\):\s*([\d/]+)",
        #         "Classified as Grade:": r"(?i)Classified\s*as\s*Grade:?\s*(\d+|(?:one|two|three|four|five|six|seven|eight|nine)|[IVXLCDM]+)",
        #         "GENERAL AVERAGE": r"General Average\s+(.\d+)",
        #         "SEX": r"Sex:?\s*([A-Z]+)"

        #     }     
            
        #     key_value_pairs = {}

        #     # Iterate through the key phrases and extract the information
        #     for key, pattern in key_phrases.items():
        #         matches = re.finditer(pattern, text)
        #         extracted_values = []
        #         for match in matches:
        #             # Remove the unwanted part from the extracted first names
        #             first_name = match.group(1).strip().split("NAME EXTN.")[0].strip()
        #             extracted_values.append(first_name)
        #         key_value_pairs[key] = ', '.join(extracted_values)


        #     # Save extracted data to JSON file
        #     with open("extracted_data.json", "w") as json_file:
        #         json.dump(key_value_pairs, json_file, indent=4)

        #     # Assuming you create a ProcessedDocument instance
            # processed_document = ProcessedDocument()
            # processed_document = ProcessedDocument(document=uploaded_file, upload_date=timezone.now())
            # processed_document.save()

        #     extracted_data_instance, created = ExtractedData.objects.get_or_create(
        #         processed_document=processed_document
        #     )
        #     extracted_data_instance.save_extracted_data(key_value_pairs)

        # # # Save the ProcessedDocument instance
        # #     processed_document.save()

            # Create ExtractedData instance and save extracted data
            # extracted_data_instance = ExtractedData(processed_document=processed_document)
            # extracted_data_instance.save_extracted_data(key_value_pairs)

            # Construct the URL of the uploaded document.
            # uploaded_document_path = os.path.join(settings.MEDIA_URL, str(processed_document.document))

            # all_extracted_data = ExtractedData.objects.all().order_by('last_name')

       

            # # Iterate through the key phrases and extract the information
            # extracted_data_for_review = {}
            # for key, pattern in key_phrases.items():
            #     matches = re.finditer(pattern, text)
            #     extracted_values = []
            #     for match in matches:
            #         # Remove the unwanted part from the extracted first names
            #         first_name = match.group(1).strip().split("NAME EXTN.")[0].strip()
            #         extracted_values.append(first_name)
            # extracted_data_for_review[key] = ', '.join(extracted_values)

            # # Print the extracted data for review in the console
            # print("Extracted Data for Review:")
            # print(extracted_data_for_review)

            # extracted_data_for_excel = {}
            # for key, pattern in key_phrases.items():
            #     matches = re.finditer(pattern, text)
            #     extracted_values = []
            #     for match in matches:
            #         # Remove the unwanted part from the extracted first names
            #         first_name = match.group(1).strip().split("NAME EXTN.")[0].strip()
            #         extracted_values.append(first_name)
            #     extracted_data_for_excel[key] = ', '.join(extracted_values)

            # # Create a new workbook and add data to it
            # workbook = openpyxl.Workbook()
            # sheet = workbook.active

            # # Write extracted data to the Excel sheet
            # for idx, (key, value) in enumerate(extracted_data_for_excel.items(), start=1):
            #     sheet.cell(row=idx, column=1, value=key)
            #     sheet.cell(row=idx, column=2, value=value)

            # processed_document_filename = processed_document.document.name

            # timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

            # subdirectory = 'excel-files'

            # # Generate the file name with the timestamp
            # excel_file_name = f"{os.path.splitext(os.path.basename(processed_document_filename))[0]}_{timestamp}.xlsx"

            # # Join the subdirectory and file name with the MEDIA_ROOT directory
            # excel_file_path = os.path.join(settings.MEDIA_ROOT, subdirectory, excel_file_name)

            # # Ensure the subdirectory exists; create it if not
            # os.makedirs(os.path.dirname(excel_file_path), exist_ok=True)

            # # Save the workbook to the specified path
            # workbook.save(excel_file_path)

            # print("Data successfully written to Excel file:", excel_file_path)

            # extracted_data_for_review = {}  # Modify this line based on your extracted data
            # extracted_text = " ".join(extracted_data_for_review.values()) 
            # print(processed_document.document.url)
            # Render the 'processed_document.html' template with the extracted text and document URL.
            # return render(request, 'admin_template/edit_extracted_data.html', {'document_text': text, 'uploaded_document_url': uploaded_document_path, 'all_extracted_data': all_extracted_data,})
        # return render(request, 'admin_template/edit_extracted_data.html', {'extracted_data': extracted_data_for_review, 'document_text': text, 'uploaded_document_url': uploaded_document_path, 'all_extracted_data': all_extracted_data,})
            # download_link = reverse('download_document', args=[processed_document.id])

        return render(request, 'admin_template/edit_extracted_data.html', {
                # 'extracted_data': extracted_data_for_review,
                'document_text': text,
                'uploaded_document_url': processed_document.document.url,
                # 'all_extracted_data': all_extracted_data,
                'processed_document': processed_document,
                'download_link': processed_document.document.url,
                # 'extracted_text': extracted_text 
            })
    else:
        form = DocumentUploadForm()

    return render(request, 'admin_template/upload_documents.html', {'form': form})



def save_edited_data(request):  
    if request.method == 'POST':
        # Assuming extracted_data is sent as POST data, retrieve it
        extracted_data = {
            "REGION": request.POST.get("REGION"),
            "DIVISION": request.POST.get("DIVISION"),
            "SCHOOL YEAR": request.POST.get("SCHOOL YEAR"),
            "SCHOOL NAME": request.POST.get("SCHOOL NAME"),
            "SCHOOL ID": request.POST.get("SCHOOL ID"),
            "GRADE_SECTION": request.POST.get("GRADE SECTION"),
            "LAST NAME": request.POST.get("LAST NAME", ""),  # Provide a default empty string
            "FIRST NAME": request.POST.get("FIRST NAME", ""),
            "MIDDLE NAME": request.POST.get("MIDDLE NAME", "") ,
        }

        # Create a new ProcessedDocument instance
        processed_document = ProcessedDocument.objects.create()

        # Create an ExtractedData instance and save the extracted data
        extracted_data_instance = ExtractedData(processed_document=processed_document)
        extracted_data_instance.save_extracted_data(extracted_data)

        print(extracted_data)
        # Create a custom success message
        success_message = "Data has been successfully saved!"

        # Send an HTTP response with the success message
        return HttpResponse(success_message)

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