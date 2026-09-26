# core/store.py
import numpy as np
import pyarrow as pa
import lancedb

from core.config import cfg
from utils.logger import log

# ── Schema ────────────────────────────────────────────────────────────
_SCHEMA = pa.schema([
    pa.field("text",       pa.utf8()),
    pa.field("department", pa.utf8()),   # ABAC isolation key
    pa.field("source",     pa.utf8()),   # original filename
    pa.field("chunk_idx",  pa.int32()),
    pa.field("vector",     pa.list_(pa.float32(), cfg.embed_dimensions)),
])


class VectorStore:
    """
    LanceDB-backed persistent vector store with ABAC department isolation.
    Every query is hard-filtered by department at the DB level.
    """

    def __init__(self):
        self.db = lancedb.connect(cfg.db_path)

    # ── Internal helpers ──────────────────────────────────────────────

    def _get_table(self):
        if cfg.table_name in self.db.table_names():
            return self.db.open_table(cfg.table_name)
        # Create empty table with schema on first use
        return self.db.create_table(cfg.table_name, schema=_SCHEMA)

    # ── Public API ────────────────────────────────────────────────────

    def add_documents(
        self,
        chunks: list[dict],
        embeddings: np.ndarray,
        department: str,
        source: str,
    ) -> int:
        """
        Index documents under a specific department.
        APPENDS to existing table — other departments are not affected.
        """
        records = [
            {
                "text":       c["text"],
                "department": department.lower(),
                "source":     source,
                "chunk_idx":  c["chunk_idx"],
                "vector":     e.tolist(),
            }
            for c, e in zip(chunks, embeddings)
        ]
        tbl = self._get_table()
        tbl.add(records)
        log.info(f"Indexed {len(records)} chunks — dept={department}, source={source}")
        return len(records)

    def search(
        self,
        query_vec: np.ndarray,
        department: str,
        top_k: int = None,
    ) -> list[dict]:
        """
        ABAC-enforced ANN search.
        The department filter is ALWAYS applied — no user can bypass it.
        """
        top_k = top_k or cfg.top_k
        dept = department.lower()
        tbl = self._get_table()

        results = (
            tbl.search(query_vec.tolist())
               .where(f"department = '{dept}'")   # ← ABAC enforcement
               .limit(top_k * 3)                  # over-fetch for BM25 re-rank
               .to_pandas()
        )

        if results.empty:
            return []

        return [
            {
                "text":       row["text"],
                "department": row["department"],
                "source":     row["source"],
                "score":      float(1.0 - row.get("_distance", 0.0)),
            }
            for _, row in results.iterrows()
        ]

    def delete_department(self, department: str):
        """Admin only: remove ALL documents for a department."""
        dept = department.lower()
        tbl = self._get_table()
        tbl.delete(f"department = '{dept}'")
        log.info(f"Deleted all documents for department='{dept}'")

    def delete_source(self, department: str, source: str):
        """Admin only: remove one specific document from a department."""
        dept = department.lower()
        tbl = self._get_table()
        tbl.delete(f"department = '{dept}' AND source = '{source}'")
        log.info(f"Deleted source='{source}' from department='{dept}'")

    def list_sources(self, department: str) -> list[str]:
        """Return unique document filenames indexed for a department."""
        dept = department.lower()
        try:
            tbl = self._get_table()
            df = tbl.to_pandas()
            dept_df = df[df["department"] == dept]
            return sorted(dept_df["source"].unique().tolist())
        except Exception:
            return []

    def get_stats(self) -> dict:
        """Return chunk counts per department (for admin dashboard)."""
        try:
            tbl = self._get_table()
            df = tbl.to_pandas()
            return df.groupby("department").size().to_dict()
        except Exception:
            return {}

    def is_empty(self, department: str) -> bool:
        """Check whether a department has any indexed documents."""
        return len(self.list_sources(department)) == 0


# Singleton — import and use everywhere
store = VectorStore()
