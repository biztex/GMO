from abc import ABC, abstractmethod

class BrokerBase(ABC):
    @abstractmethod
    async def login(self): pass

    @abstractmethod
    async def fetch_rate(self): pass

    @abstractmethod
    async def place_order(self, order_data: dict): pass

    @abstractmethod
    async def fetch_execution(self, order_id: str): pass

    @abstractmethod
    async def get_positions(self): pass

    @abstractmethod
    async def close_order(self, position_id: str): pass

    @abstractmethod
    async def close(self): pass
