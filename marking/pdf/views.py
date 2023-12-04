from django.shortcuts import render
import os
from utility.pdf_utility import *
from django.views.generic import TemplateView
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import JsonResponse
from django.middleware.csrf import get_token
from rest_framework import status
# Create your views here.
def get_csrf_token(request):
    csrf_token = get_token(request)
    print("csrf_token",csrf_token)
    return JsonResponse({'csrf_token': csrf_token})
class UploadPDF(APIView):
    # template_name = 'pdf_upload.html'
    
    def post(self,request):
        pdf_file = request.FILES['pdf_file']
        print(pdf_file.name)
        parts = pdf_file.name.split('.')
        # Check if the last part is 'pdf'
        if parts[-1].lower() != 'pdf':
            return render(request, 'pdf_upload.html', {'response_message': "Please upload PDF file", 'success': False})
        typ = request.POST['type'] 
        print(typ)
        # success, response_message = handle_uploaded_pdf(pdf_file)
        QA,final_QA = extract_pdf_text(pdf_file,typ)
        if QA ==1:
            return Response({"status_code":400,"response_msg":"PDF upload failed, Please do the changes and upload again..."},status = status.HTTP_400_BAD_REQUEST)
        if len(QA)==0:
            success = False
            response_message = "PDF upload failed, Please do the changes and upload again..."
        else:
            print(QA)
            print(final_QA)
            errors = evaluate_pdf(QA,typ)
            print(errors)
            if len(errors) == 0:
                success = True
                resp = upload_assessment(pdf_file,typ,final_QA)
                print("resp", resp)
                if resp == 0:
                    response_message = "PDF File Uploaded Successfully..."
                elif resp ==1 :
                    success = False
                    response_message = "Assessment dose not exists."
                else:
                    success = False
                    response_message = "PDF upload failed, Please do the changes and upload again..."
            else:
                success = False
                response_message = "PDF upload failed, Please do the changes and upload again..."
        print("Print success", success)
        if success:
            # return render(request, 'pdf_upload.html', {'response_message': response_message, 'success': True})
            return Response({"status_code":200,"response_msg":response_message}, status= status.HTTP_200_OK)
        else:
            # return render(request, 'pdf_upload.html', {'response_message': response_message, 'success': False})
            return Response({"status_code":400,"response_msg":response_message},status = status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        return render(request, self.template_name)