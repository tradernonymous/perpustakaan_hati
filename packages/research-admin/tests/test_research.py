import json

import httpx
import pytest
import respx

from research_admin.config import Settings
from research_admin.research import ResearchError, mine_pain_points

URL = "https://openrouter.ai/api/v1/chat/completions"
SOURCE = {"text": "How do I rebuild trust?", "permalink": "https://www.threads.com/@sample/post/1", "source_type": "reply", "secret": "must-not-share"}
INSIGHT = {"theme": "Trust", "quote": "rebuild trust", "source_url": SOURCE["permalink"], "ebook_idea": "A guided reflection about boundaries"}


def call(posts=None, model="openrouter/free"):
    with httpx.Client() as http:
        return mine_pain_points([SOURCE] if posts is None else posts, Settings(openrouter_api_key="secret-key", openrouter_model=model), http)


@respx.mock
def test_free_router_and_grounded_insights():
    def response(request):
        payload = json.loads(request.content)
        assert payload["model"] == "openrouter/free"
        assert "models" not in payload
        assert payload["provider"]["max_price"] == {"prompt": 0, "completion": 0}
        assert "must-not-share" not in request.content.decode()
        assert payload["response_format"] == {"type": "json_object"}
        return httpx.Response(200, json={"choices": [{"message": {"content": json.dumps({"insights": [INSIGHT]})}}]})
    respx.post(URL).mock(side_effect=response)
    assert call() == [INSIGHT]


@pytest.mark.parametrize("content", ["broken", "[]", '{"insights": "bad"}', '{"insights":[{}]}', json.dumps({"insights": [{**INSIGHT, "source_url": "https://attacker.example"}]}), json.dumps({"insights": [{**INSIGHT, "quote": "invented quote"}]})])
@respx.mock
def test_rejects_malformed_or_fabricated_evidence(content):
    respx.post(URL).respond(200, json={"choices": [{"message": {"content": content}}]})
    with pytest.raises(ResearchError):
        call()


@respx.mock
def test_fenced_json_supported():
    respx.post(URL).respond(200, json={"choices": [{"message": {"content": '```json\n{"insights": []}\n```'}}]})
    assert call() == []


@respx.mock
def test_empty_posts_never_calls_provider():
    assert call([]) == []
    assert not respx.calls


@respx.mock
def test_rate_limit_redacted_no_fallback_or_retry():
    respx.post(URL).respond(429, json={"error": {"message": "secret-key"}})
    with pytest.raises(ResearchError, match="rate limit") as error:
        call()
    assert "secret-key" not in str(error.value)
    assert len(respx.calls) == 1


@respx.mock
def test_paid_model_rejected_before_network():
    with pytest.raises(ResearchError, match="free"):
        call(model="vendor/paid-model")
    assert not respx.calls


@respx.mock
def test_missing_key_is_actionable():
    with httpx.Client() as http, pytest.raises(ResearchError, match="OPENROUTER_API_KEY"):
        mine_pain_points([SOURCE], Settings(), http)


@respx.mock
def test_paid_model_request_omits_the_free_price_cap():
    def response(request):
        payload = json.loads(request.content)
        assert payload["model"] == "qwen/qwen3.7-flash"
        assert "provider" not in payload
        assert payload["reasoning"] == {"enabled": False}
        return httpx.Response(200, json={"choices": [{"message": {"content": json.dumps({"insights": [INSIGHT]})}}]})
    respx.post(URL).mock(side_effect=response)
    assert call(model="qwen/qwen3.7-flash") == [INSIGHT]


@respx.mock
def test_reasoning_model_that_returns_no_content_is_actionable():
    """Qwen's thinking mode used the whole budget on reasoning and sent no content."""
    respx.post(URL).respond(200, json={"choices": [{"message": {"content": None, "reasoning": "thinking..."}, "finish_reason": "length"}]})
    with pytest.raises(ResearchError, match="output budget"):
        call()


@respx.mock
def test_content_parts_and_a_top_level_array_are_accepted():
    content = [{"type": "text", "text": json.dumps([INSIGHT])}]
    respx.post(URL).respond(200, json={"choices": [{"message": {"content": content}}]})
    assert call() == [INSIGHT]


@pytest.mark.parametrize("content", [None, [], {}, 17])
@respx.mock
def test_non_string_content_is_safe_error(content):
    respx.post(URL).respond(200, json={"choices": [{"message": {"content": content}}]})
    with pytest.raises(ResearchError, match="format"):
        call()


@pytest.mark.parametrize("unlinked", [False, True])
@respx.mock
def test_quote_must_belong_to_its_cited_source(unlinked):
    second = {"text": "Different topic", "permalink": "https://www.threads.com/@sample/post/2"}
    first = {**SOURCE, "permalink": ""} if unlinked else SOURCE
    wrong = {**INSIGHT, "source_url": second["permalink"]}
    respx.post(URL).respond(200, json={"choices": [{"message": {"content": json.dumps({"insights": [wrong]})}}]})
    with pytest.raises(ResearchError, match="evidence"):
        call([first, second])


@respx.mock
def test_focus_is_appended_to_the_prompt_and_bounded():
    def response(request):
        prompt = json.loads(request.content)["messages"][0]["content"]
        assert "Focus for this run: healers after a breakup" in prompt
        assert "must-not-share" not in request.content.decode()
        return httpx.Response(200, json={"choices": [{"message": {"content": json.dumps({"insights": [INSIGHT]})}}]})
    respx.post(URL).mock(side_effect=response)
    with httpx.Client() as http:
        insights = mine_pain_points([SOURCE], Settings(openrouter_api_key="k"), http, focus="  healers   after a breakup  ")
    assert insights == [INSIGHT]


@respx.mock
def test_blank_focus_leaves_the_prompt_untouched():
    def response(request):
        prompt = json.loads(request.content)["messages"][0]["content"]
        assert "Focus for this run" not in prompt
        return httpx.Response(200, json={"choices": [{"message": {"content": json.dumps({"insights": [INSIGHT]})}}]})
    respx.post(URL).mock(side_effect=response)
    with httpx.Client() as http:
        assert mine_pain_points([SOURCE], Settings(openrouter_api_key="k"), http, focus="   ") == [INSIGHT]


@respx.mock
def test_openai_model_uses_max_completion_tokens_and_sends_attribution():
    def response(request):
        payload = json.loads(request.content)
        assert payload["max_completion_tokens"] >= 3000
        assert "max_tokens" not in payload
        assert request.headers["HTTP-Referer"].startswith("https://")
        assert request.headers["X-Title"]
        return httpx.Response(200, json={"choices": [{"message": {"content": json.dumps({"insights": [INSIGHT]})}}]})
    respx.post(URL).mock(side_effect=response)
    assert call(model="openai/gpt-6-luna") == [INSIGHT]


@respx.mock
def test_paid_model_attribution_headers_are_sent_too():
    def response(request):
        assert request.headers["X-Title"]
        return httpx.Response(200, json={"choices": [{"message": {"content": json.dumps({"insights": [INSIGHT]})}}]})
    respx.post(URL).mock(side_effect=response)
    assert call(model="qwen/qwen3.7-flash") == [INSIGHT]
