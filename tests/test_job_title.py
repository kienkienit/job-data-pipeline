"""Unit tests for job title normalization."""

from src.transform.job_title import normalize_job_title


def test_empty():
    assert normalize_job_title(None) == "Other"
    assert normalize_job_title("") == "Other"


def test_software_engineer_variants():
    assert normalize_job_title(".Net Developer (N3) | T9160") == "Software Engineer"
    assert normalize_job_title("Nhân Viên Lập Trình Phần Mềm") == "Software Engineer"
    assert normalize_job_title("Senior Fullstack Developer (Nodejs & React)") == (
        "Software Engineer"
    )
    assert normalize_job_title("Java Developer Từ 3 Năm Kinh Nghiệm") == (
        "Software Engineer"
    )


def test_business_analyst():
    assert normalize_job_title("Business Analyst") == "Business Analyst"
    assert (
        normalize_job_title("Chuyên Viên Phân Tích Nghiệp Vụ (Business Analyst)")
        == "Business Analyst"
    )


def test_project_manager():
    assert normalize_job_title("Project Manager") == "Project Manager"
    assert normalize_job_title("Product Owner") == "Project Manager"


def test_qa_tester():
    assert normalize_job_title("Manual Tester") == "QA / Tester"
    assert normalize_job_title("Nhân Viên Kiểm Thử Phần Mềm") == "QA / Tester"
    assert normalize_job_title("QA Engineer") == "QA / Tester"


def test_data_ai():
    assert normalize_job_title("AI Engineer") == "Data / AI"
    assert normalize_job_title("Data Analyst") == "Data / AI"


def test_devops():
    assert normalize_job_title("Devops Engineer") == "DevOps / Infra"
    assert normalize_job_title("IT Helpdesk") == "DevOps / Infra"


def test_design():
    assert normalize_job_title("UI/UX Designer") == "Design"


def test_brse():
    assert normalize_job_title("Brse Engineer (2+ Năm Kinh Nghiệm)") == "BrSE / Comtor"


def test_other():
    assert normalize_job_title("Nhân viên hành chính") == "Other"
    assert normalize_job_title("Nhân Viên Digtal Marketing") == "Other"


def test_word_boundary_ba_not_in_backend():
    assert normalize_job_title("BA") == "Business Analyst"
    assert normalize_job_title("Backend Developer") == "Software Engineer"
