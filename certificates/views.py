import urllib.parse
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, Http404
from django.contrib import messages
from django.views.decorators.http import require_GET, require_http_methods
from .models import StudentLead
from .forms import StudentLeadForm
from .utils import (
    generate_certificate_jpeg_bytes,
    generate_certificate_pdf_bytes,
)


def get_client_ip(request):
    """Retrieve user real IP address behind proxies or directly."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


@require_http_methods(["GET", "POST"])
def certificate_request_view(request):
    """
    Public student entry page:
    Fill Name, Class (1st, 2nd, 3rd year), Phone number, and click 'Get Certificate'.
    """
    if request.method == "POST":
        form = StudentLeadForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            student_class = form.cleaned_data['student_class']
            phone_number = form.cleaned_data['phone_number']
            ip_addr = get_client_ip(request)

            # Check if lead with identical name and phone already exists
            existing_lead = StudentLead.objects.filter(
                name__iexact=name,
                phone_number=phone_number
            ).first()

            if existing_lead:
                # Update details if re-submitting same student
                existing_lead.name = name
                existing_lead.student_class = student_class
                existing_lead.ip_address = ip_addr
                existing_lead.save()
                lead = existing_lead
                messages.success(request, f"Welcome back, {name}! Your certificate is ready.")
            else:
                # Save new lead in backend database
                lead = form.save(commit=False)
                lead.ip_address = ip_addr
                lead.save()
                messages.success(request, f"Congratulations, {name}! Your certificate has been generated successfully.")

            return redirect('certificates:certificate_detail', uuid=str(lead.certificate_uuid))
    else:
        form = StudentLeadForm()

    context = {
        'form': form,
        'title': "Natdemy Workshop Certificate Portal",
        'workshop_title': "CREATIVE WORKSHOP",
        'institution': "St. Joseph's College Devagiri, Kozhikode",
        'date': "23 November 2026",
    }
    return render(request, 'certificates/index.html', context)


@require_GET
def certificate_detail_view(request, uuid):
    """
    Shows student's generated certificate with live preview, download options,
    and social sharing buttons.
    """
    lead = get_object_or_404(StudentLead, certificate_uuid=uuid)
    
    current_url = request.build_absolute_uri()
    whatsapp_text = urllib.parse.quote(
        f"Hey! I just got my Certificate of Participation from Natdemy for the Creative Workshop held at St. Joseph's College Devagiri! 🎓 Check it out here: {current_url}"
    )

    context = {
        'lead': lead,
        'whatsapp_text': whatsapp_text,
        'page_url': current_url,
    }
    return render(request, 'certificates/detail.html', context)


@require_GET
def certificate_preview_view(request, uuid):
    """Inline JPEG preview of the certificate for <img src> or direct view."""
    lead = get_object_or_404(StudentLead, certificate_uuid=uuid)
    buf = generate_certificate_jpeg_bytes(lead.name, quality=90)
    return HttpResponse(buf.getvalue(), content_type="image/jpeg")


@require_GET
def certificate_download_image_view(request, uuid):
    """Download certificate as 300 DPI high-resolution JPEG."""
    lead = get_object_or_404(StudentLead, certificate_uuid=uuid)
    lead.download_count += 1
    lead.save(update_fields=['download_count', 'updated_at'])

    buf = generate_certificate_jpeg_bytes(lead.name, quality=95)
    safe_name = "".join(c for c in lead.name if c.isalnum() or c in (' ', '_', '-')).strip().replace(' ', '_')
    filename = f"Natdemy_Certificate_{safe_name}.jpg"

    response = HttpResponse(buf.getvalue(), content_type="image/jpeg")
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


@require_GET
def certificate_download_pdf_view(request, uuid):
    """Download certificate as 300 DPI print-ready PDF."""
    lead = get_object_or_404(StudentLead, certificate_uuid=uuid)
    lead.download_count += 1
    lead.save(update_fields=['download_count', 'updated_at'])

    buf = generate_certificate_pdf_bytes(lead.name)
    safe_name = "".join(c for c in lead.name if c.isalnum() or c in (' ', '_', '-')).strip().replace(' ', '_')
    filename = f"Natdemy_Certificate_{safe_name}.pdf"

    response = HttpResponse(buf.getvalue(), content_type="application/pdf")
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response
