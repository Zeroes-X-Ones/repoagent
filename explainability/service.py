import os
import re
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


class ExplainabilityService:
    """Service layer that turns retrieval decisions into structured explanations."""

    def build_explanation(self, *, repository: str, user_prompt: str, kept_files: List[str], removed_files: List[str], retrieved_blocks: List[Dict[str, Any]], model: str = "unknown", provider: str = "unknown") -> Dict[str, Any]:
        kept = []
        removed = []

        for file_path in kept_files:
            kept.append(self._build_file_explanation(file_path, user_prompt, retained=True, retrieved_blocks=retrieved_blocks))

        for file_path in removed_files:
            removed.append(self._build_file_explanation(file_path, user_prompt, retained=False, retrieved_blocks=retrieved_blocks))

        report = {
            "report_id": str(uuid.uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "repository": repository or os.getenv("REPO_NAME", "unknown"),
            "user_prompt": user_prompt,
            "model": model,
            "provider": provider,
            "kept_files": kept,
            "removed_files": removed,
            "summary": self._build_summary(kept, removed),
        }
        return report

    def _build_file_explanation(self, file_path: str, user_prompt: str, retained: bool, retrieved_blocks: List[Dict[str, Any]]) -> Dict[str, Any]:
        base_name = os.path.basename(file_path)
        lower_path = file_path.lower()
        lower_prompt = user_prompt.lower()

        if retained:
            confidence = 0.9
            reason = self._infer_retained_reason(lower_path, lower_prompt)
        else:
            confidence = 0.88
            reason = self._infer_removed_reason(lower_path, lower_prompt)

        block = next((item for item in retrieved_blocks if item.get("file") == file_path), None)
        retrieval_score = float(block.get("score", 0.0)) if block else 0.0
        semantic_similarity = round(min(1.0, max(0.0, retrieval_score + 0.1)), 3)
        dependencies = self._infer_dependencies(file_path)
        related_symbols = self._infer_related_symbols(file_path)
        importance_score = self._score_importance(file_path, lower_prompt, retained)

        return {
            "file": file_path,
            "retained": retained,
            "importance_score": round(importance_score, 3),
            "confidence": round(confidence, 3),
            "reason": reason,
            "dependencies": dependencies,
            "related_symbols": related_symbols,
            "retrieval_score": round(retrieval_score, 3),
            "semantic_similarity": semantic_similarity,
            "explanation": self._natural_language_explanation(file_path, retained, reason, importance_score),
        }

    def _infer_retained_reason(self, file_path: str, user_prompt: str) -> str:
        if "auth" in file_path or "security" in file_path:
            return "This file is relevant because authentication or security logic is central to the request."
        if "test" in file_path or "tests" in file_path:
            return "This file was kept because it directly supports the runtime behavior under discussion."
        if "db" in file_path or "database" in file_path:
            return "This file was retained because data access or persistence behavior is necessary to resolve the request."
        if "config" in file_path:
            return "This file was kept because configuration touches the execution path of the request."
        if "api" in file_path or "server" in file_path:
            return "This file was retained because the request affects exposed application behavior."
        return f"This file was retained because it contains relevant context for: {user_prompt[:60]}"

    def _infer_removed_reason(self, file_path: str, user_prompt: str) -> str:
        if "readme" in file_path or "doc" in file_path:
            return "This file was removed because documentation duplicates code-level guidance already present elsewhere."
        if "test" in file_path or "tests" in file_path:
            return "This file was removed because the request concerns runtime logic rather than test coverage."
        if "example" in file_path or "sample" in file_path:
            return "This file was removed because examples are not required to implement or explain the request."
        return f"This file was removed because it is not essential to the current request context: {user_prompt[:60]}"

    def _infer_dependencies(self, file_path: str) -> List[str]:
        lower = file_path.lower()
        deps = []
        if "auth" in lower or "security" in lower:
            deps.append("authentication")
        if "db" in lower or "database" in lower:
            deps.append("persistence")
        if "api" in lower or "server" in lower:
            deps.append("transport")
        if "router" in lower:
            deps.append("routing")
        if not deps:
            deps.append("core")
        return deps

    def _infer_related_symbols(self, file_path: str) -> List[str]:
        base = os.path.splitext(os.path.basename(file_path))[0]
        if not base:
            return []
        return [base, f"{base}_handler", f"{base}_logic"]

    def _score_importance(self, file_path: str, user_prompt: str, retained: bool) -> float:
        lower = file_path.lower()
        score = 0.3
        if retained:
            score += 0.4
        if "auth" in lower or "security" in lower:
            score += 0.2
        if "db" in lower or "database" in lower:
            score += 0.2
        if "server" in lower or "api" in lower:
            score += 0.15
        if user_prompt and len(user_prompt) > 20:
            score += 0.05
        return min(1.0, round(score, 3))

    def _natural_language_explanation(self, file_path: str, retained: bool, reason: str, importance_score: float) -> str:
        status = "retained" if retained else "removed"
        return f"{os.path.basename(file_path)} was {status} because {reason.lower()} The file's importance score is {importance_score:.2f}."

    def _build_summary(self, kept: List[Dict[str, Any]], removed: List[Dict[str, Any]]) -> Dict[str, Any]:
        return {
            "kept_count": len(kept),
            "removed_count": len(removed),
            "avg_importance": round(sum(item["importance_score"] for item in kept + removed) / max(1, len(kept) + len(removed)), 3),
            "avg_confidence": round(sum(item["confidence"] for item in kept + removed) / max(1, len(kept) + len(removed)), 3),
        }


explainability_service = ExplainabilityService()
