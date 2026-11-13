import json

import httpx
import pytest
import respx

from research_admin.config import Settings
from research_admin.content import generate_drafts
from research_admin.research import ResearchError

URL = "https://openrouter.ai/api/v1/chat/completions"
INSIGHT = {"id": 7, "theme": "Trust", "quote": "rebuild trust", "ebook_idea": "A guided reflection about boundaries", "source_url": "https://www.threads.net/@rahimah/post/ABC123"}
DRAFTS = {"drafts": [
    {"kind": "threads_post", "title": "A note on trust", "content": {"post": "Trust grows in small, honest moments."}, "source_ids": [7]},
    {"kind": "ebook_outline", "title": "Rebuilding trust", "content": {
        "premise": "Trust can be rebuilt carefully.",
        "intended_reader_need": "A reader who wants a practical next step.",
        "chapters": [
            {"title": "Name what broke", "outcome": "The reader names the rupture without blame."},
            {"title": "Small promises", "outcome": "The reader chooses one repeatable action."},
            {"title": "Repair conversations", "outcome": "The reader can ask for a repair talk."},
        ],
    }, "source_ids": [7]},
    {"kind": "design_brief", "title": "Trust, quietly", "content": {
        "concept": "Open hands, not a locked door.",
        "format": "Square social card",
        "visual_direction": "Warm paper texture, sage and gold.",
        "copy": "Trust is rebuilt in small, kept promises.",
    }, "source_ids": [7]},
]}


def settings(model="qwen/qwen3.7-flash"):
    return Settings(openrouter_api_key="secret-key", openrouter_model=model)


def call(model="qwen/qwen3.7-flash"):
    with httpx.Client() as http:
        return generate_drafts([INSIGHT], settings(model), http)


@respx.mock
def test_paid_model_draft_request_omits_the_free_price_cap():
    """The zero-price filter made OpenRouter answer 404 for a paid model."""
    def respond(request):
        payload = json.loads(request.content)
        assert payload["model"] == "qwen/qwen3.7-flash"
        assert "provider" not in payload
        assert payload["reasoning"] == {"enabled": False}
        assert payload["max_tokens"] >= 3000
        return httpx.Response(200, json={"choices": [{"message": {"content": json.dumps(DRAFTS)}}]})
    respx.post(URL).mock(side_effect=respond)
    drafts = call()
    assert [draft["kind"] for draft in drafts] == ["threads_post", "ebook_outline", "design_brief"]
    assert all(draft["source_ids"] == [7] for draft in drafts)


@respx.mock
def test_free_model_draft_request_keeps_the_zero_price_cap():
    def respond(request):
        payload = json.loads(request.content)
        assert payload["provider"]["max_price"] == {"prompt": 0, "completion": 0}
        return httpx.Response(200, json={"choices": [{"message": {"content": json.dumps(DRAFTS)}}]})
    respx.post(URL).mock(side_effect=respond)
    assert len(call(model="openrouter/free")) == 3


@respx.mock
def test_model_without_endpoint_is_actionable():
    respx.post(URL).respond(404, json={"error": {"message": "No endpoints found that satisfy the max price for this request"}})
    with pytest.raises(ResearchError, match="OPENROUTER_MODEL"):
        call()


@respx.mock
def test_threads_post_sent_as_a_bare_string_is_kept():
    """The live model answers a post as a string, not the requested object."""
    drafts = json.loads(json.dumps(DRAFTS))
    drafts["drafts"][0]["content"] = "Trust grows in small, honest moments. What promise can you keep this week?"
    respx.post(URL).respond(200, json={"choices": [{"message": {"content": json.dumps(drafts)}, "finish_reason": "stop"}]})
    posts = call()
    assert posts[0]["kind"] == "threads_post"
    assert posts[0]["content"]["post"].startswith("Trust grows in small, honest moments.")


@respx.mock
def test_alternative_post_field_and_single_source_id_are_normalised():
    drafts = json.loads(json.dumps(DRAFTS))
    drafts["drafts"][0]["content"] = {"text": "Trust grows in small, honest moments."}
    drafts["drafts"][0]["source_ids"] = 7
    respx.post(URL).respond(200, json={"choices": [{"message": {"content": json.dumps(drafts)}, "finish_reason": "stop"}]})
    posts = call()
    assert posts[0]["content"]["post"] == "Trust grows in small, honest moments."
    assert posts[0]["source_ids"] == [7]


@respx.mock
def test_truncated_response_explains_the_output_budget():
    respx.post(URL).respond(200, json={"choices": [{"message": {"content": ""}, "finish_reason": "length"}]})
    with pytest.raises(ResearchError, match="output budget"):
        call()


@respx.mock
def test_outline_and_brief_carry_the_source_post_link_but_the_post_does_not():
    drafts = json.loads(json.dumps(DRAFTS))
    for draft in drafts["drafts"]:
        draft["content"]["references"] = [{"url": "https://model.example/invented"}]
    respx.post(URL).respond(200, json={"choices": [{"message": {"content": json.dumps(drafts)}, "finish_reason": "stop"}]})
    post, outline, brief = call()
    assert "references" not in post["content"]
    for draft in (outline, brief):
        assert draft["content"]["references"] == [{
            "insight_id": 7,
            "theme": "Trust",
            "url": "https://www.threads.net/@rahimah/post/ABC123",
        }]


@respx.mock
def test_drafts_without_a_saved_permalink_omit_the_references_block():
    respx.post(URL).respond(200, json={"choices": [{"message": {"content": json.dumps(DRAFTS)}, "finish_reason": "stop"}]})
    insight = {key: value for key, value in INSIGHT.items() if key != "source_url"}
    with httpx.Client() as http:
        drafts = generate_drafts([insight], settings(), http)
    assert all("references" not in draft["content"] for draft in drafts)


@respx.mock
def test_openai_model_draft_request_uses_max_completion_tokens_and_attribution():
    """OpenAI models reject max_tokens; OpenRouter also asks for app attribution."""
    def respond(request):
        payload = json.loads(request.content)
        assert payload["model"] == "openai/gpt-6-luna"
        assert payload["max_completion_tokens"] >= 3000
        assert "max_tokens" not in payload
        assert request.headers["HTTP-Referer"].startswith("https://")
        assert request.headers["X-Title"]
        return httpx.Response(200, json={"choices": [{"message": {"content": json.dumps(DRAFTS)}}]})
    respx.post(URL).mock(side_effect=respond)
    assert len(call(model="openai/gpt-6-luna")) == 3


@respx.mock
def test_qwen_draft_request_still_uses_max_tokens_with_attribution():
    def respond(request):
        payload = json.loads(request.content)
        assert payload["max_tokens"] >= 3000
        assert "max_completion_tokens" not in payload
        assert request.headers["X-Title"]
        return httpx.Response(200, json={"choices": [{"message": {"content": json.dumps(DRAFTS)}}]})
    respx.post(URL).mock(side_effect=respond)
    assert len(call()) == 3


@respx.mock
def test_prompt_only_requests_the_selected_draft_kinds_tone_and_language():
    def respond(request):
        system = json.loads(request.content)["messages"][0]["content"]
        suffix = system.split("Generate only these draft kinds:", 1)[1]
        assert "threads_post, ebook_outline." in suffix
        assert "Tone: reflective." in suffix
        assert "Language: English." in suffix
        assert "design_brief" not in suffix
        return httpx.Response(200, json={"choices": [{"message": {"content": json.dumps(
            {"drafts": [d for d in DRAFTS["drafts"] if d["kind"] != "design_brief"]})}}]})
    respx.post(URL).mock(side_effect=respond)
    with httpx.Client() as http:
        drafts = generate_drafts([INSIGHT], settings(), http, kinds=["threads_post", "ebook_outline"], tone="reflective", language="English")
    assert [draft["kind"] for draft in drafts] == ["threads_post", "ebook_outline"]


@respx.mock
def test_subset_run_rejects_a_response_missing_one_selected_kind():
    """Extra kinds are dropped, but a selected kind that never arrives is an error."""
    partial = {"drafts": [d for d in DRAFTS["drafts"] if d["kind"] == "threads_post"]}
    respx.post(URL).respond(200, json={"choices": [{"message": {"content": json.dumps(partial)}, "finish_reason": "stop"}]})
    with httpx.Client() as http:
        with pytest.raises(ResearchError, match="did not include every selected kind"):
            generate_drafts([INSIGHT], settings(), http, kinds=["threads_post", "ebook_outline"])


@respx.mock
def test_unknown_tone_and_language_fall_back_to_the_defaults():
    def respond(request):
        system = json.loads(request.content)["messages"][0]["content"]
        assert "Tone: empathetic." in system
        assert "Language: match evidence (match the dominant language of the supplied evidence)." in system
        return httpx.Response(200, json={"choices": [{"message": {"content": json.dumps(DRAFTS)}}]})
    respx.post(URL).mock(side_effect=respond)
    with httpx.Client() as http:
        drafts = generate_drafts([INSIGHT], settings(), http, kinds=None, tone="shakespearean", language="Klingon")
    assert len(drafts) == 3
