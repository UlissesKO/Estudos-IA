"""MCP server for evidence-grounded resume optimization."""

from __future__ import annotations

import json
import re
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP


SERVER_ROOT = Path(__file__).resolve().parent
CONTENT_ROOT = SERVER_ROOT / "Fontes de conteúdo"
PROMPT_PATH = SERVER_ROOT / "PROMPT_OTIMIZADO.md"
KNOWLEDGE_PATH = CONTENT_ROOT / "conhecimentos.md"
JOB_PATH = CONTENT_ROOT / "descricao-vaga.md"
GENERAL_RESUME_PATH = CONTENT_ROOT / "Currículo Geral.html"
FINAL_RESUMES_ROOT = SERVER_ROOT / "Curriculos Finalizados"

mcp = FastMCP("resume-maker")

MANDATORY_PROMPT_INSTRUCTION = (
	"Leia e siga obrigatoriamente o arquivo PROMPT_OTIMIZADO.md antes de qualquer ação. "
	"Nunca execute uma operação sem consultar este prompt e obedecer suas instruções "
	"de forma prioritária."
)


class _HTMLTextExtractor(HTMLParser):
	"""Extract visible text without adding an HTML dependency."""

	def __init__(self) -> None:
		super().__init__()
		self.parts: list[str] = []
		self._ignored_depth = 0

	def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
		if tag.lower() in {"script", "style"}:
			self._ignored_depth += 1

	def handle_endtag(self, tag: str) -> None:
		if tag.lower() in {"script", "style"} and self._ignored_depth:
			self._ignored_depth -= 1

	def handle_data(self, data: str) -> None:
		if not self._ignored_depth:
			self.parts.append(data)


def _read_text(path: Path) -> str:
	if not path.exists():
		raise FileNotFoundError(f"Arquivo não encontrado: {path}")
	return path.read_text(encoding="utf-8-sig")


def _extract_html_text(html: str) -> str:
	parser = _HTMLTextExtractor()
	parser.feed(html)
	return " ".join(" ".join(parser.parts).split())


def _tokens(text: str) -> set[str]:
	return {
		token.lower()
		for token in re.findall(r"[A-Za-zÀ-ÿ][A-Za-zÀ-ÿ0-9+#./-]{2,}", text)
		if token.lower() not in {"com", "para", "uma", "dos", "das", "the", "and"}
	}


def _json(data: Any) -> str:
	return json.dumps(data, ensure_ascii=False, indent=2)


def _input_status() -> dict[str, Any]:
	job = _read_text(JOB_PATH).strip()
	knowledge = _read_text(KNOWLEDGE_PATH)
	general_resume = _read_text(GENERAL_RESUME_PATH)
	return {
		"mandatory_pre_action_instruction": MANDATORY_PROMPT_INSTRUCTION,
		"prompt_path": str(PROMPT_PATH),
		"job_description_present": len(job) > 0 and "Abaixo do título" not in job,
		"job_description_path": str(JOB_PATH),
		"knowledge_path": str(KNOWLEDGE_PATH),
		"general_resume_path": str(GENERAL_RESUME_PATH),
		"knowledge_characters": len(knowledge),
		"general_resume_characters": len(general_resume),
		"final_output_directory": str(FINAL_RESUMES_ROOT),
	}


def _assert_job_is_ready(job: str) -> None:
	if not job or "Abaixo do título" in job:
		raise ValueError(
			"descricao-vaga.md está vazio ou contém apenas o modelo. "
			"Cole uma descrição de vaga antes de executar a otimização."
		)


def _assert_candidate_html(candidate_html: str) -> None:
	lowered = candidate_html.lower()
	if "<html" not in lowered or "</html>" not in lowered:
		raise ValueError("O currículo candidato precisa ser um documento HTML completo.")
	if "<style" not in lowered or "</style>" not in lowered:
		raise ValueError("O currículo candidato precisa preservar a folha de estilos.")


@mcp.tool()
def get_resume_optimization_context() -> str:
	"""Return the vacancy, evidence base, and base resume for the AI agent."""
	job = _read_text(JOB_PATH).strip()
	knowledge = _read_text(KNOWLEDGE_PATH)
	general_resume = _read_text(GENERAL_RESUME_PATH)
	return _json(
		{
			"status": _input_status(),
			"mandatory_pre_action_instruction": MANDATORY_PROMPT_INSTRUCTION,
			"instructions": [
				"Leia o arquivo PROMPT_OTIMIZADO.md antes de qualquer ação e siga todas as suas instruções.",
				"Use only claims supported by conhecimentos.md.",
				"Preserve the HTML structure and CSS of the general resume.",
				"Keep qualifiers such as apoio, estudo, noções and POC.",
				"Do not optimize or save while the job description is empty.",
			],
			"job_description": job,
			"knowledge_base": knowledge,
			"general_resume_html": general_resume,
		}
	)


@mcp.tool()
def analyze_vacancy_match() -> str:
	"""Analyze vacancy terms against the evidence base and current resume."""
	job = _read_text(JOB_PATH).strip()
	_assert_job_is_ready(job)
	knowledge = _read_text(KNOWLEDGE_PATH)
	resume_text = _extract_html_text(_read_text(GENERAL_RESUME_PATH))
	job_tokens = _tokens(job)
	knowledge_tokens = _tokens(knowledge)
	resume_tokens = _tokens(resume_text)
	evidence_terms = sorted(job_tokens & knowledge_tokens)
	resume_terms = sorted(job_tokens & resume_tokens)
	missing_terms = sorted(job_tokens - resume_tokens - {"experiência", "profissional"})
	return _json(
		{
			"mandatory_pre_action_instruction": MANDATORY_PROMPT_INSTRUCTION,
			"job_terms_supported_by_knowledge": evidence_terms,
			"job_terms_already_in_general_resume": resume_terms,
			"job_terms_not_in_general_resume": missing_terms,
			"supported_term_coverage_percent": round(
				len(evidence_terms) / max(len(job_tokens), 1) * 100, 1
			),
			"guidance": "Use missing terms only when conhecimentos.md supports the underlying skill; otherwise do not add them.",
		}
	)


@mcp.tool()
def evaluate_resume(resume_html: str | None = None) -> str:
	"""Score a resume from recruiter and ATS perspectives using the current vacancy."""
	job = _read_text(JOB_PATH).strip()
	_assert_job_is_ready(job)
	html = resume_html or _read_text(GENERAL_RESUME_PATH)
	_assert_candidate_html(html)
	resume_text = _extract_html_text(html)
	job_tokens = _tokens(job)
	resume_tokens = _tokens(resume_text)
	matched = job_tokens & resume_tokens
	coverage = len(matched) / max(len(job_tokens), 1)
	section_count = len(re.findall(r"<h2\b", html, flags=re.IGNORECASE))
	has_contact = all(term in resume_text.lower() for term in ("email", "linkedin"))
	has_experience = "experiência" in resume_text.lower()
	ats_score = min(10.0, round(coverage * 10, 1))
	recruiter_score = min(
		10.0,
		round(coverage * 7 + (1.0 if section_count >= 5 else 0.0) + (1.0 if has_contact else 0.0) + (1.0 if has_experience else 0.0), 1),
	)
	return _json(
		{
			"mandatory_pre_action_instruction": MANDATORY_PROMPT_INSTRUCTION,
			"recruiter_human_score": recruiter_score,
			"ats_score": ats_score,
			"matched_terms": sorted(matched),
			"term_coverage_percent": round(coverage * 100, 1),
			"recommendation": "Review each suggested match against conhecimentos.md before saving the final resume.",
		}
	)


@mcp.tool()
def save_optimized_resume(resume_html: str, output_filename: str = "Currículo Otimizado.html") -> str:
	"""Validate and save an AI-generated resume in Curriculos Finalizados."""
	job = _read_text(JOB_PATH).strip()
	_assert_job_is_ready(job)
	_assert_candidate_html(resume_html)
	filename = Path(output_filename).name
	if not filename.lower().endswith(".html"):
		raise ValueError("output_filename deve terminar com .html")
	FINAL_RESUMES_ROOT.mkdir(parents=True, exist_ok=True)
	output_path = FINAL_RESUMES_ROOT / filename
	output_path.write_text(resume_html, encoding="utf-8")
	return _json(
		{
			"mandatory_pre_action_instruction": MANDATORY_PROMPT_INSTRUCTION,
			"saved": True,
			"path": str(output_path),
			"next_step": "Call evaluate_resume with the saved HTML and report both scores.",
		}
	)


@mcp.tool()
def get_server_status() -> str:
	"""Report whether the MCP inputs are ready for an optimization run."""
	status = _input_status()
	status["mandatory_pre_action_instruction"] = MANDATORY_PROMPT_INSTRUCTION
	return _json(status)


if __name__ == "__main__":
	mcp.run()
