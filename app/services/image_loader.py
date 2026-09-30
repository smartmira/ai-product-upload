import requests
import tempfile


def download_temp_image(image_url):

    response = requests.get(image_url)

    response.raise_for_status()

    tmp = tempfile.NamedTemporaryFile(
        suffix=".jpg",
        delete=False
    )

    tmp.write(response.content)

    tmp.close()

    return tmp.name