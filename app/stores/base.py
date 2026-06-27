"""Store cơ sở — adapter 3 backend: Postgres (psycopg2) > Supabase > JSON local.

Một interface (insert/get/update/list/delete). Chọn backend theo env:
  - TATA_DATABASE_URL (postgres://…)  → Postgres trực tiếp (DB truyền thống / deploy server)
  - SUPABASE_URL + SUPABASE_KEY        → Supabase (PostgREST)
  - (không có)                          → JSON file local (dev/offline)
Deploy đổi DB chỉ cần set TATA_DATABASE_URL — store con + logic phía trên KHÔNG đổi.
"""
import os
import json
import time
import uuid
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TaTa.Store")

DATA_DIR = os.environ.get("TATA_STORE_DIR", "tata_store_data")

_supabase_client = None
_supabase_inited = False
_pg_conn = None


def _load_env_caveman():
    fp = ".env.caveman"
    if not os.path.exists(fp):
        return
    with open(fp, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())


def pg_dsn():
    _load_env_caveman()
    return os.environ.get("TATA_DATABASE_URL")


def get_pg():
    """Connection psycopg2 autocommit (cache 1 cái, tự reconnect nếu đứt)."""
    global _pg_conn
    dsn = pg_dsn()
    if not dsn:
        return None
    if _pg_conn is not None and getattr(_pg_conn, "closed", 1) == 0:
        return _pg_conn
    import psycopg2
    _pg_conn = psycopg2.connect(dsn)
    _pg_conn.autocommit = True
    logger.info("✅ Store: kết nối Postgres trực tiếp (TATA_DATABASE_URL).")
    return _pg_conn


def get_supabase():
    global _supabase_client, _supabase_inited
    if _supabase_inited:
        return _supabase_client
    _supabase_inited = True
    _load_env_caveman()
    url, key = os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_KEY")
    if url and key:
        try:
            from supabase import create_client
            _supabase_client = create_client(url, key)
            logger.info("✅ Store: kết nối Supabase.")
        except Exception as e:  # noqa: BLE001
            logger.warning("⚠️ Store: Supabase lỗi (%s) → fallback.", e)
            _supabase_client = None
    return _supabase_client


def _jsonify(v):
    """Bọc list/dict thành psycopg2 Json để vào cột JSONB."""
    from psycopg2.extras import Json
    return Json(v) if isinstance(v, (list, dict)) else v


class Store:
    id_prefix = "row"

    def __init__(self, collection, client=None):
        self.collection = collection
        # ưu tiên Postgres → Supabase → JSON
        if pg_dsn():
            self.backend = "pg"
        elif client is not None or get_supabase():
            self.backend = "supabase"
            self.client = client if client is not None else get_supabase()
        else:
            self.backend = "json"
        if self.backend == "json":
            os.makedirs(DATA_DIR, exist_ok=True)
            self._path = os.path.join(DATA_DIR, f"{collection}.json")
            if not os.path.exists(self._path):
                self._write_local([])

    # ---------- JSON ----------
    def _read_local(self):
        try:
            with open(self._path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:  # noqa: BLE001
            logger.error("Đọc %s lỗi: %s", self._path, e)
            return []

    def _write_local(self, rows):
        with open(self._path, "w", encoding="utf-8") as f:
            json.dump(rows, f, ensure_ascii=False, indent=2)

    # ---------- Postgres ----------
    def _pg_cursor(self):
        from psycopg2.extras import RealDictCursor
        return get_pg().cursor(cursor_factory=RealDictCursor)

    def _new_id(self):
        return f"{self.id_prefix}-{uuid.uuid4().hex[:10]}"

    # ---------- CRUD ----------
    def insert(self, row):
        row = dict(row)
        row.setdefault("id", self._new_id())
        row.setdefault("created_at", time.time())
        if self.backend == "pg":
            cols = list(row.keys())
            ph = ", ".join(["%s"] * len(cols))
            with self._pg_cursor() as cur:
                cur.execute(
                    f'INSERT INTO {self.collection} ({", ".join(cols)}) VALUES ({ph})',
                    [_jsonify(row[c]) for c in cols],
                )
            return row
        if self.backend == "supabase":
            try:
                self.client.table(self.collection).insert(row).execute()
                return row
            except Exception as e:  # noqa: BLE001
                logger.warning("Supabase insert lỗi (%s).", e)
                return row
        rows = self._read_local(); rows.append(row); self._write_local(rows)
        return row

    def get(self, row_id):
        if self.backend == "pg":
            with self._pg_cursor() as cur:
                cur.execute(f"SELECT * FROM {self.collection} WHERE id = %s LIMIT 1", [row_id])
                r = cur.fetchone()
                return dict(r) if r else None
        if self.backend == "supabase":
            r = self.client.table(self.collection).select("*").eq("id", row_id).limit(1).execute()
            data = getattr(r, "data", None) or []
            return data[0] if data else None
        for row in self._read_local():
            if row.get("id") == row_id:
                return row
        return None

    def update(self, row_id, patch):
        patch = dict(patch)
        patch["updated_at"] = time.time()
        if self.backend == "pg":
            sets = ", ".join(f"{k} = %s" for k in patch)
            vals = [_jsonify(v) for v in patch.values()] + [row_id]
            with self._pg_cursor() as cur:
                cur.execute(f"UPDATE {self.collection} SET {sets} WHERE id = %s", vals)
            return self.get(row_id)
        if self.backend == "supabase":
            self.client.table(self.collection).update(patch).eq("id", row_id).execute()
            return self.get(row_id)
        rows = self._read_local(); found = None
        for row in rows:
            if row.get("id") == row_id:
                row.update(patch); found = row; break
        if found is not None:
            self._write_local(rows)
        return found

    def list(self, **filters):
        if self.backend == "pg":
            sql = f"SELECT * FROM {self.collection}"
            vals = []
            if filters:
                sql += " WHERE " + " AND ".join(f"{k} = %s" for k in filters)
                vals = list(filters.values())
            with self._pg_cursor() as cur:
                cur.execute(sql, vals)
                return [dict(r) for r in cur.fetchall()]
        if self.backend == "supabase":
            q = self.client.table(self.collection).select("*")
            for k, v in filters.items():
                q = q.eq(k, v)
            r = q.execute()
            return getattr(r, "data", None) or []
        rows = self._read_local()
        if filters:
            rows = [r for r in rows if all(r.get(k) == v for k, v in filters.items())]
        return rows

    def delete(self, row_id):
        if self.backend == "pg":
            with self._pg_cursor() as cur:
                cur.execute(f"DELETE FROM {self.collection} WHERE id = %s", [row_id])
            return True
        if self.backend == "supabase":
            self.client.table(self.collection).delete().eq("id", row_id).execute()
            return True
        rows = self._read_local()
        new = [r for r in rows if r.get("id") != row_id]
        self._write_local(new)
        return len(new) != len(rows)
