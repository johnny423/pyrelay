from datetime import datetime, timezone
from typing import Optional, Self

from sqlalchemy import and_, column, or_, select, update
from sqlalchemy.orm import contains_eager, sessionmaker
from sqlalchemy.sql import Select
from sqlalchemy.sql.elements import BinaryExpression, BooleanClauseList

from pyrelay.nostr.event import EventId, EventKind, NostrEvent, NostrTag
from pyrelay.nostr.filters import NostrFilter
from pyrelay.relay.relay_service import EventsRepository


class SqlAlchemyEventRepository(EventsRepository):
    def __init__(self, session: sessionmaker) -> None:
        self.session_maker = session

    async def delete(self, event_ids: list[EventId]) -> None:
        async with self.session_maker() as s:
            async with self.session_maker.begin():
                query = (
                    update(NostrEvent)
                    .where(NostrEvent.id.in_(event_ids))
                    .values(deleted_at=datetime.now(timezone.utc))
                    .execution_options(synchronize_session="fetch")
                )

                await s.execute(query)
            await s.commit()

    async def add(self, event: NostrEvent) -> None:
        async with self.session_maker() as s:
            async with self.session_maker.begin():
                s.add(event)

            await s.commit()

    async def query(self, *filters: NostrFilter) -> list[NostrEvent]:
        query = (
            select(NostrEvent)
            .outerjoin(NostrTag)
            .options(contains_eager(NostrEvent.tags))
            .filter(column("deleted_at").is_(None))
        )

        query_builder = EventQueryBuilder(query)
        limits = []

        for _filter in filters:
            query_builder = query_builder.apply_filter(_filter)
            if _filter.limit:
                limits.append(_filter.limit)

        query = query_builder.build()

        if limits:
            limit = max(limits)
            query = query.order_by(NostrEvent.created_at.desc()).limit(  # type: ignore
                limit
            )
        else:
            query = query.order_by(NostrEvent.created_at)

        async with self.session_maker() as s:
            x = await s.execute(query)
            return [event for (event,) in x.unique()]


class EventQueryBuilder:
    def __init__(self, query: Select) -> None:
        self.query = query
        self.filters: list[BooleanClauseList] = []

    def apply_filter(self, _filter: NostrFilter) -> Self:  # type: ignore
        filter_builder = (
            EventFiltersBuilder()  # type: ignore
            .filter_ids(_filter.ids)
            .filter_authors(_filter.authors)
            .filter_kinds(_filter.kinds)
            .filter_since(_filter.since)
            .filter_until(_filter.until)
        )

        if _filter.e_tag:
            filter_builder = filter_builder.filter_tags("e", _filter.e_tag)

        if _filter.p_tag:
            filter_builder = filter_builder.filter_tags("p", _filter.p_tag)

        f = filter_builder.build()
        self.filters.append(f)

        return self

    def build(self) -> Select:
        match len(self.filters):
            case 0:
                return self.query
            case 1:
                [filters] = self.filters
            case _:
                filters = or_(*self.filters)

        return self.query.filter(filters)


class EventFiltersBuilder:
    def __init__(self) -> None:
        self.filters: list[BinaryExpression] = []

    def filter_tags(self, tag_type: str, tags: list[str]) -> Self:  # type: ignore
        self.filters.append(NostrTag.type == tag_type)
        self.filters.append(NostrTag.key.in_(tags))  # type: ignore
        return self

    def filter_since(self, since: Optional[int]) -> Self:  # type: ignore
        if since:
            self.filters.append(NostrEvent.created_at >= since)

        return self

    def filter_until(self, until: Optional[int]) -> Self:  # type: ignore
        if until:
            self.filters.append(NostrEvent.created_at < until)

        return self

    def filter_ids(self, ids: Optional[list[str]]) -> Self:  # type: ignore
        if ids:
            prefix = [
                NostrEvent.id.ilike(f"{event_id}%") for event_id in ids  # type: ignore
            ]
            self.filters.append(or_(*prefix))

        return self

    def filter_authors(self, authors: Optional[list[str]]) -> Self:  # type: ignore
        if authors:
            prefix = [
                NostrEvent.pubkey.ilike(f"{author}%")  # type: ignore
                for author in authors
            ]
            self.filters.append(or_(*prefix))

        return self

    def filter_kinds(self, kinds: Optional[list[EventKind]]) -> Self:  # type: ignore
        if kinds:
            prefix = [NostrEvent.kind == kind for kind in kinds]
            self.filters.append(or_(*prefix))

        return self

    def build(self) -> BooleanClauseList:
        return and_(*self.filters)
