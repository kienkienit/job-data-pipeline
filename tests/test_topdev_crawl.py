"""Unit tests for TopDev crawl mappers (no live network)."""

from src.crawl.topdev import format_address, format_salary, map_job_to_row


def test_format_salary_negotiable_with_estimate():
    text = format_salary(
        {
            "is_negotiable": 1,
            "min_estimate": 40_000_000,
            "max_estimate": 60_000_000,
            "currency_estimate": "VND",
        }
    )
    assert text == "40 - 60 triệu"


def test_format_salary_pure_negotiable():
    assert format_salary({"is_negotiable": 1, "min_estimate": 0, "max_estimate": 0}) == (
        "Thoả thuận"
    )


def test_format_address_sort_addresses():
    assert format_address({"sort_addresses": "Quận Hà Đông, Hà Nội"}) == (
        "Hà Nội: Quận Hà Đông"
    )


def test_format_address_city_only():
    assert (
        format_address(
            {
                "sort_addresses": "Hồ Chí Minh",
                "address_region_list": "Thành phố Hồ Chí Minh",
            }
        )
        == "Hồ Chí Minh"
    )


def test_map_job_to_row():
    job = {
        "id": 1,
        "title": "Data Engineer",
        "detail_url": "https://topdev.vn/detail-jobs/x-1",
        "company": {"display_name": "ACME"},
        "salary": {
            "is_negotiable": 0,
            "min": 1000,
            "max": 2000,
            "currency": "USD",
        },
        "addresses": {"sort_addresses": "Quận 1, Hồ Chí Minh"},
        "refreshed": {"date": "24-09-2026", "since": "1 day ago"},
        "closed": {"since": "in 2 weeks"},
        "skills_str": "Python, SQL",
    }
    row = map_job_to_row(job)
    assert row["job_title"] == "Data Engineer"
    assert row["company"] == "ACME"
    assert row["salary"] == "1000 - 2000 USD"
    assert row["address"] == "Hồ Chí Minh: Quận 1"
    assert row["created_date"] == "2026-09-24"
    assert row["link_description"].endswith("-1")
    assert row["source_id"] == 1
