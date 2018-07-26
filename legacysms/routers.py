import legacysms


class StatsSchemaRouter:
    """
    This is a database router that routes queries for stats schema tables.
    """

    def db_for_read(self, model, **hints):
        """
        The only stats schema table defined is MediaStatsByDay,
        so route queries on this to the stats DB.
        """
        if legacysms.models.MediaStatsByDay == model:
            return 'stats'

        return 'default'
