from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from certificates.models import StudentLead
from certificates.utils import generate_certificate_image, generate_certificate_pdf_bytes


class CertificatePortalTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_superuser('testadmin', 'test@natdemy.com', 'password123')

    def test_form_submission_creates_lead_and_redirects(self):
        """Test student filling out form creates lead in database and redirects to certificate page."""
        response = self.client.post(reverse('certificates:request_certificate'), {
            'name': 'Rahul Sharma',
            'student_class': '2nd Year',
            'phone_number': '9876543210'
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        lead = StudentLead.objects.filter(phone_number='9876543210').first()
        self.assertIsNotNone(lead)
        self.assertEqual(lead.name, 'Rahul Sharma')
        self.assertEqual(lead.student_class, '2nd Year')
        self.assertEqual(lead.download_count, 0)
        self.assertContains(response, 'Rahul Sharma')

    def test_dropdown_choices(self):
        """Test dropdown contains 1st Year, 2nd Year, 3rd Year and rejects invalid choice."""
        for valid_class in ['1st Year', '2nd Year', '3rd Year']:
            response = self.client.post(reverse('certificates:request_certificate'), {
                'name': 'Test Student',
                'student_class': valid_class,
                'phone_number': '9123456789'
            })
            self.assertEqual(response.status_code, 302)

        # Invalid class
        response = self.client.post(reverse('certificates:request_certificate'), {
            'name': 'Invalid Student',
            'student_class': '4th Year',
            'phone_number': '9123456789'
        })
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response.context['form'], 'student_class', 'Select a valid choice. 4th Year is not one of the available choices.')

    def test_certificate_preview_and_download(self):
        """Test certificate image preview and download increments count."""
        lead = StudentLead.objects.create(
            name='Fathima Zahra',
            student_class='1st Year',
            phone_number='9988776655'
        )

        # Test preview
        preview_resp = self.client.get(reverse('certificates:certificate_preview', kwargs={'uuid': str(lead.certificate_uuid)}))
        self.assertEqual(preview_resp.status_code, 200)
        self.assertEqual(preview_resp['Content-Type'], 'image/jpeg')
        self.assertTrue(len(preview_resp.content) > 100000)

        # Test image download
        img_download_resp = self.client.get(reverse('certificates:download_image', kwargs={'uuid': str(lead.certificate_uuid)}))
        self.assertEqual(img_download_resp.status_code, 200)
        self.assertEqual(img_download_resp['Content-Type'], 'image/jpeg')
        self.assertIn('attachment;', img_download_resp['Content-Disposition'])

        lead.refresh_from_db()
        self.assertEqual(lead.download_count, 1)

        # Test PDF download
        pdf_download_resp = self.client.get(reverse('certificates:download_pdf', kwargs={'uuid': str(lead.certificate_uuid)}))
        self.assertEqual(pdf_download_resp.status_code, 200)
        self.assertEqual(pdf_download_resp['Content-Type'], 'application/pdf')
        self.assertIn('attachment;', pdf_download_resp['Content-Disposition'])

        lead.refresh_from_db()
        self.assertEqual(lead.download_count, 2)

    def test_certificate_image_generation(self):
        """Verify image dimensions and rendering."""
        im = generate_certificate_image("Muhammed Rashid")
        self.assertEqual(im.size, (3508, 2480))

    def test_admin_export(self):
        """Verify admin can export leads to Excel and CSV."""
        StudentLead.objects.create(name='Anil Kumar', student_class='3rd Year', phone_number='9871234560')
        self.client.force_login(self.admin_user)

        # Admin change list page
        admin_resp = self.client.get('/admin/certificates/studentlead/')
        self.assertEqual(admin_resp.status_code, 200)
        self.assertContains(admin_resp, 'Anil Kumar')
