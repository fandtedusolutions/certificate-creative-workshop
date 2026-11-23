import re
import csv
from datetime import datetime
from django.contrib import admin
from django.http import HttpResponse
from django.utils.html import format_html
from django.urls import reverse
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from .models import StudentLead


admin.site.site_header = "Natdemy Workshop Administration"
admin.site.site_title = "Natdemy Certificates & Leads"
admin.site.index_title = "Certificate Generation & Student Leads Portal"


@admin.register(StudentLead)
class StudentLeadAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'student_class_badge',
        'phone_with_actions',
        'download_count_badge',
        'created_at_formatted',
        'certificate_actions',
    )
    list_filter = ('student_class', 'created_at')
    search_fields = ('name', 'phone_number', 'certificate_uuid')
    readonly_fields = (
        'certificate_uuid',
        'download_count',
        'ip_address',
        'created_at',
        'updated_at',
        'certificate_preview_html',
    )
    actions = ['export_to_excel', 'export_to_csv']
    date_hierarchy = 'created_at'
    list_per_page = 25

    fieldsets = (
        ("Student Information", {
            'fields': ('name', 'student_class', 'phone_number')
        }),
        ("Certificate & Tracking", {
            'fields': ('certificate_uuid', 'download_count', 'ip_address', 'certificate_preview_html')
        }),
        ("Timestamps", {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def student_class_badge(self, obj):
        colors = {
            '1st Year': '#0d6efd',
            '2nd Year': '#198754',
            '3rd Year': '#d63384',
        }
        color = colors.get(obj.student_class, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 10px; border-radius: 12px; font-weight: 600; font-size: 11px;">{}</span>',
            color, obj.student_class
        )
    student_class_badge.short_description = "Class"
    student_class_badge.admin_order_field = 'student_class'

    def phone_with_actions(self, obj):
        # Format clean phone number for whatsapp
        digits = re.sub(r'\D', '', obj.phone_number)
        if len(digits) == 10:
            wa_number = f"91{digits}"
        else:
            wa_number = digits

        return format_html(
            '<div style="display:flex; align-items:center; gap:8px;">'
            '<a href="tel:{}" style="font-weight:600; color:#13334d; text-decoration:none;">📞 {}</a>'
            '<a href="https://wa.me/{}" target="_blank" title="Chat on WhatsApp" style="background:#25D366; color:white; border-radius:12px; padding:2px 8px; text-decoration:none; font-size:11px; font-weight:bold;">WhatsApp</a>'
            '</div>',
            obj.phone_number, obj.phone_number, wa_number
        )
    phone_with_actions.short_description = "Phone / WhatsApp"
    phone_with_actions.admin_order_field = 'phone_number'

    def download_count_badge(self, obj):
        bg = '#20c997' if obj.download_count > 0 else '#adb5bd'
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 10px; font-weight: bold; font-size: 11px;">{} downloads</span>',
            bg, obj.download_count
        )
    download_count_badge.short_description = "Downloads"
    download_count_badge.admin_order_field = 'download_count'

    def created_at_formatted(self, obj):
        return obj.created_at.strftime("%d %b %Y, %I:%M %p")
    created_at_formatted.short_description = "Registered On"
    created_at_formatted.admin_order_field = 'created_at'

    def certificate_actions(self, obj):
        preview_url = reverse('certificates:certificate_preview', kwargs={'uuid': str(obj.certificate_uuid)})
        detail_url = reverse('certificates:certificate_detail', kwargs={'uuid': str(obj.certificate_uuid)})
        return format_html(
            '<a href="{}" target="_blank" class="button" style="background:#13334d; color:white; padding:4px 8px; border-radius:4px; text-decoration:none; margin-right:4px;">View</a> '
            '<a href="{}" target="_blank" class="button" style="background:#d4af37; color:#111; padding:4px 8px; border-radius:4px; text-decoration:none; font-weight:bold;">Student Page</a>',
            preview_url, detail_url
        )
    certificate_actions.short_description = "Actions"

    def certificate_preview_html(self, obj):
        if obj.certificate_uuid:
            preview_url = reverse('certificates:certificate_preview', kwargs={'uuid': str(obj.certificate_uuid)})
            return format_html(
                '<div style="margin-top:10px;"><a href="{}" target="_blank">'
                '<img src="{}" style="max-width: 480px; border: 2px solid #ddd; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);" />'
                '</a><p style="color:#666; font-size:12px; margin-top:4px;">Click image to open full resolution certificate</p></div>',
                preview_url, preview_url
            )
        return "Not generated yet"
    certificate_preview_html.short_description = "Certificate Preview"

    @admin.action(description="📥 Export Selected Leads to Excel (.xlsx)")
    def export_to_excel(self, request, queryset):
        workbook = openpyxl.Workbook()
        worksheet = workbook.active
        worksheet.title = "Natdemy Workshop Leads"

        # Styles
        header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
        header_fill = PatternFill(start_color="13334D", end_color="13334D", fill_type="solid")
        border = Border(
            left=Side(style='thin', color='DDDDDD'),
            right=Side(style='thin', color='DDDDDD'),
            top=Side(style='thin', color='DDDDDD'),
            bottom=Side(style='thin', color='DDDDDD')
        )

        headers = [
            "SL No",
            "Student Name",
            "Class / Year",
            "Phone Number / WhatsApp",
            "Downloads Count",
            "Registration Date & Time",
            "Certificate UUID",
            "Certificate Direct Link",
        ]
        worksheet.append(headers)

        for cell in worksheet[1]:
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = Alignment(horizontal="center", vertical="center")

        base_url = request.build_absolute_uri('/')[:-1]

        for idx, lead in enumerate(queryset, start=1):
            cert_url = base_url + reverse('certificates:certificate_detail', kwargs={'uuid': str(lead.certificate_uuid)})
            row = [
                idx,
                lead.name,
                lead.student_class,
                lead.phone_number,
                lead.download_count,
                lead.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                str(lead.certificate_uuid),
                cert_url
            ]
            worksheet.append(row)

        # Format column widths
        for col in worksheet.columns:
            max_len = max(len(str(cell.value or '')) for cell in col)
            col_letter = col[0].column_letter
            worksheet.column_dimensions[col_letter].width = max(max_len + 4, 12)

        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        filename = f"Natdemy_Leads_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        workbook.save(response)
        return response

    @admin.action(description="📄 Export Selected Leads to CSV")
    def export_to_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        filename = f"Natdemy_Leads_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'

        writer = csv.writer(response)
        writer.writerow([
            "ID", "Student Name", "Class / Year", "Phone Number",
            "Downloads", "Registered Date", "Certificate UUID", "Certificate Link"
        ])

        base_url = request.build_absolute_uri('/')[:-1]
        for lead in queryset:
            cert_url = base_url + reverse('certificates:certificate_detail', kwargs={'uuid': str(lead.certificate_uuid)})
            writer.writerow([
                lead.id,
                lead.name,
                lead.student_class,
                lead.phone_number,
                lead.download_count,
                lead.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                str(lead.certificate_uuid),
                cert_url,
            ])
        return response
