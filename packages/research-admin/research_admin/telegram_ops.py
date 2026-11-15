"""Telegram notification formatter, storm-controlled sender, and Mini App keyboard builder."""

from html import escape

import httpx

from .config import Settings

TELEGRAM_LIMIT = 4096
CALLBACK_LIMIT = 64


def callback_id(*parts: str) -> str:
    """Build a compact callback identifier capped to Telegram's 64-byte limit."""
    raw = "ra:" + ":".join(str(p or "").strip().replace(":", "-") for p in parts if str(p or "").strip())
    encoded = raw.encode("utf-8")[:CALLBACK_LIMIT]
    return encoded.decode("utf-8", errors="ignore")


def split_telegram_message(text: str, *, limit: int = TELEGRAM_LIMIT) -> list[str]:
    clean = str(text or "").strip()
    if not clean:
        return []
    if len(clean) <= limit:
        return [clean]
    chunks: list[str] = []
    remaining = clean
    while remaining:
        if len(remaining) <= limit:
            chunks.append(remaining)
            break
        split_at = remaining.rfind("\n", 0, limit)
        if split_at <= limit // 3:
            split_at = remaining.rfind(" ", 0, limit)
        if split_at <= 0:
            split_at = limit
        chunks.append(remaining[:split_at].rstrip())
        remaining = remaining[split_at:].lstrip()
    return chunks


def format_digest_html(*, title: str, lines: list[str], permalink: str = "") -> str:
    body = [f"<b>{escape(title)}</b>"]
    for line in lines[:20]:
        if str(line).strip():
            body.append(escape(str(line).strip()))
    if permalink:
        safe_url = escape(permalink, quote=True)
        body.append(f"<a href=\"{safe_url}\">Open in Dashboard</a>")
    return "\n".join(body)


def build_draft_keyboard(draft: dict, *, mini_app_url: str = "") -> dict:
    """Build Telegram Bot API 7.11+ inline keyboard with copy_text and optional web_app launcher."""
    draft_id = str(draft.get("id", ""))
    post_text = ""
    if isinstance(draft.get("content"), dict):
        post_text = str(draft["content"].get("post") or draft["content"].get("copy") or "")[:250]
    row_one = []
    if post_text:
        row_one.append({"text": "Copy Draft", "copy_text": {"text": post_text}})
    row_one.append({"text": "Approve", "callback_data": callback_id("approve", draft_id)})
    rows = [row_one]
    if mini_app_url:
        rows.append([{"text": "Open Mini App Review", "web_app": {"url": f"{mini_app_url.rstrip('/')}/mini?draft={draft_id}"}}])
    return {"inline_keyboard": rows}


def send_telegram_alert(
    settings: Settings,
    store,
    http: httpx.Client,
    message: str,
    options: dict | None = None,
) -> dict:
    """Send an HTML Telegram notification with 5-minute dedupe storm protection."""
    opts = options or {}
    dedupe_key = str(opts.get("dedupe_key") or message[:60]).strip()
    force = bool(opts.get("force", False))
    reply_markup = opts.get("reply_markup")
    token = getattr(settings, "telegram_bot_token", "")
    chat_id = getattr(settings, "telegram_chat_id", "")
    if not token or not chat_id:
        return {"ok": False, "skipped": True, "reason": "telegram_unconfigured"}
    if not force and store.recent_notification_exists(dedupe_key, within_seconds=300):
        return {"ok": False, "skipped": True, "reason": "dedupe_suppressed"}

    chunks = split_telegram_message(message)
    if not chunks:
        return {"ok": False, "skipped": True, "reason": "empty_message"}

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    last_error = ""
    sent_ok = True
    for idx, chunk in enumerate(chunks):
        payload: dict = {
            "chat_id": chat_id,
            "text": chunk,
            "parse_mode": "HTML",
            "disable_web_page_preview": True,
        }
        if reply_markup and idx == len(chunks) - 1:
            payload["reply_markup"] = reply_markup
        try:
            resp = http.post(url, json=payload, timeout=10.0)
            if not resp.is_success:
                sent_ok = False
                last_error = f"HTTP {resp.status_code}"
                break
        except httpx.HTTPError as exc:
            sent_ok = False
            last_error = str(exc)[:180]
            break

    store.record_notification(
        channel="telegram",
        dedupe_key=dedupe_key,
        message=chunks[0][:500],
        status="sent" if sent_ok else "failed",
        error=last_error,
    )
    return {"ok": sent_ok, "error": last_error}
