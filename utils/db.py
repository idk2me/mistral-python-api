import aiosqlite
from utils.logging_config import get_logger

DB_PATH: str = "papers.db"
logger = get_logger(__name__)


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
        CREATE TABLE IF NOT EXISTS papers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            arxiv_id TEXT UNIQUE,
            title TEXT,
            summary TEXT,
            authors TEXT,
            published TEXT,
            category TEXT,
            link TEXT,
            processed BOOLEAN DEFAULT 0,
            ai_summary TEXT,
            novelty_score INTEGER,
            relevance_score INTEGER,
            read_recommendation TEXT,
            viewed BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        )
        await db.execute(
            """
        CREATE TABLE IF NOT EXISTS user_settings (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            niche_interests TEXT,
            additional_params TEXT
        );
        """
        )
        # Insert default row if it doesn't exist
        await db.execute(
            """
        INSERT OR IGNORE INTO user_settings (id, niche_interests, additional_params)
        VALUES (1, '', '');
        """
        )
        
        # Migration: Add viewed column if it doesn't exist
        try:
            await db.execute("ALTER TABLE papers ADD COLUMN viewed BOOLEAN DEFAULT 0;")
            logger.info("Added viewed column to papers table")
        except Exception:
            # Column already exists
            pass
        
        # Migration: Set viewed=1 where ai_summary exists or processed=1
        await db.execute(
            """
            UPDATE papers 
            SET viewed = 1 
            WHERE ai_summary IS NOT NULL OR processed = 1;
            """
        )
        
        await db.commit()


async def add_paper(paper: dict):
    async with aiosqlite.connect(DB_PATH) as db:
        logger.info(
            f"Adding paper: {paper.get('arxiv_id', 'unknown')} - {paper.get('title', 'no title')}"
        )
        try:
            await db.execute(
                """
                INSERT INTO papers (arxiv_id, title, summary, authors, published, category, link)
                VALUES (?,?,?,?,?,?,?)
            """,
                (
                    paper["arxiv_id"],
                    paper["title"],
                    paper["summary"],
                    paper["authors"],
                    paper["published"],
                    paper["category"],
                    paper["link"],
                ),
            )
            await db.commit()
            logger.info(f"Successfully added paper: {paper['arxiv_id']}")
        except aiosqlite.IntegrityError as e:
            logger.debug(
                f"Paper already exists in database: {paper.get('arxiv_id', 'unknown')}"
            )
        except Exception as e:
            logger.error(f"Error adding paper {paper.get('arxiv_id', 'unknown')}: {e}")
            logger.error(f"Paper data: {paper}")
            raise


async def update_paper_summary(arxiv_id: str, summary_data: dict):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            UPDATE papers
            SET ai_summary = ?, 
                novelty_score = ?, 
                relevance_score = ?, 
                read_recommendation = ?, 
                processed = 1
            WHERE arxiv_id = ?;
        """,
            (
                summary_data.get("ai_summary"),
                summary_data.get("novelty_score"),
                summary_data.get("relevance_score"),
                summary_data.get("read_recommendation"),
                arxiv_id,
            ),
        )
        await db.commit()


async def get_latest_papers(limit: int = 10) -> list[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            """
            SELECT * FROM papers
            ORDER BY created_at DESC
            LIMIT ?;
            """,
            (limit,),
        ) as cursor:
            rows = await cursor.fetchall()
            return [dict(r) for r in rows]


async def get_paper_by_id(id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            """
            SELECT * FROM papers
            WHERE id = ?;
            """,
            (id,),
        ) as cursor:
            return await cursor.fetchone()


async def get_all_papers():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            """
            SELECT * FROM papers;
            """,
        ) as cursor:
            return await cursor.fetchall()


async def get_user_settings() -> dict:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            """
            SELECT niche_interests, additional_params FROM user_settings
            WHERE id = 1;
            """
        ) as cursor:
            row = await cursor.fetchone()
            return (
                dict(row) if row else {"niche_interests": "", "additional_params": ""}
            )


async def update_user_settings(niche_interests: str, additional_params: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            UPDATE user_settings 
            SET niche_interests = ?, additional_params = ?
            WHERE id = 1;
            """,
            (niche_interests, additional_params),
        )
        await db.commit()
