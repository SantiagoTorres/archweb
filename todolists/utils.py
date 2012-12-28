from django.db import connections, router
from django.db.models import Count

from .models import Todolist, TodolistPackage


def todo_counts():
    sql = """
SELECT todolist_id, count(*), sum(CASE WHEN status = %s THEN 1 ELSE 0 END)
    FROM todolists_todolistpackage
    GROUP BY todolist_id
    """
    database = router.db_for_write(TodolistPackage)
    connection = connections[database]
    cursor = connection.cursor()
    cursor.execute(sql, [TodolistPackage.COMPLETE])
    results = cursor.fetchall()
    return {row[0]: (row[1], row[2]) for row in results}


def get_annotated_todolists(incomplete_only=False):
    lists = Todolist.objects.all().select_related(
            'creator').order_by('-created')
    lookup = todo_counts()

    # tag each list with package counts
    for todolist in lists:
        counts = lookup.get(todolist.id, (0, 0))
        todolist.pkg_count = counts[0]
        todolist.complete_count = counts[1]
        todolist.incomplete_count = counts[0] - counts[1]

    if incomplete_only:
        lists = [l for l in lists if l.incomplete_count > 0]

    return lists

# vim: set ts=4 sw=4 et:
