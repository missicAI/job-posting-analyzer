import json
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from pydantic import ValidationError

from joblens.extraction import JobPosting, extract_job, validate_grounding
from joblens.llm import LLMClient, LLMError

ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / ".env")
st.set_page_config(page_title="JobLens · JD Analyzer", page_icon="📋", layout="wide")
st.title("📋 JobLens — Đọc hiểu tin tuyển dụng")
st.caption("Trích xuất yêu cầu có dẫn chứng · Xuất JSON và bảng kỹ năng")
examples = json.loads((ROOT / "data/examples.json").read_text(encoding="utf-8"))
with st.sidebar:
    mode = st.radio("Cách chạy", ["Xem kết quả mẫu", "Phân tích bằng LLM"])
    st.caption("Chế độ mẫu chỉ đọc kết quả soạn sẵn, không gọi mô hình.")
    selected = st.selectbox(
        "Tin tuyển dụng mẫu", range(len(examples)), format_func=lambda i: examples[i]["name"]
    )
    client = LLMClient.from_env()
    st.caption(f"Mô hình khi chạy thật: {client.model}")
    st.caption("Cấu hình trong .env theo README.md.")
sample = examples[selected]
text = st.text_area("Nội dung tin tuyển dụng", sample["text"], height=270, key=f"posting_{selected}")
if st.button("Xem kết quả" if mode == "Xem kết quả mẫu" else "Phân tích", type="primary"):
    try:
        if mode == "Xem kết quả mẫu":
            if text != sample["text"]:
                raise ValueError("Bạn đã sửa nội dung. Chọn Phân tích bằng LLM để xử lý tin mới.")
            job = validate_grounding(JobPosting.model_validate(sample["expected"]), text)
            st.info("Kết quả mẫu soạn sẵn — đây không phải kết quả gọi LLM.")
        else:
            with st.spinner("Đang trích xuất và kiểm tra kết quả..."):
                job = extract_job(text, client)
        left, right = st.columns(2)
        with left:
            st.subheader(job.job_title or "Chưa có tên vị trí")
            for label, value in [
                ("Công ty", job.company),
                ("Địa điểm", job.location),
                ("Hình thức", job.work_mode),
                ("Kinh nghiệm", job.experience),
                ("Lương", job.salary),
            ]:
                st.write(f"**{label}:** {value or 'Chưa được cung cấp'}")
            rows = [
                {"Nhóm": group, "Kỹ năng": s.name, "Dẫn chứng": s.evidence}
                for group, skills in [("Bắt buộc", job.required_skills), ("Ưu tiên", job.preferred_skills)]
                for s in skills
            ]
            if rows:
                st.dataframe(rows, hide_index=True, width="stretch")
            else:
                st.info("Tin không nêu kỹ năng cụ thể.")
        with right:
            st.json(job.model_dump())
        st.download_button("Tải JSON", job.model_dump_json(indent=2), "job_analysis.json", "application/json")
    except (LLMError, ValidationError, ValueError) as exc:
        st.error(str(exc))
