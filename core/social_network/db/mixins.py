from .base import M


class LimitMixin:
    LIMIT_QUERY = 'LIMIT {0} OFFSET {1}'

    @staticmethod
    def validate_limit(limit: int, offset: int):
        for param in (limit, offset):
            if not isinstance(param, int) or param < 0:
                raise ValueError(f'Invalid values: {limit}, {offset}')

    def add_limit(self, query: str, limit: int = 100, offset: int = 0) -> str:
        self.validate_limit(limit, offset)
        return '\n'.join((query, self.LIMIT_QUERY.format(limit, offset)))


class OrderMixin:
    model: M
    order = ('ASC', 'DESC')

    ORDER_QUERY = 'ORDER BY {0} {1}'

    def validate_order(self, field: str, order: str):
        if field not in self.model._fields or order not in self.order:
            raise ValueError(f'Invalid values: {field}, {order}')

    def add_order(self, query: str, field: str, order='ASC') -> str:
        self.validate_order(field, order)
        return '\n'.join((query, self.ORDER_QUERY.format(field, order)))
