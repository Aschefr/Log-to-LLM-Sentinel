import json

def clean_log_line(line: str) -> str:
    """Tente de nettoyer une ligne de log si elle est au format JSON (ex: Nextcloud)."""
    stripped = line.strip()
    if not (stripped.startswith('{') and stripped.endswith('}')):
        return line

    try:
        data = json.loads(stripped)
        # Pour Nextcloud : extraire message, app, et éventuellement exception
        msg = data.get("message", "")
        app = data.get("app", "")
        # Extraire l'exception si elle existe (peut être dans 'exception' ou 'data.exception')
        exc = data.get("exception", "") or data.get("data", {}).get("exception", "")
        
        if msg:
            cleaned = f"[{app}] {msg}"
            if exc:
                # On ne garde que le début de l'exception si elle est énorme
                exc_str = str(exc)
                if len(exc_str) > 1000:
                    exc_str = exc_str[:1000] + "... [EXCEPTION TRONQUÉE]"
                cleaned += f" | Exception: {exc_str}"
            return cleaned
        return line # Fallback si pas de champ message
    except:
        return line


def rotate_log_file(fp, max_bytes: int, backup_count: int = 5):
    """
    Standard shifted log rotation:
    - If fp does not exist or size < max_bytes, do nothing.
    - Otherwise, shift backups (xxx.log.4 -> xxx.log.5, ..., xxx.log -> xxx.log.1)
    """
    from pathlib import Path
    fp = Path(fp)
    if not fp.exists() or fp.stat().st_size < max_bytes:
        return
        
    for i in range(backup_count - 1, 0, -1):
        sfn = fp.with_suffix(f"{fp.suffix}.{i}")
        dfn = fp.with_suffix(f"{fp.suffix}.{i + 1}")
        if sfn.exists():
            try:
                if dfn.exists():
                    dfn.unlink()
                sfn.rename(dfn)
            except Exception:
                pass
                
    dfn = fp.with_suffix(f"{fp.suffix}.1")
    try:
        if dfn.exists():
            dfn.unlink()
        fp.rename(dfn)
    except Exception:
        pass
