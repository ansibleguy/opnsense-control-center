from re import match as regex_match
from re import compile as regex_compile
from json import loads as json_loads
from json import JSONDecodeError
from urllib import request
from hashlib import sha256


class FilterModule(object):
    def filters(self):
        return {
            "nftables_format_list": self.nftables_format_list,
            "ensure_list": self.ensure_list,
            "valid_hostname": self.valid_hostname,
            "github_latest_release": self.github_latest_release,
            "sha256sum": self.sha256sum,
        }

    @staticmethod
    def sha256sum(text: str) -> str:
        return sha256(text.encode('utf-8')).hexdigest()

    @staticmethod
    def github_latest_release(user: str, repo: str) -> str:
        with request.urlopen(f"https://api.github.com/repos/{user}/{repo}/releases/latest") as response:
            try:
                return json_loads(response.read())['name'].replace('v', '')

            except (KeyError, JSONDecodeError):
                return ''

    @staticmethod
    def _valid_domain(name: str) -> bool:
        # see: https://validators.readthedocs.io/en/latest/_modules/validators/domain.html
        domain = regex_compile(
            r'^(([a-zA-Z]{1})|([a-zA-Z]{1}[a-zA-Z]{1})|'
            r'([a-zA-Z]{1}[0-9]{1})|([0-9]{1}[a-zA-Z]{1})|'
            r'([a-zA-Z0-9][-_.a-zA-Z0-9]{0,61}[a-zA-Z0-9]))\.'
            r'([a-zA-Z]{2,13}|[a-zA-Z0-9-]{2,30}.[a-zA-Z]{2,3})$'
        )
        return domain.match(name) is not None

    @classmethod
    def valid_hostname(cls, name: str) -> bool:
        # see: https://en.wikipedia.org/wiki/Hostname#Restrictions_on_valid_host_names
        expr_hostname = r'^[a-zA-Z0-9-\.]{1,253}$'
        valid_hostname = regex_match(expr_hostname, name) is not None
        return all([cls._valid_domain(name), valid_hostname])

    @staticmethod
    def ensure_list(data: (str, list)) -> list:
        if isinstance(data, list):
            return data

        return [data]

    @classmethod
    def nftables_format_list(cls, data: list) -> str:
        return f"{{ {', '.join(map(str, cls.ensure_list(data)))} }}"
