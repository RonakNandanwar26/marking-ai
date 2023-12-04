from PyPDF2 import PdfReader
import re
import os
from pdf.models import *
from django.db.models import Max
from django.core.exceptions import ObjectDoesNotExist


def handle_uploaded_pdf(pdf_file):
    try:
        # Specify the directory where you want to save the uploaded PDFs
        upload_dir = 'media/uploaded_pdfs/'
        os.makedirs(upload_dir, exist_ok=True)
        with open(os.path.join(upload_dir, pdf_file.name), 'wb') as destination:
            for chunk in pdf_file.chunks():
                destination.write(chunk)

        return True, "File uploaded successfully."
    except Exception as e:
        return False, f"Error uploading file: {str(e)}"

def fetch_substring(input_string, start_char, end_char):
    start_index = input_string.find(start_char)
    if not end_char == -1:
        end_index = input_string.find(end_char, start_index + 1)
    else:
        end_index = -1
    
    if start_index != -1 and end_index != -1:
        result_substring = input_string[start_index + len(start_char):end_index]
        return result_substring.strip()  # Remove leading and trailing whitespaces
    elif start_index != -1 and end_index == -1:
        result_substring = input_string[start_index + len(start_char):]
        return result_substring.strip()
    else:
        return None
    
def check_counts(result):
    ques = len(re.findall(r'Question:', result))
    ans  = len(re.findall(r'Answer:', result))
    pattern = re.compile(r'Question \d+\.\d+')
    matches = pattern.findall(result)
    count = len(matches)
    if ques == ans == count:
        return 0
    else:
        return 1
    
def check_counts_educator(result):
    ques = len(re.findall(r'Question:', result))
    ans  = len(re.findall(r'Instructions to marker:', result))
    pattern = re.compile(r'Question \d+\.\d+')
    matches = pattern.findall(result)
    count = len(matches)
    if ques == ans == count:
        return 0
    else:
        return 1

def extract_pdf_text(file,typ):
    # with open(filepath,'rb') as pdf:
    reader = PdfReader(file)
    results = []
    for i in range(len(reader.pages)):
        page = reader.pages[i]
        text = page.extract_text()
        results.append(text)
    result = ' '.join(results)
    result = result.replace('\n', ' ')
    if typ == 'Teacher':
        verify = check_counts_educator(result)
    else:
        verify = check_counts(result)
    if verify == 0:
        QA = re.split(r'Question \d+\.\d+', result)[1:]
        sections = re.findall(r'Question \d+\.\d+', result)

        for i in range(len(QA)):
            QA[i] = sections[i] + QA[i]
        if typ == 'Teacher':
            answer = 'Instructions to marker:'
        else:
            answer = 'Answer:'
        final_QA = []
        for i in range(len(QA)):
            qa_dict = {}
            qa_dict['section'] = sections[i].split()[1].split('.')[0]
            qa_dict['question_no'] = sections[i].split()[1].split('.')[1]
            qa_dict['question'] = fetch_substring(QA[i],'Question:','(')
            qa_dict['marks'] = fetch_substring(QA[i],'(',')')
            qa_dict['answer'] = fetch_substring(QA[i],answer,-1)
            final_QA.append(qa_dict)

        return QA,final_QA
    else :
        return 1,1

def evaluate_pdf(QA,typ):
    errors =[]
    q = None
    cur_que_no = None
    cur_section_no = None
    if typ == 'Teacher':
        answer = 'Instructions to marker:'
    else:
        answer = 'Answer:'
    for i in QA:
        # print(i)
        if not re.search(r'Question \d+\.\d+',i):
            print("checking section")
            if q is not None:
                errors.append(f"There is a problem with Section and Question number after {q}")
            else:
                errors.append("There is a problem with Section and Question number in first question")
        else:
            q = re.findall(r'Question \d+\.\d+',i)[0]
            # print(q)
            cur_section_no = q.split()[1].split('.')[0]
            cur_que_no = section_no = q.split()[1].split('.')[1]
            if not re.search(r'Question:',i):
                print("checking Question")
                errors.append(f"There is a problem with Question: in {q}, also please check spelling of question or : is missing")
            else:
                if not re.search(answer,i):
                    print('checking Instruction')
                    errors.append(f"There is a problem with {answer} in {q}, also please check spelling of Instructions to marker:")
                else:
                    print("checking marks")
                    check_marks_string = fetch_substring(i,'Question:',answer)
                    # print(check_marks_string)
                    if not re.search(r'.*\(\d+ mark(s)?\)$',check_marks_string):
                        errors.append(f"There is a problem with Marks in {q}, also please check spelling of Marks or check if ( or ) is missing.")
    return errors



def evaluate_student_pdf(QA):
    errors =[]
    q = None
    cur_que_no = None
    cur_section_no = None
    for i in QA:
        # print(i)
        if not re.search(r'Question \d+\.\d+',i):
            if q is not None:
                errors.append(f"There is a problem with Section and Question number after {q}")
            else:
                errors.append("There is a problem with Section and Question number in first question")
        else:
            q = re.findall(r'Question \d+\.\d+',i)[0]
            # print(q)
            section_no = q.split()[1].split('.')[0]
            que_no = section_no = q.split()[1].split('.')[1]
            if not re.search(r'Question:',i):
                print("checking Question")
                errors.append(f"There is a problem with Question: in {q}, also please check spelling of question or : is missing")
            else:
                if not re.search(r'Answer:',i):
                    print('checking Instruction')
                    errors.append(f"There is a problem with Instructions to marker: in {q}, also please check spelling of Instructions to marker:")
                else:
                    print("checking marks")
                    check_marks_string = fetch_substring(i,'Question:','Answer:')
                    # print(check_marks_string)
                    if not re.search(r'.*\(\d+ mark(s)?\)$',check_marks_string):
                        errors.append(f"There is a problem with Marks in {q}, also please check spelling of Marks or check if ( or ) is missing.")
    return errors

def upload_assessment(file,typ,final_qa):
    try:
        if typ == 'Teacher':
            assessment = Assessment.objects.create(teacher_id=1,file=file)
            
            for i in final_qa:
                Question.objects.create(section_number=i['section'],
                                        question_number=i['question_no'],
                                        marks=i['marks'][0],
                                        question_text=i['question'],
                                        marking_guide=i['answer'],
                                        assessment_id=assessment)
        else:
            assessment = Assessment.objects.aggregate(Max('id')) 
            assessment_id = assessment['id__max']
            print("assessment_id",assessment_id)
            assessment = Assessment.objects.get(id=assessment_id)
            attempt = Attempts.objects.aggregate(Max('attempt_id')) 
            print('attempt id',attempt['attempt_id__max'])
            attempt_id = attempt['attempt_id__max'] 
            if attempt_id is None:
                attempt_id=1
            else:
                attempt_id+=1
            print('new attempt id',attempt_id)
            for i in final_qa:
                Attempts.objects.create(attempt_id=attempt_id,
                                        student_id=1,
                                        section_id=i['section'],
                                        question_id=i['question_no'],
                                        assessment=assessment,
                                        answer=i['answer'])
        return 0
    except ObjectDoesNotExist:
        return 1
    except Exception as e:
        return e
    
def validate_pdf (text, typ):
    try:
        if typ == "Teacher":
            question_pattern = re.compile(r'''
                                Question\s+(\d+\.\d+)  # Match "Question" followed by a space, and capture the question number
                                \s*Question:\s*        # Match optional spaces and "Question:"
                                ([\s\S]*?)             # Capture the question text (non-greedy)
                                \(\d+\s*mark[s]?\)           # Match "(marks)"
                                \s*Instructions\s+to\s+marker:\s*  # Match "Instructions to marker:" with optional spaces
                                ([\s\S]*?)             # Capture the instructions (non-greedy)
                                (?=\n\n|$)             # Lookahead for two consecutive newlines or end of string
                            ''', re.VERBOSE)
            questions = re.findall(question_pattern, text)

            # Check if questions are found
            if questions:
                return True
            else:
                return False
        else:
            # Define a regular expression pattern to match the format
            pattern = r'Question\s*\d+\.\d+\s*Question:\s*(.*?)\(\d+\s*mark[s]?\)\s*Answer:\s*(.*?)\n'
        
        # Use re.findall to find all occurrences of the pattern in the text
            matches = re.findall(pattern, text, re.DOTALL)

        # Return True if at least one match is found, else return False
            return bool(matches)
    except Exception as e:
        print(e)
        return e
    