# from django.shortcuts import render
# Create your views here.

from django.shortcuts import render
from .services import process_arff

def index(request):
    context = {}
    if request.method == "POST":
        file = request.FILES.get("file")
        if not file:
            context["error"] = "Debes subir un archivo .arff"
        else:
            try:
                context["result"] = process_arff(file)
            except Exception as e:
                context["error"] = f"Error procesando archivo: {str(e)}"
    return render(request, "index.html", context)

