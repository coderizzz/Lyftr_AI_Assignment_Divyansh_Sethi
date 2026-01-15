from datetime import datetime
from sqlite3 import IntegrityError
from app.models import get_connection


def insert_message(msg):
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute(
            """
            INSERT INTO messages (
                message_id,
                from_msisdn,
                to_msisdn,
                ts,
                text,
                created_at
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                msg.message_id,
                msg.from_msisdn,
                msg.to_msisdn,
                msg.ts.isoformat().replace("+00:00", "Z"),
                msg.text,
                datetime.utcnow().isoformat() + "Z",
            ),
        )
        conn.commit()
        return "created"
    except IntegrityError:
        return "duplicate"
    finally:
        conn.close()
def list_messages(limit, offset, from_msisdn=None, since=None, q=None):
    conn = get_connection()
    cur = conn.cursor()

    filters = []
    params = []

    if from_msisdn:
        filters.append("from_msisdn = ?")
        params.append(from_msisdn)

    if since:
        filters.append("ts >= ?")
        params.append(since)

    if q:
        filters.append("LOWER(text) LIKE ?")
        params.append(f"%{q.lower()}%")

    where = ""
    if filters:
        where = "WHERE " + " AND ".join(filters)

    total_query = f"SELECT COUNT(*) FROM messages {where}"
    cur.execute(total_query, params)
    total = cur.fetchone()[0]

    data_query = f"""
        SELECT message_id, from_msisdn, to_msisdn, ts, text
        FROM messages
        {where}
        ORDER BY ts ASC, message_id ASC
        LIMIT ? OFFSET ?
    """

    cur.execute(data_query, params + [limit, offset])
    rows = cur.fetchall()

    conn.close()

    data = [
        {
            "message_id": r[0],
            "from": r[1],
            "to": r[2],
            "ts": r[3],
            "text": r[4],
        }
        for r in rows
    ]

    return data, total

def get_stats():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM messages")
    total_messages = cur.fetchone()[0]

    cur.execute("SELECT COUNT(DISTINCT from_msisdn) FROM messages")
    senders_count = cur.fetchone()[0]

    cur.execute(
        """
        SELECT from_msisdn, COUNT(*) as c
        FROM messages
        GROUP BY from_msisdn
        ORDER BY c DESC
        LIMIT 10
        """
    )
    messages_per_sender = [
        {"from": r[0], "count": r[1]} for r in cur.fetchall()
    ]

    cur.execute("SELECT MIN(ts), MAX(ts) FROM messages")
    row = cur.fetchone()
    first_ts = row[0]
    last_ts = row[1]

    conn.close()

    return {
        "total_messages": total_messages,
        "senders_count": senders_count,
        "messages_per_sender": messages_per_sender,
        "first_message_ts": first_ts,
        "last_message_ts": last_ts,
    }
