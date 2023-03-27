import re
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile as imuf
from PIL import Image
from django.conf import settings


def title_from_filename(filename, is_landscape=True):
    import re

    title = filename
    title = title.replace('fifdee_', '').replace('_', ' ').replace('.jpg', '')
    r = re.findall(r'[abcdef1234567890-]{36}', title)
    if len(r) > 0:
        to_delete = r[0]
        title = title.replace(to_delete, '')

    if 'wallpaper' not in title:
        title += ' wallpaper'

    if not is_landscape:
        if 'mobile' not in title:
            title = title.replace('wallpaper', 'mobile wallpaper')

    return title


def get_image_tags(image_url):
    from azure.cognitiveservices.vision.computervision import ComputerVisionClient
    from msrest.authentication import CognitiveServicesCredentials
    subscription_key = settings.IMAGE_CAPTIONING_KEY
    endpoint = settings.IMAGE_CAPTIONING_ENDPOINT

    computervision_client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(subscription_key))
    try:
        # result = computervision_client.describe_image(image_url)
        # return {'tags': result.tags, 'title': result.captions[0].text}

        tags_result_remote = computervision_client.tag_image(image_url)
        if len(tags_result_remote.tags) == 0:
            return None
        else:
            return [tag.name for tag in tags_result_remote.tags]

    except Exception as e:
        print(f'captioning exception: {e}')

    return None


def get_description_from_keywords(tags_as_string_comma_sep):
    import openai
    openai.api_key = settings.OPENAI_KEY
    prompt = f'Write a mobile wallpaper description based on following keywords: {tags_as_string_comma_sep}'

    r = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt,
        max_tokens=350,
        temperature=0
    )

    try:
        description = r['choices'][0]['text']
        return description
    except Exception as e:
        print(f'OPEN AI EXCEPTION: {e}')
        return None


def compress_image_return_with_thumbnail(input_image):
    thumbnail_size = 512, 512

    with Image.open(input_image) as img:
        # Convert to RGB as RGBA can not be changed into JPEG(no transparency)
        img = img.convert('RGB')
        filename = input_image.name.split('.')[0]
        outio = BytesIO()
        img.save(outio, format='JPEG', quality=75)

        img.thumbnail(thumbnail_size)
        outio_thumb = BytesIO()
        img.save(outio_thumb, format='JPEG', quality=75)

        output_image = imuf(outio, 'ImageField', f"{filename}.jpg", 'image/jpeg', outio.tell(), None)
        output_image_thumb = imuf(outio_thumb, 'ImageField', f"{filename}_thumb.jpg", 'image/jpeg', outio_thumb.tell(),
                                  None)

        return output_image, output_image_thumb


def unique_slugify(instance, value, slug_field_name='slug', queryset=None,
                   slug_separator='-'):
    """
    Calculates and stores a unique slug of ``value`` for an instance.

    ``slug_field_name`` should be a string matching the name of the field to
    store the slug in (and the field to check against for uniqueness).

    ``queryset`` usually doesn't need to be explicitly provided - it'll default
    to using the ``.all()`` queryset from the model's default manager.
    """
    slug_field = instance._meta.get_field(slug_field_name)

    slug = getattr(instance, slug_field.attname)
    slug_len = slug_field.max_length

    # Sort out the initial slug, limiting its length if necessary.
    from django.utils.text import slugify
    slug = slugify(value)
    if slug_len:
        slug = slug[:slug_len]
    slug = _slug_strip(slug, slug_separator)
    original_slug = slug

    # Create the queryset if one wasn't explicitly provided and exclude the
    # current instance from the queryset.
    if queryset is None:
        queryset = instance.__class__._default_manager.all()
    if instance.pk:
        queryset = queryset.exclude(pk=instance.pk)

    # Find a unique slug. If one matches, at '-2' to the end and try again
    # (then '-3', etc).
    next = 2
    while not slug or queryset.filter(**{slug_field_name: slug}):
        slug = original_slug
        end = '%s%s' % (slug_separator, next)
        if slug_len and len(slug) + len(end) > slug_len:
            slug = slug[:slug_len - len(end)]
            slug = _slug_strip(slug, slug_separator)
        slug = '%s%s' % (slug, end)
        next += 1

    setattr(instance, slug_field.attname, slug)


def _slug_strip(value, separator='-'):
    """
    Cleans up a slug by removing slug separator characters that occur at the
    beginning or end of a slug.

    If an alternate separator is used, it will also replace any instances of
    the default '-' separator with the new separator.
    """
    separator = separator or ''
    if separator == '-' or not separator:
        re_sep = '-'
    else:
        re_sep = '(?:-|%s)' % re.escape(separator)
    # Remove multiple instances and if an alternate separator is provided,
    # replace the default '-' separator.
    if separator != re_sep:
        value = re.sub('%s+' % re_sep, separator, value)
    # Remove separator from the beginning and end of the slug.
    if separator:
        if separator != '-':
            re_sep = re.escape(separator)
        value = re.sub(r'^%s+|%s+$' % (re_sep, re_sep), '', value)
    return value
