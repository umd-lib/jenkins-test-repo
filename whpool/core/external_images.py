
import html
import logging
import math

from collections import defaultdict
from itertools import filterfalse
from mailbox import Mailbox, mboxMessage
from whpool.core.message_file import MessageFile
from whpool.core.external_image_file import ExternalImageFile
from typing import Dict, List, Set

from bs4 import BeautifulSoup  # type: ignore

import requests

logger = logging.getLogger(__name__)


class ExternalImages:
    def __init__(self,
                 external_image_srcs_set: Set[str],  # The Set of all srcs (including non-retrievable srcs)
                 message_ids_to_srcs: Dict[str, List[str]],  # Mapping of message ids to list of srcs
                 external_image_files: Dict[str, ExternalImageFile]  # Mapping of src to ExternalImageFile
                 ):
        self.external_image_srcs_set = external_image_srcs_set
        self.message_ids_to_srcs = message_ids_to_srcs
        self.external_image_files = external_image_files

    def srcs(self, msg_id: str) -> List[str]:
        '''
        Returns the list of "src" entries for the given message id, or an
        empty list if message id has no files.
        '''
        return self.message_ids_to_srcs.get(msg_id, [])

    def get_file(self, src: str) -> ExternalImageFile:
        '''
        Returns the ExternalImageFile associated with the given src
        '''
        return self.external_image_files[src]


class ExternalImagesFactory:
    FILE_EXTENSIONS = {
        'image/png': 'png',
        'image/gif': 'gif',
        'image/jpeg': 'jpg'
    }

    UNKNOWN_FILE_EXTENSION = 'unknown'

    def __init__(self) -> None:
        # Set of unique "src" fields from all image tags
        self.external_image_srcs_set: Set[str] = set()

        # Dictonary of message ids to images "srcs" it contains
        self.message_ids_to_srcs: Dict[str, List[str]] = defaultdict(list)

        # List of failed retrievals
        self.failed_src_retrievals: List[str] = []

        # Dictionary of "src" to ExternalImageFile
        self.external_image_files: Dict[str, ExternalImageFile] = {}

    @staticmethod
    def create_filename(image_index: int, num_images: int, content_type: str) -> str:
        zero_padding = f"0{math.ceil(math.log10(num_images))}"

        base_filename = f"external_img{image_index:{zero_padding}}"
        file_extension = ExternalImagesFactory.FILE_EXTENSIONS.get(
            content_type.lower(), ExternalImagesFactory.UNKNOWN_FILE_EXTENSION)

        filename = f"{base_filename}.{file_extension}"
        return filename

    def add(self, message_id: str, src: str) -> None:
        self.external_image_srcs_set.add(src)

        srcs_list = self.message_ids_to_srcs[message_id]
        srcs_list.append(src)

    def retrieve(self) -> None:
        # Retrieve images
        num_images = len(self.external_image_srcs_set)
        for image_index, src in enumerate(self.external_image_srcs_set):
            logger.debug(f"Retrieving '{src}'")
            src = src

            response = requests.get(src, stream=True)

            if response.ok:
                logger.debug(f"Successfully Retrieved '{src}'.")

                content_type = ""
                try:
                    content_type = response.headers['Content-Type']
                    logger.debug(f"Content-Type={content_type}")
                except KeyError:
                    logger.warn(f"Response for '{src}' did not contain a Content-Type header")

                filename = ExternalImagesFactory.create_filename(image_index, num_images, content_type)
                logger.debug(f"Storing as {filename}")

                bytes = response.raw.data
                external_image_file = ExternalImageFile(src, filename, bytes)
                self.external_image_files[src] = external_image_file
            else:
                logger.warn(f"FAILED to retrieve '{src}'. response={response}")
                self.failed_src_retrievals.append(src)

    def remove_failures(self) -> None:
        # Remove from message_ids_to_srcs any srcs that could not be
        # retrieved

        for msg_id in self.message_ids_to_srcs:
            srcs = self.message_ids_to_srcs[msg_id]

            temp = []
            for src in srcs:
                if src not in self.failed_src_retrievals:
                    temp.append(src)
                else:
                    logger.debug(f"Removing {src} from message {msg_id} as it could not be retrieved.")

            self.message_ids_to_srcs[msg_id] = temp

    def build(self) -> ExternalImages:
        self.retrieve()
        self.remove_failures()
        return ExternalImages(self.external_image_srcs_set, self.message_ids_to_srcs, self.external_image_files)


def retrieve_external_images(box: Mailbox[mboxMessage]) -> ExternalImages:
    logger.debug("Retrieving external images")

    externalImagesFactory = ExternalImagesFactory()

    for msg_id, message in box.iteritems():
        logger.debug(f'Processing message {msg_id} for external images')

        for part in message.walk():
            content_type = part.get_content_type()
            filename = part.get_filename()

            if content_type == 'text/html':
                # Assume this is the message body
                bytes = part.get_payload(decode=True)
                soup = BeautifulSoup(bytes, 'html.parser')
                img_tags = soup.find_all('img')
                for tag in img_tags:
                    try:
                        src = tag['src']
                    except KeyError:
                        logger.warn(f"In message {msg_id} could not find 'src' attribute in {tag}")
                        continue

                    if src.lower().startswith("http"):
                        logger.debug(f'Storing "img" tag for further processing, src={src}')
                        # Using HTML "escape" on the src attribute, because
                        # Beautiful Soup decodes the string, and we need the
                        # "escaped" version for matching against the HTML file
                        escaped_src = html.escape(src)
                        externalImagesFactory.add(msg_id, escaped_src)
                    elif src.lower().startswith("cid:"):
                        logger.debug(f'Skipping "img" tag -- starts with "cid:", src={src}."')
                    else:
                        logger.warn(f'Skipping "img" tag in message {msg_id} -- unknown protocol, src={src}."')

    external_images = externalImagesFactory.build()

    return external_images
