from django.core.management.base import BaseCommand
from changes.models import Version
from datetime import datetime

class Command(BaseCommand):
  help = 'Update the release date for each version based on its name'

  def handle(self, *args, **kwargs):
    version_data = {
      "3.42": "2025-02-21",
      "3.40": "2024-10-25",
      "3.38": "2024-06-21",
      "3.36": "2024-02-23",
      "3.34": "2023-10-29",
      "3.32": "2023-06-26",
      "3.30": "2023-03-04",
      "3.28": "2022-10-21",
      "3.26": "2022-06-17",
      "3.24": "2022-02-18",
      "3.22": "2021-10-22",
      "3.20": "2021-06-18",
      "3.18": "2021-02-19",
      "3.16": "2020-10-23",
      "3.14": "2020-06-19",
      "3.12": "2020-02-21",
      "3.10 LTR": "2019-10-25",
      "3.8": "2019-06-21",
      "3.6.0": "2019-02-22",
      "3.4 LTR": "2018-10-26",
      "3.2.0": "2018-06-22",
      "3.0.0": "2018-02-23",
      "2.18.0": "2016-10-21",
      "2.16.0": "2016-07-08",
      "2.14.0": "2016-02-26",
      "2.12.0": "2015-10-23",
      "2.10.0": "2015-06-26",
      "2.8.0": "2015-02-20",
      "2.6.0": "2014-10-31",
      "2.4.0": "2014-06-27",
      "2.2.0": "2014-02-22",
      "2.0.0": "2013-09-09",
    }

    for version_name, release_date in version_data.items():
      try:
        version = Version.objects.get(
          name=version_name,
          project__slug="qgis"
        )
        version.release_date = datetime.strptime(release_date, "%Y-%m-%d").date()
        version.save()
        self.stdout.write(self.style.SUCCESS(f"Updated {version_name} with release date {release_date}"))
      except Version.DoesNotExist:
        self.stdout.write(self.style.WARNING(f"Version {version_name} does not exist in the database"))