import logging
import os
import re
import socket
from pathlib import Path
from urllib.parse import urlparse

import requests
import urllib3.exceptions
from bs4 import BeautifulSoup

TAGS_ATTRIBUTES = {
    'img': 'src',
    'script': 'src',
    'link': 'href',
}

log = logging.getLogger(__name__)


def get_new_link_format(url):
    preparation = urlparse(url)
    new_link = re.sub(r'\W', '-', f'{preparation.netloc}{preparation.path}')
    return new_link


def create_folder(url, path):
    if requests.get(url).status_code == 200:
        string = get_new_link_format(url)
        folder_name = f'{string}_files'
        full_path = os.path.join(path, folder_name)

        if not os.path.isdir(full_path):
            try:
                os.mkdir(full_path)
            except IOError:
                log.error(f'Failed to create folder {folder_name}')
                raise

        return folder_name


def save_to_file(path_to_file, data):
    try:
        if isinstance(data, bytes):
            with open(path_to_file, 'wb') as file_name:
                file_name.write(data)

        else:
            with open(path_to_file, 'w', encoding='utf-8') as file_name:
                file_name.write(data)

    except PermissionError:
        log.error(f'Permission denied to the specified directory '
                  f'{path_to_file}')
        raise


def get_content(url):
    try:
        response = requests.get(url)
        response.raise_for_status()

    except requests.exceptions.HTTPError:
        log.error(f'Failed to establish a connection to site: {url}\n'
                  f'Check the correctness of the entered link!')
        raise requests.exceptions.HTTPError('An HTTP error occurred.')
    except requests.exceptions.SSLError:
        log.error(f'Failed to establish a connection to site: {url}\n'
                  f'Check the correctness of the entered link!')
        raise requests.exceptions.SSLError('An SSL error occurred.')
    except requests.exceptions.ConnectionError:
        log.error(f'Failed to establish a connection to site: {url}\n'
                  f'Check the correctness of the entered link!')
        raise requests.exceptions.ConnectionError(
            'A Connection error occurred.')
    except requests.RequestException:
        log.error(f'Failed to establish a connection to site: {url}\n'
                  f'Check the correctness of the entered link!')
        raise
    except urllib3.util.ssl_:
        log.error(f'Failed to establish a connection to site: {url}\n'
                  f'Check the correctness of the entered link!')
        raise
    except urllib3.exceptions.MaxRetryError:
        log.error(f'Failed to establish a connection to site: {url}\n'
                  f'Check the correctness of the entered link!')
        raise urllib3.exceptions.MaxRetryError('Max retries exceeded with url')
    except urllib3.exceptions.NewConnectionError:
        log.error(f'Failed to establish a connection to site: {url}\n'
                  f'Check the correctness of the entered link!')
        raise urllib3.exceptions.NewConnectionError('Fail to establish '
                                                    'a new connection.')
    except urllib3.exceptions.HTTPError:
        log.error(f'Failed to establish a connection to site: {url}\n'
                  f'Check the correctness of the entered link!')
        raise urllib3.exceptions.HTTPError('An HTTP error occurred.')
    except socket.gaierror:
        log.error(f'Failed to establish a connection to site: {url}\n'
                  f'Check the correctness of the entered link! ')
        raise socket.gaierror('Failed to execute script')
    else:
        return response.content


def get_html_file(url, path):
    response = get_content(url)

    if response:
        new_link = get_new_link_format(url)
        file_name = f'{new_link}.html'
        path_to_file = os.path.join(path, file_name)
        save_to_file(path_to_file, response)

        return path_to_file


def get_soup(url):
    response = get_content(url)
    return BeautifulSoup(response, 'html.parser')


def change_links(url, path):
    path_to_file = get_html_file(url, path)
    preparation = urlparse(url)
    domain_name = get_new_link_format(preparation.netloc)
    urls = f'{preparation.scheme}://{preparation.netloc}'
    folder_name = create_folder(url, path)

    def get_link_to_file(search_tag, attribute):

        tags = soup.find_all(search_tag)

        for tag in tags:
            file_name = f'{os.path.basename(tag[attribute])}'
            paths = os.path.dirname(tag[attribute])
            extension = Path(f'{urls}{tag[attribute]}').suffix
            result = re.search(r'.\D{2,4}$', extension)
            if not tag[attribute].startswith('http'):

                if result:
                    tag[attribute] = os.path.join(
                        folder_name,
                        f'{domain_name}'
                        f'{get_new_link_format(paths)}-'
                        f'{file_name}')
                else:
                    tag[attribute] = os.path.join(
                        folder_name,
                        f'{domain_name}'
                        f'{get_new_link_format(paths)}-'
                        f'{file_name}.html')

            if tag[attribute].startswith('http') \
                    and urlparse(url).netloc == urlparse(tag[attribute]).netloc:
                if result:
                    tag[attribute] = os.path.join(
                        folder_name,
                        f'{get_new_link_format(paths)}-'
                        f'{file_name}')
                else:
                    tag[attribute] = os.path.join(
                        folder_name,
                        f'{domain_name}'
                        f'{get_new_link_format(paths)}'
                        f'{file_name}.html')

    soup = get_soup(url)

    for tag_name, attr in TAGS_ATTRIBUTES.items():
        get_link_to_file(tag_name, attr)

    save_to_file(path_to_file, soup.prettify(formatter='minimal'))


def download_content(url, path):
    folder_name = create_folder(url, path)
    preparation = urlparse(url)
    domain_name = get_new_link_format(preparation.netloc)
    urls = f'{preparation.scheme}://{preparation.netloc}'

    def get_link_to_file(search_tag, attribute):

        tags = soup.find_all(search_tag)

        for tag in tags:
            file_name = f'{os.path.basename(tag[attribute])}'
            paths = os.path.dirname(tag[attribute])
            extension = Path(f'{urls}{tag[attribute]}').suffix
            result = re.search(r'.\D{2,4}$', extension)
            if not tag[attribute].startswith('http'):
                if result:
                    print(os.path.join(path, folder_name,
                                       f'{domain_name}'
                                       f'{get_new_link_format(paths)}-'
                                       f'{file_name}'))
                    save_to_file(os.path.join(path, folder_name,
                                              f'{domain_name}'
                                              f'{get_new_link_format(paths)}-'
                                              f'{file_name}'),
                                 get_content(f'{urls}{tag[attribute]}'))
                else:
                    print(os.path.join(
                        path, folder_name,
                        f'{domain_name}'
                        f'{get_new_link_format(paths)}'
                        f'{get_new_link_format(tag[attribute])}.html'
                    ))
                    save_to_file(os.path.join(
                        path, folder_name,
                        f'{domain_name}'
                        f'{get_new_link_format(paths)}'
                        f'{get_new_link_format(tag[attribute])}.html'
                    ),
                        get_content(f'{urls}{tag[attribute]}'))

            if tag[attribute].startswith('http') \
                    and urlparse(url).netloc == urlparse(tag[attribute]).netloc:
                if result:
                    save_to_file(os.path.join(path, folder_name,
                                              f'{get_new_link_format(paths)}'
                                              f'{file_name}'),
                                 get_content(tag[attribute]))
                else:
                    save_to_file(os.path.join(
                        path, folder_name,
                        f'{domain_name}'
                        f'{get_new_link_format(paths)}'
                        f'{get_new_link_format(tag[attribute])}.html'
                    ),
                        get_content(tag[attribute]))

    soup = get_soup(url)

    for tag_name, attr in TAGS_ATTRIBUTES.items():
        get_link_to_file(tag_name, attr)
    # tags_src = soup.find_all(TAGS_ATTRIBUTES.keys(), {'src': True})
    # tags_href = soup.find_all(TAGS_ATTRIBUTES.keys(), {'href': True})
    #
    # for tag in tags_src:
    #     file_name = f'{os.path.basename(tag["src"])}'
    #     paths = os.path.dirname(tag['src'])
    #     extension = Path(f'{urls}{tag["src"]}').suffix
    #     result = re.search(r'.\D{2,4}$', extension)
    #     if not tag['src'].startswith('http'):
    #         if result:
    #             save_to_file(os.path.join(path, folder_name,
    #                                       f'{domain_name}'
    #                                       f'{get_new_link_format(paths)}-'
    #                                       f'{file_name}'),
    #                          get_content(f'{urls}{tag["src"]}'))
    #         else:
    #             save_to_file(os.path.join(
    #                 path, folder_name,
    #                 f'{domain_name}'
    #                 f'{get_new_link_format(paths)}'
    #                 f'{get_new_link_format(tag["src"])}.html'
    #             ),
    #                 get_content(f'{urls}{tag["src"]}'))
    #
    #     if tag['src'].startswith('http') \
    #             and urlparse(url).netloc == urlparse(tag['src']).netloc:
    #         if result:
    #             save_to_file(os.path.join(path, folder_name,
    #                                       f'{get_new_link_format(paths)}-'
    #                                       f'{file_name}'),
    #                          get_content(tag["src"]))
    #         else:
    #             save_to_file(os.path.join(
    #                 path, folder_name,
    #                 f'{domain_name}'
    #                 f'{get_new_link_format(paths)}'
    #                 f'{get_new_link_format(tag["src"])}.html'
    #             ),
    #                 get_content(tag["src"]))
    #
    # for tag_ in tags_href:
    #     file_name = f'{os.path.basename(tag_["href"])}'
    #
    #     paths = os.path.dirname(tag_['href'])
    #     extension = Path(f'{urls}{tag_["href"]}').suffix
    #     result = re.search(r'.\D{2,4}$', extension)
    #     if not tag_['href'].startswith('http'):
    #         if result:
    #             save_to_file(os.path.join(path, folder_name,
    #                                       f'{domain_name}'
    #                                       f'{get_new_link_format(paths)}-'
    #                                       f'{file_name}'),
    #                          get_content(f'{urls}{tag_["href"]}'))
    #         else:
    #             save_to_file(os.path.join(
    #                 path, folder_name,
    #                 f'{domain_name}'
    #                 f'{get_new_link_format(tag_["href"])}.html'
    #             ),
    #                 get_content(f'{urls}{tag_["href"]}'))
    #
    #     if tag_['href'].startswith('http') \
    #             and urlparse(url).netloc == urlparse(tag_['href']).netloc:
    #
    #         if result:
    #             save_to_file(os.path.join(path, folder_name,
    #                                       f'{get_new_link_format(paths)}-'
    #                                       f'{file_name}'),
    #                          get_content(tag_["href"]))
    #         else:
    #             save_to_file(os.path.join(
    #                 path, folder_name,
    #                 f'{domain_name}'
    #                 f'{get_new_link_format(paths)}'
    #                 f'{get_new_link_format(tag_["href"])}.html'
    #             ),
    #                 get_content(tag_['href']))
