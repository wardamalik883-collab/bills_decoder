"""Level 2 question answering module for Pakistani utility bills."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from bill_decoder.calc_tools import bill_helpers
from bill_decoder.config import Config
from bill_decoder.extractor import parse_json_from_llm
from bill_decoder.llm_client import LLMClient
from bill_decoder.preprocess import preprocess_image_path
from bill_decoder.prompts import QA_SYSTEM_PROMPT, build_qa_prompt

logger = logging.getLogger(__name__)

FALLBACK_ANSWER = "This information could not be determined from the bill image."


def _fallback_answers(questions: dict[str, str]) -> dict[str, str]:
    return {qid: FALLBACK_ANSWER for qid in questions}


def _coerce_answers(raw: dict[str, Any], questions: dict[str, str]) -> dict[str, str]:
    """Map model output onto the known question ids, filling gaps with a fallback."""
    answers: dict[str, str] = {}
    for qid in questions:
        value = raw.get(qid)
        if isinstance(value, str) and value.strip():
            answers[qid] = value.strip()
        elif value is not None:
            answers[qid] = str(value).strip()
        else:
            answers[qid] = FALLBACK_ANSWER
    return answers


def answer_questions(
    bill_json: dict[str, Any],
    context: dict[str, Any],
    image_path: Path | str,
    questions: dict[str, str],
    config: Config | None = None,
    client: LLMClient | None = None,
) -> dict[str, str]:
    """Answer a mapping of {question_id: question_text} for one bill.

    Performs a single LLM call containing all questions. On any failure,
    every question receives a safe non-empty fallback answer.
    """
    if not questions:
        return {}

    try:
        proc_image_path = preprocess_image_path(image_path)
    except Exception:
        proc_image_path = Path(image_path)

    try:
        llm = client or LLMClient(config=config)
    except Exception as e:
        logger.warning("Q&A LLM init failed: %s. Returning fallback answers.", e)
        return _fallback_answers(questions)

    helpers = bill_helpers(bill_json, context)
    prompt = build_qa_prompt(
        bill_json=json.dumps(bill_json, ensure_ascii=False),
        context_json=json.dumps(context, ensure_ascii=False),
        helpers_json=json.dumps(helpers, ensure_ascii=False),
        questions_json=json.dumps(questions, ensure_ascii=False),
    )

    try:
        raw = llm.generate(
            prompt=prompt,
            image_path=proc_image_path,
            system=QA_SYSTEM_PROMPT,
            json_mode=True,
        )
        parsed = parse_json_from_llm(raw)
        return _coerce_answers(parsed, questions)
    except Exception as e:
        logger.warning("Batch Q&A call failed for %s: %s. Trying per-question.", image_path, e)

    # Fallback: one call per question
    answers: dict[str, str] = {}
    for qid, question in questions.items():
        try:
            single_prompt = build_qa_prompt(
                bill_json=json.dumps(bill_json, ensure_ascii=False),
                context_json=json.dumps(context, ensure_ascii=False),
                helpers_json=json.dumps(helpers, ensure_ascii=False),
                questions_json=json.dumps({qid: question}, ensure_ascii=False),
            )
            raw = llm.generate(
                prompt=single_prompt,
                image_path=proc_image_path,
                system=QA_SYSTEM_PROMPT,
                json_mode=True,
            )
            parsed = parse_json_from_llm(raw)
            answers[qid] = _coerce_answers(parsed, {qid: question})[qid]
        except Exception:
            answers[qid] = FALLBACK_ANSWER
    return answers
