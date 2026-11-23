import uuid
from django.db import models
from django.urls import reverse


class StudentLead(models.Model):
    CLASS_CHOICES = [
        ('1st Year', '1st Year'),
        ('2nd Year', '2nd Year'),
        ('3rd Year', '3rd Year'),
    ]

    id = models.BigAutoField(primary_key=True)
    certificate_uuid = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
        verbose_name="Certificate ID"
    )
    name = models.CharField(
        max_length=150,
        verbose_name="Student Name",
        help_text="Candidate name printed on the certificate"
    )
    student_class = models.CharField(
        max_length=20,
        choices=CLASS_CHOICES,
        verbose_name="Class / Year"
    )
    phone_number = models.CharField(
        max_length=25,
        verbose_name="Phone Number / WhatsApp"
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name="IP Address"
    )
    download_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Download Count"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Registered Date"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Last Updated"
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Student Lead"
        verbose_name_plural = "Student Leads & Certificates"

    def __str__(self):
        return f"{self.name} ({self.student_class}) - {self.phone_number}"

    def get_absolute_url(self):
        return reverse('certificates:certificate_detail', kwargs={'uuid': str(self.certificate_uuid)})
