# coding=utf-8
"""
Simple request-timing middleware for development profiling.

Logs one summary line per request:
  [PROFILE] GET /en/version/4.0/ → 4832 ms | 47 queries | 1203 ms in DB

Enable by adding to MIDDLEWARE in dev.py:
  MIDDLEWARE = ['core.profiling_middleware.RequestTimingMiddleware'] + MIDDLEWARE
"""
import logging
import time

from django.db import connection

logger = logging.getLogger('changes.profiling')


class RequestTimingMiddleware:
    """Log total request time, number of DB queries, and cumulative DB time."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Reset query log for this request
        n_queries_before = len(connection.queries)
        t_start = time.perf_counter()

        response = self.get_response(request)

        t_total_ms = (time.perf_counter() - t_start) * 1000

        # Queries executed during this request
        queries = connection.queries[n_queries_before:]
        n_queries = len(queries)
        t_db_ms = sum(float(q.get('time', 0)) for q in queries) * 1000

        logger.debug(
            '[PROFILE] %s %s → %.0f ms | %d queries | %.0f ms in DB',
            request.method,
            request.path,
            t_total_ms,
            n_queries,
            t_db_ms,
        )

        # If there are many duplicate queries, flag them
        sql_list = [q['sql'] for q in queries]
        duplicates = {s: sql_list.count(s) for s in set(sql_list) if sql_list.count(s) > 1}
        if duplicates:
            logger.debug(
                '[PROFILE] ⚠ %d duplicate query pattern(s):',
                len(duplicates),
            )
            for sql, count in sorted(duplicates.items(), key=lambda x: -x[1])[:5]:
                logger.debug('  ×%d  %s', count, sql[:120])

        return response
