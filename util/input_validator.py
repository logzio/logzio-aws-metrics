"""
This module is for validating user's input
"""
import re
from util.data import aws_namespaces, aws_regions


# is_valid_logzio_token checks if a given token is a valid logz.io token
def is_valid_logzio_token(token):
    if type(token) is not str:
        raise TypeError("Token should be a string")
    regex = r"\b[a-zA-Z]{32}\b"
    match_obj = re.search(regex, token)
    if match_obj is not None and match_obj.group() is not None:
        if any(char.islower() for char in token) and any(char.isupper() for char in token):
            return True
    raise ValueError("Invalid token: {}".format(token))


# is_valid_logzio_region_code checks that a the region code is a valid logzio region code.
# an empty string ("") is also acceptable
def is_valid_logzio_region_code(logzio_region_code):
    if logzio_region_code is None or type(logzio_region_code) is not str:
        raise TypeError("Logzio region code should be a string")
    valid_logzio_regions = ["au", "ca", "eu", "nl", "uk", "us", "wa"]
    if logzio_region_code != "":
        if logzio_region_code not in valid_logzio_regions:
            raise ValueError("invalid logzio region code: {}. cannot start monitoring".format(logzio_region_code))
    return True


def is_valid_logz_io_modules(modules, suported_modules):
    if modules is None or type(modules) is not str:
        raise TypeError("Logzio modules parameter should be a string")
    logz_io_modules = modules.replace(' ', '').split(',')
    for module in logz_io_modules:
        if module not in suported_modules:
            raise ValueError(f'{module} module is not supported')
    return logz_io_modules


def is_valid_scrape_interval(interval):
    if (interval % 60) != 0:
        raise ValueError('Scrape interval should be in multiplies of 60')


def is_valid_aws_region(aws_region):
    if aws_region is None or type(aws_region) is not str:
        raise TypeError("AWS region parameter should be a string")
    if aws_region not in aws_regions:
        raise ValueError(f'{aws_region} is not supported')


def is_valid_aws_namespaces(namespaces):
    if namespaces is None or type(namespaces) is not str:
        raise TypeError("AWS namespaces parameter should be a string")
    try:
        aws_namespaces_list = namespaces.replace(' ', '').split(',')
        for n in aws_namespaces_list:
            if n not in aws_namespaces:
                raise ValueError(f'{n} namespace is not supported')
    except KeyError:
        raise KeyError(f'Could not find aws services: {KeyError}')
    return aws_namespaces_list

