import http
import logging
import logging.handlers
import re
from enum import Enum
from http import HTTPStatus
from pathlib import Path
from typing import Optional

import requests
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from requests import PreparedRequest
from requests.auth import AuthBase, HTTPBasicAuth

logger = logging.getLogger()

MEBIBYTE = 1024**2


class BearerAuth(AuthBase):
    def __init__(self, api_key: str) -> None:
        self.api_key = api_key

    def __call__(self, r: PreparedRequest) -> PreparedRequest:
        r.headers["Authorization"] = f"Bearer {self.api_key}"
        return r


class DnsRecordType(Enum):
    SOA = "SOA"
    NS = "NS"
    A = "A"


class ModemConfig(BaseModel):
    url: str = ""
    username: str = ""
    password: str = ""
    wan_ip_matcher: str = ""


class DnsConfig(BaseModel):
    url_template: str = ""
    domain: str = ""
    api_key: str = ""
    subdomains: set[str] = Field(default_factory=lambda: {"@", "www"})


class DnsRecord(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    type: DnsRecordType
    data: str

    class Config:
        frozen = True


class Persistence(BaseModel):
    previous_wan_ip_address_file: Path = Field(default_factory=Path)


class LoggingConfig(BaseModel):
    level: int | str = logging.INFO
    path: Path = Field(default_factory=Path)
    max_bytes: int = 20 * MEBIBYTE
    backup_count: int = 3


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="Home_Automation/scripts/ddns/.env",
        env_nested_delimiter="__",
    )

    modem: ModemConfig = ModemConfig()
    dns: DnsConfig = DnsConfig()
    persistence: Persistence = Persistence()
    logging: LoggingConfig = LoggingConfig()


config = Settings()


def get_modem_status_page(url: str, username: str, password: str) -> str | None:
    response = requests.get(url, auth=HTTPBasicAuth(username=username, password=password))

    if response.status_code == HTTPStatus.OK:
        logger.debug("Modem status page successfully retrieved")
    else:
        logger.error("Failed to retrieve modem status page")

    return response.text if response.status_code == HTTPStatus.OK else None


def get_wan_ip_from_status_page(status_page: str | None, matcher: str) -> str | None:
    return re.search(matcher, status_page).group("ip") if isinstance(status_page, str) else None


def get_current_wan_id_address(modem_config: ModemConfig) -> str | None:
    status_page = get_modem_status_page(
        url=modem_config.url,
        username=modem_config.username,
        password=modem_config.password,
    )
    current_wan_id_address = get_wan_ip_from_status_page(status_page=status_page, matcher=modem_config.wan_ip_matcher)
    logger.debug(f"Current WAN IP retrieved: {current_wan_id_address}")

    return current_wan_id_address


def make_sure_previous_wan_id_address_file_exists(previous_wan_ip_address_file: Path) -> None:
    if not previous_wan_ip_address_file.exists():
        previous_wan_ip_address_file.touch()


def get_previous_wan_id_address(previous_wan_ip_address_file: Path) -> str | None:
    make_sure_previous_wan_id_address_file_exists(previous_wan_ip_address_file=previous_wan_ip_address_file)
    candidate = previous_wan_ip_address_file.read_text()

    previous_wan_ip_address = candidate if len(candidate) > 0 else None
    logger.debug(f"Previous WAN IP retrieved: {previous_wan_ip_address}")

    return previous_wan_ip_address


def update_previous_wan_ip_address(ip_address: str, previous_wan_ip_address_file: Path) -> None:
    previous_wan_ip_address_file.write_text(ip_address)

    logger.debug(f"Previous WAN IP successfully updated ({ip_address})")


def get_dns_record_base_url(url_template: str, domain: str) -> str:
    return url_template.format(domain=domain)


def get_dns_records(base_url: str, api_key: str) -> set[DnsRecord]:
    response = requests.get(base_url, auth=BearerAuth(api_key=api_key))

    return {DnsRecord(**record) for record in response.json()["domain_records"]}


def filter_dns_subdomain_records(records: set[DnsRecord], subdomains: set[str]) -> set[DnsRecord]:
    return {record for record in records if (record.type is DnsRecordType.A) and (record.name in subdomains)}


def get_updated_dns_records(records: set[DnsRecord], data: str) -> set[DnsRecord]:
    new_records = set()
    for record in records:
        candidate = DnsRecord(**(record.model_dump() | {"data": data}))
        new_records.add(candidate)

    return new_records


def get_new_dns_records(ip_address: str, subdomains: set[str]) -> set[DnsRecord]:
    return {
        DnsRecord(
            name=name,
            type=DnsRecordType.A,
            data=ip_address,
        )
        for name in subdomains
    }


def record_to_dto(record: DnsRecord) -> dict[str, str]:
    return {"name": record.name, "type": record.type.name, "data": record.data}


def create_dns_records(base_url: str, ip_address: str, subdomains: set[str], api_key: str) -> None:
    for record in get_new_dns_records(ip_address=ip_address, subdomains=subdomains):
        response = requests.post(base_url, json=record_to_dto(record=record), auth=BearerAuth(api_key=api_key))

        if response.status_code == http.HTTPStatus.OK:
            logger.info(
                f"Successfully created new DNS record for subdomain: {record.name} (new IP address: {ip_address})",
            )
        else:
            message = f"Failed to created new DNS record for subdomain: {record.name}"
            logger.error(message)
            raise RuntimeError(message)


def update_dns_records(base_url: str, records: set[DnsRecord], data: str, api_key: str) -> None:
    for record in get_updated_dns_records(records=records, data=data):
        response = requests.put(
            f"{base_url}/{record.id}",
            json=record_to_dto(record=record),
            auth=BearerAuth(api_key=api_key),
        )

        if response.status_code == http.HTTPStatus.OK:
            logger.info(f"Successfully updated DNS record for subdomain: {record.name} (new IP address: {data})")
        else:
            message = f"Failed to update DNS record for subdomain: {record.name}"
            logger.error(message)
            raise RuntimeError(message)


def add_file_handler(logging_config: LoggingConfig, level: int | str, formatter: logging.Formatter) -> None:
    handler = logging.handlers.RotatingFileHandler(
        logging_config.path,
        maxBytes=logging_config.max_bytes,
        backupCount=logging_config.backup_count,
    )
    handler.setFormatter(formatter)
    handler.setLevel(level)
    logger.addHandler(handler)


def add_stdout_stream_handler(level: int | str, formatter: logging.Formatter) -> None:
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    handler.setLevel(level)
    logger.addHandler(handler)


def log_setup(logger: logging.Logger, logging_config: LoggingConfig) -> None:
    formatter = logging.Formatter("%(asctime)s|%(levelname)s|%(message)s", "%Y-%m-%dT%H:%M:%S%z")
    level = logging_config.level

    add_stdout_stream_handler(level=level, formatter=formatter)

    if isinstance(logging_config.path, Path):
        add_file_handler(logging_config=logging_config, level=level, formatter=formatter)

    logger.setLevel(level)


if __name__ == "__main__":
    log_setup(logger=logger, logging_config=config.logging)
    previous_wan_ip_address = get_previous_wan_id_address(
        previous_wan_ip_address_file=config.persistence.previous_wan_ip_address_file,
    )
    current_wan_ip_address = get_current_wan_id_address(modem_config=config.modem)
    if previous_wan_ip_address != current_wan_ip_address:
        dns_record_base_url = get_dns_record_base_url(url_template=config.dns.url_template, domain=config.dns.domain)
        current_dns_records = get_dns_records(base_url=dns_record_base_url, api_key=config.dns.api_key)
        current_dns_a_records = filter_dns_subdomain_records(
            records=current_dns_records,
            subdomains=config.dns.subdomains,
        )

        wan_ip_address_set = next(iter(current_dns_a_records)).data
        try:
            if previous_wan_ip_address is None:
                if len(current_dns_a_records) == 0:
                    create_dns_records(
                        base_url=dns_record_base_url,
                        ip_address=current_wan_ip_address,
                        subdomains=config.dns.subdomains,
                        api_key=config.dns.api_key,
                    )
                    wan_ip_address_set = current_wan_ip_address
            else:
                update_dns_records(
                    base_url=dns_record_base_url,
                    records=current_dns_a_records,
                    data=current_wan_ip_address,
                    api_key=config.dns.api_key,
                )
                wan_ip_address_set = current_wan_ip_address
        except RuntimeError:
            logger.error("DNS records remained unchanged.")
        else:
            logger.info("DNS records successfully changed.")

        update_previous_wan_ip_address(
            ip_address=wan_ip_address_set,
            previous_wan_ip_address_file=config.persistence.previous_wan_ip_address_file,
        )
    else:
        logger.info("DNS records unchanged.")
