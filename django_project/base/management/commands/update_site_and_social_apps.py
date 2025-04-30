from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp
import getpass


class Command(BaseCommand):
    help = 'Updates default Site and Social Application configurations'

    def handle(self, *args, **options):
        self.stdout.write(self.style.HTTP_INFO("\n=== Site Configuration Update ==="))
        self.update_site()
        self.stdout.write(self.style.HTTP_INFO("\n=== Social Applications Update ==="))
        self.update_social_apps()

    def update_site(self):
        """Update the default Site domain and display name"""
        try:
            site = Site.objects.get_current()
            self.stdout.write(self.style.HTTP_INFO("\nCurrent Site Configuration:"))
            self.stdout.write(f"Domain: {site.domain}")
            self.stdout.write(f"Display Name: {site.name}\n")

            new_domain = input("Enter new domain (e.g., example.com): ").strip()
            new_name = input("Enter new display name: ").strip()

            if new_domain:
                site.domain = new_domain
            if new_name:
                site.name = new_name

            site.save()
            self.stdout.write(self.style.SUCCESS("Site updated successfully!"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error updating site: {str(e)}"))

    def update_social_apps(self):
        """Update all Social Applications"""
        social_apps = SocialApp.objects.all()

        if not social_apps.exists():
            self.stdout.write(self.style.WARNING("No social applications found."))
            return

        for app in social_apps:
            self.stdout.write(self.style.HTTP_INFO(f"\nUpdating {app.provider} application:"))

            # Get new values with current values as placeholders
            new_name = input(f"Application name [{app.name}]: ").strip() or app.name
            new_client_id = input(f"Client ID [{app.client_id}]: ").strip() or app.client_id

            # For secret key, don't show current value for security
            self.stdout.write("Current secret key: [hidden]")
            new_secret = getpass.getpass("New Secret Key (leave blank to keep current): ").strip()

            # Update fields
            app.name = new_name
            app.client_id = new_client_id
            if new_secret:
                app.secret = new_secret

            try:
                app.save()
                self.stdout.write(self.style.SUCCESS(f"{app.provider} application updated!"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error updating {app.provider}: {str(e)}"))
