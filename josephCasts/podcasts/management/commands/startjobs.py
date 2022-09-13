# podcasts/management/commands/startjobs.py


# Creating a Django custom command that can be run directly with manage.py


# Standard library
import logging 

# Django
from django.conf import settings 
from django.core.management.base import BaseCommand

# Third Party
import feedparser
from dateutil import parser
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution


# Models
from podcasts.models import Episode

logger = logging.getLogger(__name__)


def save_new_episodes(feed):
    podcast_title = feed.channel.title
    podcast_image = feed.channel.image["href"]

    for item in feed.entries:
        if not Episode.objects.filter(guid=item.guid).exists():


            

            episode = Episode(
                title=item.title,
                description=item.description,
                pub_date=parser.parse(item.published),
                link=item.link,
                image=podcast_image,
                podcast_name=podcast_title,
                guid=item.guid,
            )
            episode.save()

def fetch_storehouses_episodes():
    _feed = feedparser.parse("https://anchor.fm/s/594997c/podcast/rss")
    save_new_episodes(_feed)

def fetch_college_episodes():
    _feed = feedparser.parse("https://anchor.fm/s/67b8c88/podcast/rss")
    save_new_episodes(_feed)

def fetch_yp_episodes():
    _feed = feedparser.parse("https://anchor.fm/s/5aa41a0/podcast/rss")
    save_new_episodes(_feed)

def fetch_special_episodes():
    _feed = feedparser.parse("https://anchor.fm/s/680d60c/podcast/rss")
    save_new_episodes(_feed)

def delete_old_job_executions(max_age=604_800):
    DjangoJobExecution.objects.delete_old_job_executions(max_age)



class Command(BaseCommand):
    help = "Runs apscheduler."

    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")

        scheduler.add_job(
            fetch_storehouses_episodes,
            trigger="interval",
            minutes=2,
            id="Joseph's Storehouses",
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added job: Joseph's Storehouses.")

        scheduler.add_job(
            fetch_college_episodes,
            trigger="interval",
            minutes=2,
            id="Joseph's Storehouses College",
            max_instances=1,
            replace_existing=True,
        )

        logger.info("Added job: Joseph's Storehouses - College.")

        scheduler.add_job(
            fetch_yp_episodes,
            trigger="interval",
            minutes=2,
            id="Joseph's Storehouses YP",
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added job: Joseph's Storehouses - YP.")

        scheduler.add_job(
            fetch_special_episodes,
            trigger="interval",
            minutes=2,
            id="Joseph's Storehouses Special",
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added job: Joseph's Storehouses - Special.")


        scheduler.add_job(
            delete_old_job_executions,
            trigger=CronTrigger(
                day_of_week="mon", hour="00", minute="00"
            ),
            id="Delete Old Job Executions",
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added weekly job: Delete Old Job Executions")

        try:
            logger.info("Starting scheduler...")
            scheduler.start()
        except KeyboardInterrupt:
            logger.info("Stopping scheduler...")
            scheduler.shutdown()
            logger.info("Scheduler shut down successfully.")

    