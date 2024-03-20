from setting import Settings
from pydantic import BaseModel
from typing import Tuple, Dict, Union
from decimal import Decimal
import requests

from typing import Generic, TypeVar

T = TypeVar('T')

class PriceInfo(Generic[T]):
    def __init__(self, value1: T, value2: T):
        self.value1 = value1
        self.value2 = value2

# class TokenOverview(BaseModel):
#     data: Dict[str, Union[float, str]]

class BirdEyeClient:

    def __init__(self) -> None:
        self.config = Settings()
        
    @property
    def _headers(self):
        return {
            "accept": "application/json",
            "x-chain": "solana",
            "X-API-KEY": self.config.BIRD_EYE_TOKEN,
        }
    
    def _make_api_call(self, method: str, query_url: str, *args, **kwargs) -> requests.Response:
        if method.lower() not in ['get', 'post']:
            raise ValueError(f'Unrecognised method "{method}" passed for query - {query_url}')
        
        if method.lower() == 'get':
            response = requests.get(query_url, *args, **kwargs)
        elif method.lower() == 'post':
            response = requests.post(query_url, *args, **kwargs)

        return response
    
    def fetch_prices(self, token_addresses: list[str]) -> dict[str, PriceInfo[Decimal, Decimal]]:
        if not token_addresses:
            raise ValueError("No tokens provided")
        
        token_address_csv = ','.join(token_addresses)
        url = f'https://public-api.birdeye.so/public/multi_price?list_address={token_address_csv}'
        response = self._make_api_call('get', url, headers=self._headers)
        
        if response.status_code != 200:
            raise ValueError(f"Failed to fetch prices for tokens {token_addresses}")
        
        return {
            token: PriceInfo(value1=Decimal(data['value']), value2=Decimal(data['priceChange24h']))
            for token, data in response.json()['data'].items()
        }



    # def fetch_token_overview(self, address: str) -> TokenOverview:
    #     if not address:
    #         raise ValueError("No tokens provided")
        
    #     url = f'https://public-api.birdeye.so/public/multi_price?list_address={address}'
    #     response = self._make_api_call('get', url, headers=self._headers)
        
    #     if response.status_code != 200:
    #         raise ValueError(f"Failed to fetch prices for tokens {address}")
        
    #     return response.json()
    #     # return {
    #     #     token: data
    #     #     for token, data in response.json()['data'].items()
    #     # }