from __future__ import annotations

import wikipedia
from typing import Any, Dict


class WikipediaService:
    def summary(self, query: str, sentences: int = 5, lang: str = "en") -> Dict[str, Any]:
        if not query:
            return {"status": "error", "message": "Please provide a topic."}

        wikipedia.set_lang(lang)
        try:
            summary = wikipedia.summary(query, sentences=sentences)
            page = wikipedia.page(query)
            return {
                "status": "ok",
                "title": page.title,
                "url": page.url,
                "summary": summary,
                "categories": page.categories[:6],
                "links_count": len(page.links),
            }
        except wikipedia.exceptions.DisambiguationError as exc:
            return {
                "status": "error",
                "message": "Ambiguous topic. Please be more specific.",
                "options": exc.options[:8],
            }
        except wikipedia.exceptions.PageError:
            return {"status": "error", "message": "Topic not found."}
