import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _


class UUIDMixin(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True

class TimeStampedMixin(models.Model):
    created = models.DateTimeField(_('created'), auto_now_add=True)
    modified = models.DateTimeField(_('modified'), auto_now=True)

    class Meta:
        abstract = True


class Genre(UUIDMixin, TimeStampedMixin):
    name = models.CharField(_('Genre name'), unique=True, max_length=100)
    description = models.TextField(_('Description'), blank=True, null=True)

    class Meta:
        db_table = 'content"."genre'
        verbose_name = _("Genre")
        verbose_name_plural = _("Genres")

    def __str__(self):
        return self.name

class Person(UUIDMixin, TimeStampedMixin):
    full_name = models.CharField(_('Full name'), max_length=150)

    class Meta:
        db_table = 'content"."person'
        verbose_name = _("Person")
        verbose_name_plural = _("People")

    def __str__(self):
        return self.full_name

class FilmWork(UUIDMixin, TimeStampedMixin):

    TYPE_CHOICES = [
        (_("Film"), _("Film")),
        (_("TV show"), _("TV show")),
        (_("Series"), _("Series")),
        (_("Video"), _("Video")),
    ]

    title = models.CharField(_('Title'), max_length=255)
    description = models.TextField(_('Description'), blank=True, null=True)
    creation_date = models.DateField(_('Creation date'), blank=True, null=True)
    rating = models.DecimalField(_('Rating'), max_digits=3, decimal_places=1, blank=True, null=True)
    type = models.TextField(_('Type'), choices=TYPE_CHOICES)

    genres = models.ManyToManyField(Genre, through="GenreFilmWork")
    persons = models.ManyToManyField(Person, through="PersonFilmWork")

    class Meta:
        db_table = 'content"."film_work'
        verbose_name = _("Film")
        verbose_name_plural = _("Films")

    def __str__(self):
        return self.title



class GenreFilmWork(UUIDMixin):
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE, verbose_name=_('Genre'))
    film_work = models.ForeignKey(FilmWork, on_delete=models.CASCADE)

    class Meta:
        db_table = 'content"."genre_film_work'
        unique_together = ("genre", "film_work")
        verbose_name = _("Genre - Film")
        verbose_name_plural = _("Genre - Film")


class PersonFilmWork(UUIDMixin):

    ROLE_CHOICES = [
        (_("Actor"), _("Actor")),
        (_("Director"), _("Director")),
        (_("Writer"), _("Writer")),
        (_("Cameraman"), _("Cameraman")),
        (_("Composer"), _("Composer")),
    ]

    person = models.ForeignKey(Person, on_delete=models.CASCADE, verbose_name=_('Person'))
    film_work = models.ForeignKey(FilmWork, on_delete=models.CASCADE)
    role = models.TextField(choices=ROLE_CHOICES, verbose_name=_('Role'))

    class Meta:
        db_table = 'content"."person_film_work'
        unique_together = ("person", "film_work", "role")
        verbose_name = _("Person - Film")
        verbose_name_plural = _("Person - Film")
