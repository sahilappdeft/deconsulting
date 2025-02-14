import pdfplumber
import json
import os
import fitz  # PyMuPDF

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status

from .serializers import FileUploadSerializer
from .utilis.pdfToJSON import extract_pdf_data

def success(message, data):
    res = {
        'success': True,
        'message': message,
        'data': data,
    }
    return res


# Error middleware
def error(message, data):
    res = {
        'success': False,
        'message': message,
        'data': data,
    }
    return res

class FileChatView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request):
        serializer = FileUploadSerializer(data=request.data)
        
        if serializer.is_valid():
            temp_dir = "temp"
            os.makedirs(temp_dir, exist_ok=True)

            extracted_texts = {}
            # Iterate over each category key
            for category, files in serializer.validated_data.items():
                if files:  # Process only if files exist in the category
                    
                    for file in files:
                        file_path = os.path.join(temp_dir, file.name)
                        with open(file_path, 'wb+') as destination:
                            for chunk in file.chunks():
                                destination.write(chunk)

                        extracted_text = extract_pdf_data(file_path)
                        extracted_texts[category] = extracted_text['data']
                        
            return Response(success('success', extracted_texts), status=status.HTTP_200_OK)
        return Response(error(serializer.errors, {}), status=status.HTTP_200_OK)
